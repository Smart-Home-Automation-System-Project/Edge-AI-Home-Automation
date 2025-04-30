import unittest
from unittest.mock import patch, MagicMock, call, ANY
import os
import sys
import datetime

# Add the parent directory to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from lights_temp_automation import weekly_check_loop


class TestWeeklyCheckLoop(unittest.TestCase):

    @patch('lights_temp_automation.weekly_check_loop.is_training_time')
    @patch('lights_temp_automation.weekly_check_loop.subprocess.run')
    @patch('lights_temp_automation.weekly_check_loop.os.getenv')
    def test_training_execution_when_time(self, mock_getenv, mock_subprocess, mock_is_training_time):
        # Setup mock paths
        mock_getenv.return_value = '/fake/path'

        # Mock that it is training time and we haven't trained today
        mock_is_training_time.return_value = True

        # Mock subprocess responses - all successful
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Reset the global variables for testing
        weekly_check_loop.training_done_today = False
        weekly_check_loop.last_training_date = None

        # Run the main function once
        with patch('builtins.print'), patch('time.sleep'):
            weekly_check_loop.main()

            expected_train_call = call(['python', ANY], capture_output=True, text=True, encoding='utf-8')
            expected_predict_call = call(['python', ANY], capture_output=True, text=True, encoding='utf-8')
            expected_publish_call = call(['python', ANY], capture_output=True, text=True, encoding='utf-8')

            mock_subprocess.assert_has_calls([
                expected_train_call,
                expected_predict_call,
                expected_publish_call
            ], any_order=False)

            self.assertTrue(weekly_check_loop.training_done_today)

    @patch('lights_temp_automation.weekly_check_loop.is_training_time')
    @patch('lights_temp_automation.weekly_check_loop.subprocess.run')
    @patch('lights_temp_automation.weekly_check_loop.os.getenv')
    def test_prediction_only_when_not_training_time(self, mock_getenv, mock_subprocess, mock_is_training_time):
        mock_getenv.return_value = '/fake/path'
        mock_is_training_time.return_value = False
        mock_subprocess.return_value = MagicMock(returncode=0)

        weekly_check_loop.training_done_today = False
        weekly_check_loop.last_training_date = None

        with patch('builtins.print'), patch('time.sleep'):
            weekly_check_loop.main()

            # Ensure train.py was NOT called
            for call_args in mock_subprocess.call_args_list:
                script = call_args[0][0][1]
                self.assertNotIn('train.py', script)

            # Ensure predict.py was called
            self.assertTrue(any('predict.py' in call_args[0][0][1] for call_args in mock_subprocess.call_args_list))

    @patch('lights_temp_automation.weekly_check_loop.datetime')
    def test_is_training_time_logic(self, mock_datetime):
        original_force = weekly_check_loop.FORCE_TRAINING
        weekly_check_loop.FORCE_TRAINING = False

        try:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 6  # Sunday
            mock_now.hour = 23
            mock_now.minute = 45
            mock_datetime.now.return_value = mock_now

            self.assertTrue(weekly_check_loop.is_training_time())

            mock_now.hour = 22
            mock_now.minute = 45
            self.assertFalse(weekly_check_loop.is_training_time())

            mock_now.weekday.return_value = 0  # Monday
            mock_now.hour = 23
            mock_now.minute = 45
            self.assertFalse(weekly_check_loop.is_training_time())

            weekly_check_loop.FORCE_TRAINING = True
            mock_now.weekday.return_value = 0
            mock_now.hour = 12
            self.assertTrue(weekly_check_loop.is_training_time())

        finally:
            weekly_check_loop.FORCE_TRAINING = original_force


if __name__ == '__main__':
    unittest.main()
