# tests/database/test_export_train_csv.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestExportTrainCsv(unittest.TestCase):

    @patch('os.getenv')
    @patch('sqlite3.connect')
    @patch('pandas.read_sql_query')
    @patch('pandas.DataFrame.to_csv')
    def test_export_train_csv(self, mock_to_csv, mock_read_sql, mock_connect, mock_getenv):
        """Test that export_train_csv correctly exports data"""
        # Mock environment variables
        mock_getenv.return_value = "/fake/project/path"

        # Mock connection
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Create mock DataFrame for pandas.read_sql_query
        test_data = []
        now = datetime.now()

        # Create sample data for past 7 days
        for day in range(7):
            for hour in range(24):
                timestamp = (now - timedelta(days=day, hours=hour)).strftime('%Y-%m-%d %H:%M:%S')

                # Add 6 sensors for each timestamp
                for sensor_id in ['101', '102', '103', '104', '105', '106']:
                    value = 1 if sensor_id in ['101', '102', '103'] else 25.0
                    test_data.append({
                        'sensor_id': sensor_id,
                        'timestamp': timestamp,
                        'sensor_value': value
                    })

        mock_df = pd.DataFrame(test_data)
        mock_read_sql.return_value = mock_df

        # Import the module to test - this will run the entire script
        import database.export_train_csv

        # Verify connection and query
        mock_connect.assert_called_once_with("database1.db")
        mock_read_sql.assert_called_once()

        # Verify CSV was written with correct columns
        mock_to_csv.assert_called_once()
        args, kwargs = mock_to_csv.call_args
        self.assertFalse(kwargs['index'])
        self.assertEqual(kwargs['float_format'], '%.2f')


if __name__ == "__main__":
    unittest.main()