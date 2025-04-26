# tests/database/test_export_test_csv.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.export_test_csv import get_latest_data_from_db, save_to_csv


class TestExportTestCsv(unittest.TestCase):

    @patch('sqlite3.connect')
    @patch('pandas.read_sql_query')
    def test_get_latest_data_from_db_with_data(self, mock_read_sql, mock_connect):
        """Test that getting latest data from DB works with available data"""
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Set up cursor.fetchone to return a timestamp
        mock_cursor.fetchone.return_value = ["2025-03-28 15:30:00"]

        # Create mock DataFrame for pandas.read_sql_query
        mock_df = pd.DataFrame({
            'sensor_id': ['101', '102', '103', '104', '105', '106'],
            'timestamp': ['2025-03-28 15:30:00'] * 6,
            'sensor_value': [1, 0, 1, 25.5, 27.3, 22.1]
        })
        mock_read_sql.return_value = mock_df

        # Call the function
        result = get_latest_data_from_db()

        # Verify SQL queries were executed
        mock_cursor.execute.assert_called_once_with('SELECT MAX(timestamp) FROM sensor_data')
        mock_read_sql.assert_called_once()

        # Check result DataFrame shape and content
        self.assertIsNotNone(result)
        self.assertIn('timestamp', result.columns)
        self.assertIn('l1', result.columns)
        self.assertIn('l2', result.columns)
        self.assertIn('l3', result.columns)
        self.assertIn('t1', result.columns)
        self.assertIn('t2', result.columns)
        self.assertIn('t3', result.columns)
        self.assertIn('day_of_week', result.columns)
        self.assertIn('hour', result.columns)

    @patch('sqlite3.connect')
    def test_get_latest_data_from_db_no_data(self, mock_connect):
        """Test that getting latest data from DB handles no data case"""
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Set up cursor.fetchone to return None (no data)
        mock_cursor.fetchone.return_value = [None]

        # Call the function
        result = get_latest_data_from_db()

        # Verify SQL query was executed
        mock_cursor.execute.assert_called_once_with('SELECT MAX(timestamp) FROM sensor_data')

        # Check result is None
        self.assertIsNone(result)

    @patch('pandas.DataFrame.to_csv')
    def test_save_to_csv(self, mock_to_csv):
        """Test that data is saved to CSV correctly"""
        # Create mock DataFrame
        df = pd.DataFrame({
            'timestamp': ['2025-03-28 15:30:00'],
            'day_of_week': [4],
            'hour': [15],
            'l1': [1],
            'l2': [0],
            'l3': [1],
            't1': [25.5],
            't2': [27.3],
            't3': [22.1]
        })

        # Call function
        save_to_csv(df)

        # Verify to_csv was called with correct parameters
        mock_to_csv.assert_called_once()
        args, kwargs = mock_to_csv.call_args
        self.assertFalse(kwargs['index'])
        self.assertEqual(kwargs['float_format'], '%.2f')


if __name__ == "__main__":
    unittest.main()