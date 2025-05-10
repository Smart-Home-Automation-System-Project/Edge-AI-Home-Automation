import unittest
import sqlite3
import os
import sys
import tempfile
import importlib.util
from unittest.mock import patch

# Add the parent directory to the path so we can import modules from the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class TestDatabaseSetup(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary file for the test database"""
        # Create a temporary file that will be automatically deleted
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        
        # Close the file descriptor immediately to avoid file locking issues
        os.close(self.temp_db_fd)
        
        # Store the original database path to restore it later
        self.original_db_path = os.path.join(os.path.dirname(os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../../database/db_setup.py'))), 'database.db')
    
    def tearDown(self):
        """Clean up after each test"""
        # Remove the temporary database file
        try:
            os.unlink(self.temp_db_path)
        except:
            pass
    
    def _run_db_setup_with_mock_path(self):
        """Run the db_setup.py script with a mocked path to use our temporary database"""
        # Get the path to the original db_setup.py file
        db_setup_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../../database/db_setup.py'))
        
        # Load the module spec
        spec = importlib.util.spec_from_file_location("db_setup", db_setup_path)
        db_setup = importlib.util.module_from_spec(spec)
        
        # Mock os.path.join to return our temporary database path
        def mock_join(*args):
            if args[-1] == 'database.db':
                return self.temp_db_path
            return os.path.join(*args)
        
        # Execute the module with the mocked path
        with patch('os.path.join', side_effect=mock_join):
            spec.loader.exec_module(db_setup)
    
    def test_database_creation(self):
        """Test that the database file is created"""
        # Run the database setup with our mocked path
        self._run_db_setup_with_mock_path()
        
        # Check that the database file exists
        self.assertTrue(os.path.exists(self.temp_db_path))
        
        # Verify we can connect to it
        conn = sqlite3.connect(self.temp_db_path)
        conn.close()
    
    def test_table_structure(self):
        """Test that the tables are created with the correct structure"""
        # Run the database setup with our mocked path
        self._run_db_setup_with_mock_path()
        
        # Connect to the database
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        
        # Check that the sensor_data table exists and has the correct schema
        cursor.execute("PRAGMA table_info(sensor_data)")
        columns = cursor.fetchall()
        
        # Check column names and types
        self.assertEqual(len(columns), 3)
        self.assertEqual(columns[0][1], 'sensor_id')
        self.assertEqual(columns[0][2], 'TEXT')
        self.assertEqual(columns[1][1], 'timestamp')
        self.assertEqual(columns[1][2], 'TEXT')
        self.assertEqual(columns[2][1], 'sensor_value')
        self.assertEqual(columns[2][2], 'REAL')
        
        # Check that the sensors table exists and has the correct schema
        cursor.execute("PRAGMA table_info(sensors)")
        columns = cursor.fetchall()
        
        # Check column names and types
        self.assertEqual(len(columns), 5)
        self.assertEqual(columns[0][1], 'id')
        self.assertEqual(columns[0][2], 'TEXT')
        self.assertEqual(columns[1][1], 'client_id')
        self.assertEqual(columns[1][2], 'TEXT')
        self.assertEqual(columns[2][1], 'name')
        self.assertEqual(columns[2][2], 'TEXT')
        self.assertEqual(columns[3][1], 'category')
        self.assertEqual(columns[3][2], 'TEXT')
        self.assertEqual(columns[4][1], 'last_val')
        self.assertEqual(columns[4][2], 'TEXT')
        
        # Check that the trigger exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name='update_last_val'")
        trigger = cursor.fetchone()
        self.assertIsNotNone(trigger)
        
        conn.close()
    
    def test_trigger_functionality(self):
        """Test that the trigger updates the last_val field in the sensors table"""
        # Run the database setup with our mocked path
        self._run_db_setup_with_mock_path()
        
        # Connect to the database
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        
        # Insert a test sensor
        cursor.execute("""
        INSERT INTO sensors (id, client_id, name, category, last_val)
        VALUES ('sensor1', 'client1', 'Test Sensor', 'temperature', NULL)
        """)
        
        # Insert a sensor reading
        cursor.execute("""
        INSERT INTO sensor_data (sensor_id, timestamp, sensor_value)
        VALUES ('sensor1', '2023-01-01 12:00:00', 25.5)
        """)
        
        # Check that the last_val field was updated
        cursor.execute("SELECT last_val FROM sensors WHERE id = 'sensor1'")
        last_val = cursor.fetchone()[0]
        self.assertEqual(float(last_val), 25.5)
        
        # Insert another sensor reading
        cursor.execute("""
        INSERT INTO sensor_data (sensor_id, timestamp, sensor_value)
        VALUES ('sensor1', '2023-01-01 12:01:00', 26.7)
        """)
        
        # Check that the last_val field was updated again
        cursor.execute("SELECT last_val FROM sensors WHERE id = 'sensor1'")
        last_val = cursor.fetchone()[0]
        self.assertEqual(float(last_val), 26.7)
        
        conn.commit()
        conn.close()
    
    def test_primary_keys(self):
        """Test that the primary keys are set correctly"""
        # Run the database setup with our mocked path
        self._run_db_setup_with_mock_path()
        
        # Connect to the database
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        
        # Test sensor_data primary key
        # Insert a record
        cursor.execute("""
        INSERT INTO sensor_data (sensor_id, timestamp, sensor_value)
        VALUES ('sensor1', '2023-01-01 12:00:00', 25.5)
        """)
        
        # Try to insert a duplicate (should fail)
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
            INSERT INTO sensor_data (sensor_id, timestamp, sensor_value)
            VALUES ('sensor1', '2023-01-01 12:00:00', 26.7)
            """)
        
        # Test sensors primary key
        # Insert a record
        cursor.execute("""
        INSERT INTO sensors (id, client_id, name, category, last_val)
        VALUES ('sensor2', 'client1', 'Test Sensor 2', 'humidity', NULL)
        """)
        
        # Try to insert a duplicate (should fail)
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
            INSERT INTO sensors (id, client_id, name, category, last_val)
            VALUES ('sensor2', 'client1', 'Duplicate Sensor', 'pressure', NULL)
            """)
        
        conn.commit()
        conn.close()

if __name__ == '__main__':
    unittest.main()
