import os
import sqlite3
import tempfile

from test_base import DatabaseTestBase
from src.database import database

class TestDatabaseInitialization(DatabaseTestBase):
    """Tests for database initialization and empty database handling."""

    def test_db_empty_database(self):
        """Test functions with an empty database."""
        # Create a new empty database
        empty_db = tempfile.NamedTemporaryFile(delete=False).name

        try:
            # Create tables but don't add any data
            with sqlite3.connect(empty_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE sensors (
                        id TEXT PRIMARY KEY,
                        client_id TEXT UNIQUE,
                        name TEXT,
                        category TEXT,
                        last_val TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE sensor_data (
                        sensor_id TEXT,
                        timestamp TEXT,
                        sensor_value REAL,
                        PRIMARY KEY(sensor_id, timestamp)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE predictions (
                        timestamp TEXT,
                        sensor_name TEXT,
                        predicted_value REAL,
                        category TEXT
                    )
                """)
                conn.commit()
            
            # Test functions with empty database
            modules = database.db_get_available_all_modules(empty_db)
            self.assertEqual(len(modules), 0)
            
            light_sensors, temp_sensors = database.db_get_light_and_temp_sensors(empty_db)
            self.assertEqual(len(light_sensors), 0)
            self.assertEqual(len(temp_sensors), 0)
            
            predictions = database.db_get_latest_predictions(empty_db)
            self.assertIsNone(predictions)
        finally:
            # Clean up
            try:
                os.remove(empty_db)
            except:
                pass

    def test_db_create_last_val_trigger(self):
        """Test creating the last_val trigger."""
        # Create the trigger
        database.db_create_last_val_trigger(self.test_db_path)
        
        # Add a sensor
        sensor_id = database.db_add_sensor("trigger_test", "Trigger Test", "temp", self.test_db_path)
        
        # Add data for the sensor
        database.db_add_sensor_data("2023-01-01 00:00:00", sensor_id, 22.5, self.test_db_path)
        
        # Check if last_val was updated
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_val FROM sensors WHERE id = ?", (sensor_id,))
            last_val = cursor.fetchone()[0]
        
        self.assertEqual(float(last_val), 22.5)

if __name__ == '__main__':
    unittest.main()