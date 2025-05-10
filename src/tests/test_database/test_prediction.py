import sqlite3
import uuid
from datetime import datetime, timedelta

from test_base import DatabaseTestBase
from src.database import database

class TestDatabasePrediction(DatabaseTestBase):
    """Tests for prediction-related database functions."""

    def setUp(self):
        """Set up test database with sample sensors and data."""
        super().setUp()
        
        # Add some test sensors
        self.light_sensor_id = database.db_add_sensor("light1", "Living Room Light", "light", self.test_db_path)
        self.temp_sensor_id = database.db_add_sensor("temp1", "Living Room Temp", "temp", self.test_db_path)
        
        # Add some test data
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        database.db_add_sensor_data(timestamp, self.light_sensor_id, 1, self.test_db_path)
        database.db_add_sensor_data(timestamp, self.temp_sensor_id, 22.5, self.test_db_path)

    def test_db_get_sensor_data_for_prediction(self):
        """Test retrieving sensor data for prediction."""
        # Use recent dates that will be within the date range
        # Get current date and create timestamps for the past few hours
        now = datetime.now()
        
        # Add more data points for recent timestamps
        for hour in range(1, 5):
            # Create timestamp for 'hour' hours ago
            past_time = now - timedelta(hours=hour)
            timestamp = past_time.strftime('%Y-%m-%d %H:%M:%S')
            
            database.db_add_sensor_data(timestamp, self.light_sensor_id, hour % 2, self.test_db_path)
            database.db_add_sensor_data(timestamp, self.temp_sensor_id, 20 + hour, self.test_db_path)
        
        # Get data for prediction (last day)
        df = database.db_get_sensor_data_for_prediction(days=1, db_name=self.test_db_path)
        
        # Check if DataFrame contains expected columns
        self.assertIn('Living Room Light', df.columns)
        self.assertIn('Living Room Temp', df.columns)
        self.assertIn('hour', df.columns)
        self.assertIn('day_of_week', df.columns)
        
        # Check if DataFrame has the expected number of rows
        # We should have at least 5 rows (1 from setUp + 4 we just added)
        self.assertGreaterEqual(len(df), 5)

    def test_db_save_predictions(self):
        """Test saving predictions to the database."""
        # Create prediction dictionary
        predictions = {
            'lights': {'Living Room Light': 1},
            'temperatures': {'Living Room Temp': 23.5}
        }
        
        # Save predictions
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        database.db_save_predictions(timestamp, predictions, self.test_db_path)
        
        # Verify predictions were saved
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM predictions")
            count = cursor.fetchone()[0]
        
        self.assertEqual(count, 2)  # One for light, one for temp
        
        # Test getting latest predictions
        latest = database.db_get_latest_predictions(self.test_db_path)
        self.assertIsNotNone(latest)
        self.assertEqual(latest['lights']['Living Room Light'], 1)
        self.assertEqual(latest['temperatures']['Living Room Temp'], 23.5)

    def test_db_get_light_and_temp_sensors(self):
        """Test retrieving light and temperature sensors."""
        light_sensors, temp_sensors = database.db_get_light_and_temp_sensors(self.test_db_path)
        
        self.assertEqual(len(light_sensors), 1)
        self.assertEqual(len(temp_sensors), 1)
        self.assertEqual(light_sensors[0], "Living Room Light")
        self.assertEqual(temp_sensors[0], "Living Room Temp")

if __name__ == '__main__':
    unittest.main()
