#!/usr/bin/env python3
import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from tests.test_predict import TestPredictFunctions
from tests.test_train import TestTrainFunctions
from tests.test_ai import TestAiFunctions
from tests.test_integration import TestAiIntegration

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromTestCase(TestPredictFunctions))
    test_suite.addTests(loader.loadTestsFromTestCase(TestTrainFunctions))
    test_suite.addTests(loader.loadTestsFromTestCase(TestAiFunctions))
    test_suite.addTests(loader.loadTestsFromTestCase(TestAiIntegration))
    
    # print("\n\n\nTests to be run:\n")
    # print(test_suite)
    # print("\n\n\n")
    # print("End of tests to be run\n")
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate status code
    sys.exit(not result.wasSuccessful())