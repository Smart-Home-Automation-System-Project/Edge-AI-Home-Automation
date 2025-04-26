import unittest
from unittest.mock import patch, MagicMock, mock_open, ANY
import os
import numpy as np
import pandas as pd
import sys
import tensorflow as tf

# Add the parent directory to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from lights_temp_automation import predict


class TestPredict(unittest.TestCase):
    @patch('lights_temp_automation.predict.keras.models.load_model')
    @patch('lights_temp_automation.predict.pd.read_csv')
    @patch('lights_temp_automation.predict.pd.DataFrame.to_csv')
    @patch('lights_temp_automation.predict.os.getenv')
    def test_prediction_flow(self, mock_getenv, mock_to_csv, mock_read_csv, mock_load_model):
        # Mock environment variable
        mock_getenv.return_value = '/fake/path'

        # Create a mock model that returns predictable outputs
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([
            [0.9, 0.1, 0.8, 0.5, 0.6, 0.7]  # [l1, l2, l3, t1, t2, t3]
        ])
        mock_load_model.return_value = mock_model

        # Create mock input data
        mock_df = pd.DataFrame({
            'timestamp': ['2023-01-01 12:00:00'],
            'hour': [12],
            'day_of_week': [3],
            'l1': [1], 'l2': [0], 'l3': [1],
            't1': [22.5], 't2': [23.0], 't3': [21.5]
        })
        mock_read_csv.return_value = mock_df

        # Run the prediction script (mocked)
        with patch('builtins.print') as mock_print:
            # Use importlib to reload the module to trigger execution
            import importlib
            importlib.reload(predict)

            # Check that model was loaded
            mock_load_model.assert_called_once_with(ANY, compile=False)

            # Check that predictions were made
            self.assertTrue(mock_model.predict.called)

            # Check that results were saved
            mock_to_csv.assert_called_once()


if __name__ == '__main__':
    unittest.main()
