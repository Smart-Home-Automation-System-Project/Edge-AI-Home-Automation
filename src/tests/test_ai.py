import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import os
import sys
import json
import time

# Add the parent directory to sys.path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions to test
from ai.ai import run_predictions_and_publish, init_ai


class TestAiFunctions(unittest.TestCase):
    
    @patch('ai.ai.ai_predict')
    def test_run_predictions_and_publish_success(self, mock_predict):
        # Setup
        mock_model = MagicMock()
        mock_client = MagicMock()
        
        # Create a mock result from ai_predict
        mock_results = {
            'temperatures': {'kitchen_temp': 22.5, 'living_room_temp': 23.0},
            'lights': {'kitchen_light': 2, 'living_room_light': 3}
        }
        mock_predict.return_value = mock_results
        
        # Execute
        run_predictions_and_publish(mock_model, mock_client)
        
        # Assert
        mock_predict.assert_called_once_with(mock_model)
        
        # Note: Currently the temp publishing logic is disabled with 'continue'
        # So we'll only check the light publishing part
        expected_calls = []
        for k, v in mock_results['lights'].items():
            irgb_value = f"{v},N,N,N"
            expected_calls.append(
                call('sensor/main/ctrl', 
                     json.dumps({"name": k, "irgb": irgb_value}))
            )
        
        mock_client.publish.assert_has_calls(expected_calls)
    
    @patch('ai.ai.ai_predict')
    def test_run_predictions_and_publish_exception(self, mock_predict):
        # Setup
        mock_model = MagicMock()
        mock_client = MagicMock()
        mock_predict.side_effect = Exception("Prediction failed")
        
        # Execute - this should not raise an exception due to the try/except block
        run_predictions_and_publish(mock_model, mock_client)
        
        # Assert
        mock_predict.assert_called_once_with(mock_model)
        mock_client.publish.assert_not_called()
    
    @patch('ai.ai.load_model')
    @patch('ai.ai.os.path.isfile')
    @patch('ai.ai.os.remove')
    @patch('ai.ai.os.rename')
    @patch('ai.ai.run_predictions_and_publish')
    @patch('ai.ai.time.sleep')
    def test_init_ai_no_update(self, mock_sleep, mock_run, mock_rename, 
                             mock_remove, mock_isfile, mock_load_model):
        # Setup to exit after one loop
        mock_sleep.side_effect = [None, KeyboardInterrupt]  # Run once then exit loop
        mock_isfile.return_value = False  # No new model file
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        mock_client = MagicMock()
        
        # Execute
        try:
            init_ai(mock_client)
        except KeyboardInterrupt:
            pass  # Expected to break the loop
        
        # Assert
        mock_load_model.assert_called_once()
        mock_isfile.assert_called_once()
        mock_rename.assert_not_called()
        mock_remove.assert_not_called()
        mock_run.assert_called_once_with(mock_model, mock_client)
        mock_sleep.assert_called_once_with(10)
    
    @patch('ai.ai.load_model')
    @patch('ai.ai.os.path.isfile')
    @patch('ai.ai.os.remove')
    @patch('ai.ai.os.rename')
    @patch('ai.ai.run_predictions_and_publish')
    @patch('ai.ai.time.sleep')
    def test_init_ai_with_update(self, mock_sleep, mock_run, mock_rename, 
                               mock_remove, mock_isfile, mock_load_model):
        # Setup to simulate model update then exit
        mock_sleep.side_effect = [None, KeyboardInterrupt]  # Run once then exit loop
        
        # First check for new model returns True, second False
        mock_isfile.side_effect = [True, True, False]  
        
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        mock_client = MagicMock()
        
        # Execute
        try:
            init_ai(mock_client)
        except KeyboardInterrupt:
            pass  # Expected to break the loop
        
        # Assert
        # Should be called twice - once initially and once after model update
        self.assertEqual(mock_load_model.call_count, 2)
        self.assertEqual(mock_isfile.call_count, 3)  # Checked new model, old model, then new model again
        mock_remove.assert_called_once()
        mock_rename.assert_called_once()
        mock_run.assert_called_once_with(mock_model, mock_client)
        mock_sleep.assert_called_once_with(10)
    
    @patch('ai.ai.load_model')
    @patch('ai.ai.os.path.isfile')
    @patch('ai.ai.run_predictions_and_publish')
    @patch('ai.ai.time.sleep')
    def test_init_ai_exception_handling(self, mock_sleep, mock_run, 
                                      mock_isfile, mock_load_model):
        # Setup to simulate an exception in the main loop then exit
        mock_sleep.side_effect = [None, KeyboardInterrupt]  # Run once then exit loop
        mock_isfile.return_value = False
        mock_run.side_effect = Exception("Something went wrong")
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        mock_client = MagicMock()
        
        # Execute - should catch the exception and continue
        try:
            init_ai(mock_client)
        except KeyboardInterrupt:
            pass  # Expected to break the loop
        
        # Assert - should still try to sleep despite the exception
        mock_run.assert_called_once()
        mock_sleep.assert_called_once_with(10)


if __name__ == '__main__':
    unittest.main()