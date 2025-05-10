import unittest
import sys
import os

# Get the absolute path to the directory containing this file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the path so Python can find the test modules
sys.path.insert(0, current_dir)

# Import all test modules with absolute imports
from test_database_core import TestDatabaseCore
from test_concurrency import TestDatabaseConcurrency
from test_initialization import TestDatabaseInitialization
from test_prediction import TestDatabasePrediction
from test_category_queries import TestDatabaseCategoryQueries
from test_error_handling import TestDatabaseErrorHandling
from test_delete_tables import TestDeleteTables
from test_db_setup import TestDatabaseSetup

def run_all_tests():
    """Run all database tests."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases from each module
    test_suite.addTest(unittest.makeSuite(TestDatabaseCore))
    test_suite.addTest(unittest.makeSuite(TestDatabaseConcurrency))
    test_suite.addTest(unittest.makeSuite(TestDatabaseInitialization))
    test_suite.addTest(unittest.makeSuite(TestDatabasePrediction))
    test_suite.addTest(unittest.makeSuite(TestDatabaseCategoryQueries))
    test_suite.addTest(unittest.makeSuite(TestDatabaseErrorHandling))
    test_suite.addTest(unittest.makeSuite(TestDeleteTables))
    test_suite.addTest(unittest.makeSuite(TestDatabaseSetup))
    
    # Create a test runner
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = test_runner.run(test_suite)
    
    # Return the result
    return result

if __name__ == '__main__':
    # Run all tests
    result = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())