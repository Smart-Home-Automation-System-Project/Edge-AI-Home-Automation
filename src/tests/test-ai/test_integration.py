import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd
import os
import sys
import datetime
import tensorflow as tf

# Add the parent directory to sys.path to import the modules
# Update path to account for new location in tests/test-ai/
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the modules to test
from ai.predict import ai_predict, load_model
from ai.train import main as train_main
from ai.ai import run_predictions_and_publish


class TestAiIntegration(unittest.TestCase):
    
    def setUp(self):
        # Create a small test model
        self.test_model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(24, 4)),
            tf.keras.layers.LSTM(4, return_sequences=False),
            tf.keras.layers.Dense(4)
        ])
    
    @patch('ai.predict.db_get_sensor_data_for_prediction')
    @patch('ai.predict.db_get_light_and_temp_sensors')
    def test_predict_integration(self, mock_get_sensors, mock_get_data):
        """Test the full prediction pipeline with a real model."""
        # Setup test data
        test_timestamp = datetime.datetime(2025, 5, 1, 12, 0)
        test_df = pd.DataFrame({
            'timestamp': [test_timestamp - datetime.timedelta(hours=i) for i in range(24)],
            'light_sensor1': [2] * 24,
            'temp_sensor1': [22.5] * 24,
            'hour': list(range(12, 12-24, -1)) + [0],  # Handle wrap-around
            'day_of_week': [3] * 24  # Wednesday
        })
        
        mock_get_data.return_value = test_df
        mock_get_sensors.return_value = (['light_sensor1'], ['temp_sensor1'])
        
        # Mock model prediction to return a known value
        self.test_model.predict = MagicMock(return_value=np.array([[2.5, 0.5, 22.7, 23.1]]))
        
        # Execute prediction
        results = ai_predict(self.test_model)
        
        # Assert
        self.assertIsNotNone(results)
        self.assertIn('lights', results)
        self.assertIn('temperatures', results)
        self.assertEqual(len(results['lights']), 1)
        self.assertEqual(len(results['temperatures']), 1)
    
    @patch('ai.ai.ai_predict')
    def test_run_predictions_and_publish_integration(self, mock_predict):
        """Test the prediction and publishing integration."""
        # Setup
        mock_model = MagicMock()
        mock_client = MagicMock()
        
        # Mock ai_predict to return realistic results
        mock_results = {
            'lights': {'living_room': 2, 'kitchen': 1},
            'temperatures': {'living_room_temp': 22.8, 'kitchen_temp': 21.5}
        }
        mock_predict.return_value = mock_results
        
        # Execute
        run_predictions_and_publish(mock_model, mock_client)
        
        # Assert
        mock_predict.assert_called_once_with(mock_model)
        self.assertTrue(mock_client.publish.called)
    
    @patch('ai.train.db_get_all_sensor_data')
    @patch('ai.train.create_lstm_model')
    @patch('ai.train.save_model')
    def test_train_to_predict_workflow(self, mock_save, mock_create_model, mock_get_data):
        """Test the end-to-end workflow from training to prediction."""
        # Setup - mock database data
        mock_sensor_data = {
            'light_sensor1': {
                'category': 'light',
                'data': [(pd.Timestamp('2025-05-01 12:00:00'), 2) for _ in range(50)]
            },
            'temp_sensor1': {
                'category': 'temp',
                'data': [(pd.Timestamp('2025-05-01 12:00:00'), 22.5) for _ in range(50)]
            }
        }
        mock_get_data.return_value = mock_sensor_data
        
        # Mock model creation to return our test model
        mock_create_model.return_value = self.test_model
        
        # Execute training
        train_main()
        
        # Assert
        mock_save.assert_called_once()
        
        # Now simulate loading this model for prediction
        with patch('ai.predict.keras.models.load_model', return_value=self.test_model):
            with patch('ai.predict.db_get_sensor_data_for_prediction') as mock_get_pred_data:
                with patch('ai.predict.db_get_light_and_temp_sensors') as mock_get_pred_sensors:
                    # Setup test data for prediction
                    test_df = pd.DataFrame({
                        'timestamp': [datetime.datetime.now() - datetime.timedelta(hours=i) for i in range(24)],
                        'light_sensor1': [2] * 24,
                        'temp_sensor1': [22.5] * 24,
                        'hour': list(range(12, 12-24, -1)),
                        'day_of_week': [3] * 24  # Wednesday
                    })
                    
                    mock_get_pred_data.return_value = test_df
                    mock_get_pred_sensors.return_value = (['light_sensor1'], ['temp_sensor1'])
                    
                    # Mock model prediction
                    self.test_model.predict = MagicMock(return_value=np.array([[2.0, 22.5]]))
                    
                    # Execute prediction with the "trained" model
                    model_path = "dummy_path.h5"
                    with patch('os.path.isfile', return_value=True):
                        model = load_model(model_path)
                        results = ai_predict(model)
                    
                    # Assert predictions work
                    self.assertIsNotNone(results)
                    self.assertIn('lights', results)
                    self.assertIn('temperatures', results)


if __name__ == '__main__':
    unittest.main()