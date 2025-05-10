import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import sqlite3

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.delete_tables import clear_sensor_data_table

class TestDeleteTables(unittest.TestCase):

    @patch('sqlite3.connect')
    @patch('builtins.print')
    def test_clear_sensor_data_table_success(self, mock_print, mock_connect):
        """Test successful deletion of data from sensor_data table."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db_name = "test_db.db"
        clear_sensor_data_table(db_name=db_name)

        mock_connect.assert_called_once_with(db_name)
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("DELETE FROM sensor_data")
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        mock_print.assert_called_with(f"All data deleted from 'sensor_data' table in {db_name}.")

    @patch('sqlite3.connect')
    @patch('builtins.print')
    def test_clear_sensor_data_table_success_default_db(self, mock_print, mock_connect):
        """Test successful deletion with default database name."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        clear_sensor_data_table() # Use default db_name

        mock_connect.assert_called_once_with("database1.db") # Default name
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("DELETE FROM sensor_data")
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        mock_print.assert_called_with("All data deleted from 'sensor_data' table in database1.db.")

    @patch('sqlite3.connect')
    @patch('builtins.print')
    def test_clear_sensor_data_table_sqlite_error(self, mock_print, mock_connect):
        """Test handling of sqlite3.Error during database operation."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        # Simulate an error during execute
        mock_conn.cursor.side_effect = sqlite3.Error("Test SQLite error")

        db_name = "error_db.db"
        clear_sensor_data_table(db_name=db_name)

        mock_connect.assert_called_once_with(db_name)
        mock_conn.cursor.assert_called_once() # Attempted to get cursor
        # Execute, commit might not be called if cursor creation fails or execute fails early
        # We are testing the error message and that close is still called
        mock_print.assert_called_with("An error occurred: Test SQLite error")
        mock_conn.close.assert_called_once() # Should be called in finally block

    @patch('sqlite3.connect')
    @patch('builtins.print')
    def test_clear_sensor_data_table_sqlite_error_on_commit(self, mock_print, mock_connect):
        """Test handling of sqlite3.Error during commit."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.commit.side_effect = sqlite3.Error("Test commit error")

        db_name = "commit_error_db.db"
        clear_sensor_data_table(db_name=db_name)

        mock_connect.assert_called_once_with(db_name)
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("DELETE FROM sensor_data")
        mock_conn.commit.assert_called_once() # Commit was attempted
        mock_print.assert_called_with("An error occurred: Test commit error")
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()