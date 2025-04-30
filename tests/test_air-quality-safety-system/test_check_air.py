# tests/air_quality_safety_system/test_check_air.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from air_quality_safety_system.check_air import check_air_quality
zz

class TestCheckAir(unittest.TestCase): # class TestCheckAir inherits from 'unittest.TestCase'

    # Patch is a decorator from 'unittest.mock' module.
    # The specified object inside it will be replaced with a 'mock'/dummy object
    # during the test and restored when the test ends.
    # It finds the real 'publish_message' inside check_air.py.It swaps it out with a fake version that:
    # Does nothing when called (no real MQTT messages sent).
    # But remembers how it was used (what arguments were passed, how many times it was called, etc).

    @patch('air_quality_safety_system.check_air.publish_message')
    def test_co2_high_level(self, mock_publish):
        """Test that high CO2 levels trigger exhaust fan"""
        # Reset state
        import air_quality_safety_system.check_air as check_air
        check_air.exhaustOn = False

        # Test with high CO2
        check_air_quality(1200, 50, 30, 200)

        # Verify exhaust fan turned on
        self.assertTrue(check_air.exhaustOn)

        # Verify mqtt message was published
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], "home/automation/co2_control") # checks whether the topic used in the MQTT message was correct
        self.assertTrue("exhaust_fan" in args[1]) # checks that "exhaust_fan" is present in the message payload
        self.assertEqual(args[1]["exhaust_fan"], 1) # asserts that the value of "exhaust_fan" in the payload is 1

    @patch('air_quality_safety_system.check_air.publish_message')
    def test_co2_normal_level(self, mock_publish):
        """Test that normal CO2 levels turn off exhaust fan"""
        # Set initial state
        import air_quality_safety_system.check_air as check_air
        check_air.exhaustOn = True

        # Test with normal CO2
        check_air_quality(700, 50, 30, 200)

        # Verify exhaust fan turned off
        self.assertFalse(check_air.exhaustOn)

        # Verify mqtt message was published
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], "home/automation/co2_control")# checks whether the topic used in the MQTT message was correct
        self.assertEqual(args[1]["exhaust_fan"], 0)# asserts that the value of "exhaust_fan" in the payload is 0

    @patch('air_quality_safety_system.check_air.publish_message')
    def test_cooking_smoke(self, mock_publish):
        """Test cooking smoke detection (high smoke, low CO)"""
        # Reset state
        import air_quality_safety_system.check_air as check_air
        check_air.exhaustOn = False
        check_air.alarmOn_smoke = False

        # Test cooking smoke (high smoke, low CO)
        check_air_quality(900, 80, 40, 200, threshold_smoke=70, threshold_co=50)

        # Verify exhaust fan turned on but alarm stays off
        self.assertTrue(check_air.exhaustOn)
        self.assertFalse(check_air.alarmOn_smoke)

        # Verify mqtt message was published
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], "home/automation/smoke_detection")
        self.assertEqual(args[1]["alarm"], 0)

    @patch('air_quality_safety_system.check_air.publish_message')
    def test_fire_smoke(self, mock_publish):
        """Test fire smoke detection (high smoke, high CO)"""
        # Reset state
        import air_quality_safety_system.check_air as check_air
        check_air.exhaustOn = False
        check_air.alarmOn_smoke = False

        # Test fire smoke (high smoke, high CO)
        check_air_quality(900, 100, 60, 200, threshold_smoke=70, threshold_co=50)

        # Verify exhaust fan and alarm turned on
        self.assertTrue(check_air.exhaustOn)
        self.assertTrue(check_air.alarmOn_smoke)

        # Verify mqtt message was published
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], "home/automation/smoke_detection")
        self.assertEqual(args[1]["alarm"], 1)

    @patch('air_quality_safety_system.check_air.publish_message')
    def test_gas_leak(self, mock_publish):
        """Test gas leak detection"""
        # Reset state
        import air_quality_safety_system.check_air as check_air
        check_air.exhaustOn = False
        check_air.alarmOn_gas = False
        check_air.gas_applianceOn = True
        check_air.gas_val_close = False

        # Test gas leak (high gas level)
        check_air_quality(900, 50, 30, 300, gas_threshold=250)

        # Verify all safety measures activated
        self.assertTrue(check_air.exhaustOn)
        self.assertTrue(check_air.alarmOn_gas)
        self.assertFalse(check_air.gas_applianceOn)
        self.assertTrue(check_air.gas_val_close)

        # Verify mqtt message was published
        mock_publish.assert_called_once()
        args = mock_publish.call_args[0]
        self.assertEqual(args[0], "home/automation/gas_detection")
        self.assertEqual(args[1]["alarm"], 1)
        self.assertEqual(args[1]["gas_valve_closed"], 1)
        self.assertEqual(args[1]["gas_appliance"], 0)
        self.assertTrue(len(args[1]["actions"]) == 4)  # All 4 actions triggered

# Scans the file for any class that inherits from unittest.TestCase
# Automatically finds all methods that start with test_
# Runs each one as a separate test case
if __name__ == "__main__":
    unittest.main()

