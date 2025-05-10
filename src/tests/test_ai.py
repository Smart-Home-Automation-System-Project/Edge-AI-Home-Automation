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
        mock_results = {
            'temperatures': {'kitchen_temp': 22.5, 'living_room_temp': 23.0},
            'lights': {'kitchen_light': 2, 'living_room_light': 3}
        }
        mock_predict.return_value = mock_results

        # Execute
        run_predictions_and_publish(mock_model, mock_client)

        # Assert
        mock_predict.assert_called_once_with(mock_model)

        # Verify light publishing logic
        expected_calls = [
            call('sensor/main/ctrl', json.dumps({"name": k, "irgb": f"{v},N,N,N"}))
            for k, v in mock_results['lights'].items()
        ]
        mock_client.publish.assert_has_calls(expected_calls, any_order=True)

    @patch('ai.ai.ai_predict')
    def test_run_predictions_and_publish_exception(self, mock_predict):
        # Setup
        mock_model = MagicMock()
        mock_client = MagicMock()
        mock_predict.side_effect = Exception("Prediction failed")

        # Execute
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
        # Setup
        mock_sleep.side_effect = [None, KeyboardInterrupt]  # Exit after one loop
        mock_isfile.return_value = False  # No new model file
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        mock_client = MagicMock()

        # Execute
        with self.assertRaises(KeyboardInterrupt):  # Expect loop to exit
            init_ai(mock_client)

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
        # Setup
        mock_sleep.side_effect = [None, KeyboardInterrupt]  # Exit after one loop
        mock_isfile.side_effect = [True, True, False]  # Simulate model update
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        mock_client = MagicMock()

        # Execute
        with self.assertRaises(KeyboardInterrupt):  # Expect loop to exit
            init_ai(mock_client)

        # Assert
        self.assertEqual(mock_load_model.call_count, 2)  # Reloaded after update
        self.assertEqual(mock_isfile.call_count, 3)  # Checked multiple times
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
        # Setup
        mock_sleep.side_effect = [None, KeyboardInterrupt]  # Exit after one loop
        mock_isfile.return_value = False
        mock_run.side_effect = Exception("Something went wrong")
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        mock_client = MagicMock()

        # Execute
        with self.assertRaises(KeyboardInterrupt):  # Expect loop to exit
            init_ai(mock_client)

        # Assert
        mock_run.assert_called_once()
        mock_sleep.assert_called_once_with(10)


if __name__ == '__main__':
    unittest.main()
