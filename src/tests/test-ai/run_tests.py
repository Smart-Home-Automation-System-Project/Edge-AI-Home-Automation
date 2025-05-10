#!/usr/bin/env python3
import unittest
import os
import sys

# Add project root to path - adjusted for the new location in tests/test-ai/
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import test modules
from test_predict import TestPredictFunctions
from test_train import TestTrainFunctions
from test_ai import TestAI
from test_integration import TestAiIntegration

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromTestCase(TestPredictFunctions))
    test_suite.addTests(loader.loadTestsFromTestCase(TestTrainFunctions))
    test_suite.addTests(loader.loadTestsFromTestCase(TestAI))
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