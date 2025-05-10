import unittest
import sqlite3
import os
import tempfile
import sys
import gc
import time

# Add the absolute path to 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Mock the globals module
class MockGlobals:
    client_id = 'test_client'

sys.modules['src.utils.globals'] = MockGlobals()

from src.database import database

class DatabaseTestBase(unittest.TestCase):
    """Base class for all database tests with common setup and teardown."""
    
    def setUp(self):
        """Set up a temporary test database with required tables."""
        # Use a temporary file for the test database
        self.test_db_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_db_path = self.test_db_file.name
        database.DB_NAME = self.test_db_path
        self.test_db_file.close()

        conn = sqlite3.connect(self.test_db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
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
        conn.close()

    def tearDown(self):
        """Clean up the temporary test database."""
        gc.collect()
        try:
            os.remove(self.test_db_path)
        except PermissionError:
            time.sleep(0.5)
            gc.collect()
            try:
                os.remove(self.test_db_path)
            except:
                print(f"Warning: Could not remove test database file: {self.test_db_path}")