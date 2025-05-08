import unittest
from unittest.mock import patch, MagicMock, mock_open
import numpy as np
import pandas as pd
import datetime
import os
import sys

# Add the parent directory to sys.path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions to test
from ai.predict import (load_model, load_and_preprocess_data, 
                      make_predictions, process_predictions, ai_predict)


class TestPredictFunctions(unittest.TestCase):
    
    @patch('ai.predict.keras.models.load_model')
    def test_load_model(self, mock_load_model):
        # Setup
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        test_path = "test_model.h5"
        
        # Execute
        result = load_model(test_path)
        
        # Assert
        mock_load_model.assert_called_once_with(test_path, compile=False)
        self.assertEqual(result, mock_model)
    
    @patch('ai.predict.keras.models.load_model')
    def test_load_model_exception(self, mock_load_model):
        # Setup
        mock_load_model.side_effect = Exception("Model loading error")
        test_path = "test_model.h5"
        
        # Execute and Assert
        with self.assertRaises(SystemExit):
            load_model(test_path)
    
    @patch('ai.predict.db_get_sensor_data_for_prediction')
    @patch('ai.predict.db_get_light_and_temp_sensors')
    def test_load_and_preprocess_data(self, mock_get_sensors, mock_get_data):
        # Setup
        # Create a mock DataFrame with the required columns
        test_df = pd.DataFrame({
            'timestamp': [datetime.datetime(2025, 5, 1, 12, 0) - datetime.timedelta(hours=i) for i in range(24)],
            'light_sensor1': [2] * 24,
            'light_sensor2': [1] * 24,
            'temp_sensor1': [22.5] * 24,
            'temp_sensor2': [23.0] * 24,
            'hour': list(range(12, 12-24, -1)),
            'day_of_week': [3] * 24  # Wednesday
        })
        
        mock_get_data.return_value = test_df
        mock_get_sensors.return_value = (['light_sensor1', 'light_sensor2'], 
                                          ['temp_sensor1', 'temp_sensor2'])
        
        # Execute
        X, last_timestamp, light_sensors, temp_sensors = load_and_preprocess_data()
        
        # Assert
        self.assertEqual(X.shape, (1, 24, 6))  # 1 sample, 24 timesteps, 6 features
        self.assertEqual(len(light_sensors), 2)
        self.assertEqual(len(temp_sensors), 2)
        self.assertIsInstance(last_timestamp, datetime.datetime)
        
    @patch('ai.predict.db_get_sensor_data_for_prediction')
    @patch('ai.predict.db_get_light_and_temp_sensors')
    def test_load_and_preprocess_data_with_insufficient_data(self, mock_get_sensors, mock_get_data):
        # Setup - only 10 hours of data (less than 24)
        test_df = pd.DataFrame({
            'timestamp': [datetime.datetime(2025, 5, 1, 12, 0) - datetime.timedelta(hours=i) for i in range(10)],
            'light_sensor1': [2] * 10,
            'temp_sensor1': [22.5] * 10,
            'hour': list(range(12, 12-10, -1)),
            'day_of_week': [3] * 10
        })
        
        mock_get_data.return_value = test_df
        mock_get_sensors.return_value = (['light_sensor1'], ['temp_sensor1'])
        
        # Execute
        X, last_timestamp, light_sensors, temp_sensors = load_and_preprocess_data()
        
        # Assert - should pad with zeros to get 24 timesteps
        self.assertEqual(X.shape, (1, 24, 4))  # 1 sample, 24 timesteps, 4 features
        
    @patch('ai.predict.db_get_sensor_data_for_prediction')
    @patch('ai.predict.db_get_light_and_temp_sensors')
    def test_load_and_preprocess_data_exception(self, mock_get_sensors, mock_get_data):
        # Setup
        mock_get_data.side_effect = Exception("Database error")
        
        # Execute and Assert
        with self.assertRaises(SystemExit):
            load_and_preprocess_data()

    def test_make_predictions(self):
        # Setup
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.5, 2.1, 0.25, 0.1]])
        test_input = np.zeros((1, 24, 4))
        
        # Execute
        result = make_predictions(mock_model, test_input)
        
        # Assert
        mock_model.predict.assert_called_once_with(test_input)
        np.testing.assert_array_equal(result, np.array([[0.5, 2.1, 0.25, 0.1]]))
    
    def test_make_predictions_exception(self):
        # Setup
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Prediction error")
        test_input = np.zeros((1, 24, 4))
        
        # Execute and Assert
        with self.assertRaises(SystemExit):
            make_predictions(mock_model, test_input)
    
    def test_process_predictions(self):
        # Setup
        predictions = np.array([[1.2, 2.8, 0.3, 0.4]])  # 2 light values, 2 temp values
        light_sensors = ['living_room', 'bedroom']
        temp_sensors = ['kitchen_temp', 'bedroom_temp']
        
        # Execute
        final_predictions, results = process_predictions(
            predictions, light_sensors, temp_sensors)
        
        # Assert
        self.assertEqual(len(final_predictions), 4)
        self.assertEqual(results['lights']['living_room'], 1)  # 1.2 -> 1
        self.assertEqual(results['lights']['bedroom'], 3)  # 2.8 -> 3 (clipped)
        self.assertIn('kitchen_temp', results['temperatures'])
        self.assertIn('bedroom_temp', results['temperatures'])
        
        # Check temperature values (with adjustment factor applied)
        # Temperature processing includes a random adjustment, so we just check range
        for temp in results['temperatures'].values():
            self.assertTrue(20 <= temp <= 30)  # Normal room temperature range
    
    @patch('ai.predict.load_and_preprocess_data')
    @patch('ai.predict.make_predictions')
    @patch('ai.predict.process_predictions')
    def test_ai_predict(self, mock_process, mock_predict, mock_preprocess):
        # Setup
        mock_model = MagicMock()
        mock_preprocess.return_value = (
            np.zeros((1, 24, 4)),  # X
            datetime.datetime.now(),  # timestamp
            ['light1', 'light2'],  # light sensors
            ['temp1', 'temp2']  # temp sensors
        )
        mock_predict.return_value = np.array([[1.0, 2.0, 0.1, 0.2]])
        
        expected_results = {
            'lights': {'light1': 1, 'light2': 2},
            'temperatures': {'temp1': 21.0, 'temp2': 22.0}
        }
        mock_process.return_value = (np.array([1, 2, 21.0, 22.0]), expected_results)
        
        # Execute
        results = ai_predict(mock_model)
        
        # Assert
        mock_preprocess.assert_called_once()
        mock_predict.assert_called_once()
        mock_process.assert_called_once()
        self.assertEqual(results, expected_results)
    
    @patch('ai.predict.load_and_preprocess_data')
    def test_ai_predict_exception(self, mock_preprocess):
        # Setup
        mock_model = MagicMock()
        mock_preprocess.side_effect = Exception("Processing error")
        
        # Execute
        result = ai_predict(mock_model)
        
        # Assert
        self.assertIsNone(result)  # Function catches the exception and returns None


if __name__ == '__main__':
    unittest.main()