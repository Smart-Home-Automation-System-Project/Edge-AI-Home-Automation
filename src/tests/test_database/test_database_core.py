import unittest
import sqlite3
import uuid
from datetime import datetime

from test_base import DatabaseTestBase
from src.database import database

class TestDatabaseCore(DatabaseTestBase):
    """Core database functionality tests."""

    def test_db_add_and_get_module(self):
        """Test adding and retrieving a module."""
        database.db_add_module("client1", "Sensor 1", "light", self.test_db_path)
        modules = database.db_get_available_all_modules(self.test_db_path)
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0]['client_id'], "client1")

    def test_db_assign_module(self):
        """Test assigning a name to a module."""
        sensor_id = str(uuid.uuid4())
        with sqlite3.connect(self.test_db_path) as conn:
            conn.execute("INSERT INTO sensors VALUES (?, ?, ?, ?, ?)", (sensor_id, "client2", None, "light", None))
        database.db_assign_module("client2", "Assigned Sensor", self.test_db_path)
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sensors WHERE client_id = 'client2'")
            result = cursor.fetchone()[0]
        self.assertEqual(result, "Assigned Sensor")

    def test_db_add_sensor_data(self):
        """Test adding sensor data."""
        # First add a sensor
        sensor_id = database.db_add_module("temp_client", "Temp Sensor", "temp", self.test_db_path)
        
        # Now add data for this sensor
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        database.db_add_sensor_data(timestamp, sensor_id, 25.5, self.test_db_path)
        
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sensor_value FROM sensor_data WHERE sensor_id = ? AND timestamp = ?", (sensor_id, timestamp))
            result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 25.5)

    def test_db_get_id_and_client_id(self):
        """Test retrieving ID and client ID."""
        # First add a sensor with a client_id
        database.db_add_module("client3", "ID Test Sensor", "switch", self.test_db_path)
        
        # Get the ID using the client_id
        id_fetched = database.db_get_id("client3", self.test_db_path)
        
        # Get the client_id using the name
        client_id = database.db_get_client_id("ID Test Sensor", self.test_db_path)
        
        self.assertIsNotNone(id_fetched)
        self.assertEqual(client_id, "client3")

    def test_db_get_and_replace_module(self):
        """Test replacing a module."""
        old_id = str(uuid.uuid4())
        placeholder_id = str(uuid.uuid4())
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sensors VALUES (?, ?, ?, ?, ?)", (old_id, "replace_client", "Sensor", "light", None))
            cursor.execute("INSERT INTO sensors VALUES (?, ?, ?, ?, ?)", (placeholder_id, "new_client", None, "light", None))
        rows_affected = database.db_replace_module(old_id, "new_client", self.test_db_path)
        self.assertGreaterEqual(rows_affected, 1)

    def test_db_delete_module(self):
        """Test deleting a module."""
        sensor_id = str(uuid.uuid4())
        with sqlite3.connect(self.test_db_path) as conn:
            conn.execute("INSERT INTO sensors VALUES (?, ?, ?, ?, ?)", (sensor_id, "del_client", "ToDelete", "light", None))
        affected = database.db_delete_module(sensor_id, self.test_db_path)
        self.assertEqual(affected, 1)

    def test_db_get_sensor_data(self):
        """Test retrieving sensor data."""
        sensor_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sensors VALUES (?, ?, ?, ?, ?)", (sensor_id, "client9", "Temp Sensor", "temp", None))
            cursor.execute("INSERT INTO sensor_data VALUES (?, ?, ?)", (sensor_id, timestamp, 22.0))
        result = database.db_get_sensor_data(sensor_id, 7, self.test_db_path)
        self.assertGreaterEqual(len(result), 1)

if __name__ == '__main__':
    unittest.main()