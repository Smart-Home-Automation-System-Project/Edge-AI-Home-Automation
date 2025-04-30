# tests/database/test_db_setup.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import sqlite3

# Add parent directory to sys.path to allow importing from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestDbSetup(unittest.TestCase):

    # replaces sqlite3.connect with a mock object for the duration of the test
    @patch('sqlite3.connect')
    def test_db_setup(self, mock_connect):
        """Test that database setup creates the correct table"""
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Import the module (this should trigger the DB setup code)
        import database.db_setup

        # Check if connect was called with correct database name
        mock_connect.assert_called_once_with("database1.db")

        # Check if correct SQL CREATE TABLE statement was executed
        mock_cursor.execute.assert_called_once()
        create_table_sql = mock_cursor.execute.call_args[0][0]
        self.assertIn("CREATE TABLE IF NOT EXISTS sensor_data", create_table_sql)
        self.assertIn("sensor_id TEXT", create_table_sql)
        self.assertIn("timestamp TEXT", create_table_sql)
        self.assertIn("sensor_value REAL", create_table_sql)
        self.assertIn("PRIMARY KEY", create_table_sql)

        # Check commit and close
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == "__main__":
    # Allow running directly from PyCharm or command line without argument issues
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
