import unittest
import sqlite3
import os
import tempfile
import sys

# Add the absolute path to 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import the module to test
from src.database import delete_tables

class TestDeleteTables(unittest.TestCase):
    """Tests for table deletion functionality."""

    def setUp(self):
        """Create a temporary database file with test data."""
        self.test_db_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_db_path = self.test_db_file.name
        self.test_db_file.close()
        
        # Create database and add test data
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            sensor_id TEXT,
            timestamp TEXT,
            sensor_value REAL,
            PRIMARY KEY (sensor_id, timestamp)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id TEXT,
            client_id TEXT,
            name TEXT,
            category TEXT,
            last_val TEXT,
            PRIMARY KEY (id, client_id)
        )
        """)
        
        # Insert test data
        cursor.execute("""
        INSERT INTO sensors (id, client_id, name, category, last_val)
        VALUES (?, ?, ?, ?, ?)
        """, ("sensor1", "client1", "Sensor 1", "temp", "22.5"))
        
        cursor.execute("""
        INSERT INTO sensor_data (sensor_id, timestamp, sensor_value)
        VALUES (?, ?, ?)
        """, ("sensor1", "2023-01-01 00:00:00", 22.5))
        
        conn.commit()
        conn.close()

    def tearDown(self):
        """Clean up the temporary database file."""
        try:
            os.remove(self.test_db_path)
        except:
            pass

    def test_clear_sensor_data_table(self):
        """Test clearing the sensor_data table."""
        # Verify data exists before clearing
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensor_data")
        count_before = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count_before, 1)
        
        # Clear the table
        delete_tables.clear_sensor_data_table(self.test_db_path)
        
        # Verify data was cleared
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensor_data")
        count_after = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count_after, 0)
        
        # Verify sensors table was not affected
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensors")
        sensors_count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(sensors_count, 1)

    def test_clear_sensors_table(self):
        """Test clearing the sensors table."""
        # Verify data exists before clearing
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensors")
        count_before = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count_before, 1)
        
        # Clear the table
        delete_tables.clear_sensors_table(self.test_db_path)
        
        # Verify data was cleared
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensors")
        count_after = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count_after, 0)
        
        # Verify sensor_data table was not affected
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensor_data")
        sensor_data_count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(sensor_data_count, 1)

    def test_clear_both_tables(self):
        """Test clearing both tables."""
        # Clear both tables
        delete_tables.clear_sensor_data_table(self.test_db_path)
        delete_tables.clear_sensors_table(self.test_db_path)
        
        # Verify both tables are empty
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM sensor_data")
        sensor_data_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sensors")
        sensors_count = cursor.fetchone()[0]
        
        conn.close()
        
        self.assertEqual(sensor_data_count, 0)
        self.assertEqual(sensors_count, 0)

if __name__ == '__main__':
    unittest.main()