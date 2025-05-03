# tests/database/test_insert_data.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.insert_sample_sensor_data import generate_sample_data, insert_data_for_entire_week


class TestInsertData(unittest.TestCase):

    def test_generate_sample_data(self):
        """Test that sample data is generated with correct format"""
        test_time = datetime.now()
        data_rows = generate_sample_data(test_time)

        # Check we have 6 rows (6 sensors)
        self.assertEqual(len(data_rows), 6)

        # Check format of each row
        for row in data_rows:
            # Each row should be (sensor_id, timestamp, value)
            self.assertEqual(len(row), 3)

            # Check sensor_id format
            self.assertIn(row[0], ['101', '102', '103', '104', '105', '106'])

            # Check timestamp format (should be string)
            self.assertIsInstance(row[1], str)
            self.assertEqual(row[1], test_time.strftime('%Y-%m-%d %H:%M:%S'))

            # Check value types
            self.assertIsInstance(row[2], (int, float))

            # Check value ranges
            if row[0] in ['101', '102', '103']:  # Light sensors
                self.assertIn(row[2], [0, 1])
            else:  # Temperature sensors
                self.assertTrue(12.0 <= row[2] <= 40.0)

    @patch('sqlite3.connect')
    def test_insert_data_for_entire_week(self, mock_connect):
        """Test that data insertion for a week works correctly"""
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Call function with reduced iterations for testing
        with patch('database.insert_data.range', side_effect=[range(1), range(2)]):  # Just 1 day, 2 intervals
            insert_data_for_entire_week()

        # Should have 12 execute calls (1 day * 2 intervals * 6 sensors)
        self.assertEqual(mock_cursor.execute.call_count, 12)

        # Verify commit and close were called
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()