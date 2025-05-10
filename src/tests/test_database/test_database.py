import unittest
import os
import sqlite3
import sys

# Add the absolute path to 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from src.database.database import db_add_sensor

TEST_DB = "test_database.db"

class TestDatabase(unittest.TestCase):
    def setUp(self):
        conn = sqlite3.connect(TEST_DB)
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
        conn.commit()
        conn.close()

    def tearDown(self):
        try:
            os.remove(TEST_DB)
        except PermissionError:
            # Ensure the connection is closed before trying again
            import gc
            gc.collect()  # force garbage collection (to close file handles)
            os.remove(TEST_DB)

    def test_db_add_sensor(self):
        db_add_sensor("X-0001", "Test Sensor", "test_cat", db_name=TEST_DB)
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensors WHERE client_id='X-0001'")
        result = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(result)
