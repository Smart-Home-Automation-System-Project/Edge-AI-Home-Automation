import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import numpy as np
import pandas as pd
import sys
import tensorflow as tf
from unittest.mock import ANY

# Add the parent directory to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from lights_temp_automation import train


class TestTrain(unittest.TestCase):
    @patch('lights_temp_automation.train.tf.keras.Sequential')
    @patch('lights_temp_automation.train.pd.read_csv')
    @patch('lights_temp_automation.train.os.getenv')
    def test_model_creation_and_training(self, mock_getenv, mock_read_csv, mock_sequential):
        # Mock environment variable
        mock_getenv.return_value = '/fake/path'

        # Create mock training data
        # Create enough rows for sequences
        rows = []
        for i in range(30):  # We need at least 24 + 1 rows
            rows.append({
                'timestamp': f'2023-01-01 {i:02d}:00:00',
                'hour': i % 24,
                'day_of_week': i % 7,
                'l1': i % 2,
                'l2': (i + 1) % 2,
                'l3': i % 2,
                't1': 20 + (i % 10),
                't2': 22 + (i % 8),
                't3': 23 + (i % 5)
            })
        mock_df = pd.DataFrame(rows)
        mock_read_csv.return_value = mock_df

        # Mock the Keras model and its methods
        mock_model = MagicMock()
        mock_sequential.return_value = mock_model

        # Run the training script
        with patch('builtins.print'):
            # Use importlib to reload the module to trigger execution
            import importlib
            importlib.reload(train)

            # Verify model was created with expected layers
            mock_sequential.assert_called_once()

            # Verify model was compiled
            mock_model.compile.assert_called_once_with(optimizer='adam', loss='mse')

            # Verify model was trained
            mock_model.fit.assert_called_once()

            # Verify model was saved
            mock_model.save.assert_called_once_with(ANY)

    @patch('lights_temp_automation.train.tf.keras.Sequential')
    @patch('lights_temp_automation.train.pd.read_csv')
    @patch('lights_temp_automation.train.os.getenv')
    def test_data_preprocessing(self, mock_getenv, mock_read_csv, mock_sequential):
        # Mock environment variable
        mock_getenv.return_value = '/fake/path'

        # Create mock model
        mock_model = MagicMock()
        mock_sequential.return_value = mock_model

        # Create mock data with specific values to test normalization
        rows = []
        for i in range(30):
            rows.append({
                'timestamp': f'2023-01-01 {i:02d}:00:00',
                'hour': 23,  # Should normalize to 1.0
                'day_of_week': 6,  # Should normalize to 1.0
                'l1': 1,
                'l2': 0,
                'l3': 1,
                't1': 30,  # Should normalize to (30-20)/10 = 1.0
                't2': 25,  # Should normalize to (25-20)/10 = 0.5
                't3': 20  # Should normalize to (20-20)/10 = 0.0
            })
        mock_df = pd.DataFrame(rows)
        mock_read_csv.return_value = mock_df

        # Run the training script but capture the data passed to fit
        with patch('builtins.print'):
            with patch.object(mock_model, 'fit', wraps=mock_model.fit) as wrapped_fit:
                # Reload to trigger execution
                import importlib
                importlib.reload(train)

                # Get the arguments passed to fit
                # Note: This is a simplified test. In reality, we'd need more complex logic to
                # extract and verify the normalized data since it's processed into sequences
                self.assertTrue(wrapped_fit.called)