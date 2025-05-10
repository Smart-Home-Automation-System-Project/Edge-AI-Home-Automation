# Edge AI Home Automation Testing Guide

This guide explains how to run and maintain the unit tests for the Edge AI Home Automation project.

## Test Structure

The tests are organized into the following files:

- `test_predict.py`: Tests for the AI prediction functionality
- `test_train.py`: Tests for the model training functionality
- `test_ai.py`: Tests for the AI orchestration components
- `test_integration.py`: Integration tests for the entire AI pipeline
- `conftest.py`: Common fixtures and mock data
- `run_tests.py`: Script to run all tests

## Setting Up the Test Environment

1. Make sure you have the required packages installed:

```bash
pip install pytest pytest-mock tensorflow numpy pandas
```

2. Place the test files in a `tests` directory in your project:

```
edge_ai_project/
├── ai/
│   ├── ai.py
│   ├── predict.py
│   └── train.py
├── database/
│   └── database.py
├── sensor/
│   └── topics.py
└── tests/
    ├── conftest.py
    ├── run_tests.py
    ├── test_ai.py
    ├── test_integration.py
    ├── test_predict.py
    └── test_train.py
```

## Running the Tests

You can run all tests using the `run_tests.py` script:

```bash
python tests/run_tests.py
```

Or run individual test files using pytest:

```bash
# Run a specific test file
pytest tests/test_predict.py -v

# Run a specific test class
pytest tests/test_predict.py::TestPredictFunctions -v

# Run a specific test
pytest tests/test_predict.py::TestPredictFunctions::test_load_model -v
```

## Understanding the Tests

### Unit Tests

The unit tests verify each function in isolation:

- **test_predict.py**: Tests functions related to making predictions with the AI model
- **test_train.py**: Tests functions related to training the AI model
- **test_ai.py**: Tests the main AI module that orchestrates model loading and predictions

### Integration Tests

The integration tests verify that components work together correctly:

- **test_integration.py**: Tests the end-to-end workflow from training to prediction

## Mocking

The tests use Python's `pytest-mock` module to replace external dependencies like:

- Database calls
- TensorFlow model operations
- File system operations
- MQTT client publishing

This allows for testing in isolation without needing actual databases or sensors.

## Test Coverage

To check test coverage, install the `pytest-cov` package:

```bash
pip install pytest-cov
```

Then run:

```bash
pytest --cov=ai tests/
```

This will show the percentage of code that's covered by tests.

## Maintaining Tests

When making changes to the AI modules:

1. Update the corresponding tests.
2. Add new tests for new functionality.
3. Run the tests to make sure everything still works.
4. Check the test coverage to ensure new code is properly tested.

## Common Testing Patterns

The tests demonstrate several useful testing patterns:

- **Patching external dependencies**: Using `@patch` to replace functions like database calls.
- **Mocking objects**: Creating mock models and clients.
- **Error handling**: Testing how functions handle exceptions.
- **Integration testing**: Testing the entire workflow from training to prediction.

## Best Practices

- Keep tests independent of each other.
- Test both normal and error conditions.
- Mock external dependencies.
- Use descriptive test names.
- Keep tests simple and focused.
- Regularly run tests when making changes.
- Check test coverage to ensure critical code paths are tested.