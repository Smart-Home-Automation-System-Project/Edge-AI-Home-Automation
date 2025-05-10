# AI Test Suite

This directory (`src/tests/test-ai/`) contains the test suite for the AI modules located in `src/ai/`. The tests are written using Python's `unittest` framework and utilize mocking to isolate dependencies, ensuring robust and reliable testing of the AI functionality. The suite covers unit tests, integration tests, and fixtures for the prediction, training, and main AI logic components.

## Directory Structure

The `src/tests/test-ai/` folder contains the following files:

- **`conftests.py`**: Defines shared fixtures used across multiple test files. These fixtures provide mock sensor data, a mock 24-hour DataFrame, and a simple TensorFlow model for testing.
- **`test_ai.py`**: Contains unit tests for the main AI logic in `src/ai/ai.py`, including functions like `adjust_predictions`, `run_predictions_and_publish`, and `init_ai`.
- **`test_integration.py`**: Includes integration tests that verify the end-to-end workflow, combining training, prediction, and publishing functionality across `src/ai/train.py`, `src/ai/predict.py`, and `src/ai/ai.py`.
- **`test_predict.py`**: Contains unit tests for the prediction-related functions in `src/ai/predict.py`, such as `load_model`, `load_and_preprocess_data`, `make_predictions`, `process_predictions`, and `ai_predict`.
- **`test_train.py`**: Includes unit tests for the training-related functions in `src/ai/train.py`, including `load_and_preprocess_data`, `prepare_sequences`, `create_lstm_model`, `train_model`, `save_model`, and `main`.
- **`run_tests.py`**: A script to execute all tests in the suite, aggregating test cases from the above files and reporting results.

## File Descriptions

### conftests.py
This file defines reusable fixtures for the test suite using `pytest`. The fixtures include:
- `mock_sensor_data`: Mock sensor data simulating light and temperature sensor readings.
- `mock_df_24h`: A mock Pandas DataFrame with 24 hours of sensor data, including timestamps, light, temperature, hour, and day-of-week features.
- `mock_test_model`: A simple TensorFlow LSTM model for testing, with an input shape of `(24, 4)` and a compiled configuration.

These fixtures ensure consistent test data and reduce code duplication across test files.

### test_ai.py
Tests the core AI logic in `src/ai/ai.py`. Key test cases include:
- Testing `adjust_predictions` for standard and special lights (e.g., `l5`, `l6`) with different presence scenarios.
- Verifying `run_predictions_and_publish` for correct prediction and MQTT publishing behavior.
- Testing `init_ai` for normal operation and model updates.

The tests use mocking to isolate database calls, file operations, and model loading.

### test_integration.py
Contains integration tests that validate the interaction between training, prediction, and publishing modules. Key test cases:
- `test_predict_integration`: Tests the prediction pipeline with a real model and mock data.
- `test_run_predictions_and_publish_integration`: Verifies the prediction and publishing workflow.
- `test_train_to_predict_workflow`: Tests the end-to-end process from training a model to using it for predictions.

These tests ensure the AI system works cohesively across its components.

### test_predict.py
Focuses on unit tests for prediction functions in `src/ai/predict.py`. Test cases cover:
- Model loading (`load_model`) with success and failure scenarios.
- Data preprocessing (`load_and_preprocess_data`) with sufficient and insufficient data.
- Prediction generation (`make_predictions`) and processing (`process_predictions`).
- The main prediction function (`ai_predict`) with normal and error cases.

### test_train.py
Tests the training functions in `src/ai/train.py`. Test cases include:
- Data loading and preprocessing (`load_and_preprocess_data`).
- Sequence preparation for LSTM training (`prepare_sequences`).
- Model creation (`create_lstm_model`) and training (`train_model`).
- Model saving (`save_model`) and the main training workflow (`main`).

### run_tests.py
A Python script that aggregates and runs all test cases from `test_predict.py`, `test_train.py`, `test_ai.py`, and `test_integration.py`. It uses `unittest.TextTestRunner` to execute the tests and reports results with verbosity level 2. The script exits with a non-zero status code if any tests fail, making it suitable for CI/CD pipelines.

## Prerequisites

To run the tests, ensure the following dependencies are installed:
- Python 3.8+
- `unittest` (included in Python standard library)
- `numpy`
- `pandas`
- `tensorflow`
- `unittest.mock` (included in Python standard library)

Install dependencies using:
```bash
pip install numpy pandas tensorflow
```

## Running the Tests

To execute the test suite, navigate to the `src/tests/test-ai/` directory and run:
```bash
python run_tests.py
```

This will:
1. Load all test cases from the test files.
2. Run the tests with detailed output (verbosity=2).
3. Display the number of tests run, failures, and errors.
4. Exit with a status code indicating success (0) or failure (non-zero).

Example output:
```
test_load_model (test_predict.TestPredictFunctions) ... ok
test_predict_integration (test_integration.TestAiIntegration) ... ok
...
----------------------------------------------------------------------
Ran 20 tests in 2.345s

OK
```

## Notes
- **Mocking**: The tests heavily use `unittest.mock` to mock database calls (`db_get_*`), file operations, and model loading to isolate the AI logic from external dependencies.
- **Test Data**: The fixtures provide realistic mock data for a home automation scenario, simulating light and temperature sensors over time.
- **Integration Tests**: The integration tests assume the AI modules (`train.py`, `predict.py`, `ai.py`) are correctly implemented. If errors occur, verify the implementation of these modules.
- **Extensibility**: New tests can be added by creating additional test files and updating `run_tests.py` to include them.

## Troubleshooting
- **ModuleNotFoundError**: Ensure the `src/ai/` directory is accessible by verifying the `sys.path` modifications in the test files.
- **TensorFlow Errors**: Check that the TensorFlow version is compatible (e.g., 2.x) and that the model configurations match the expected input/output shapes.
- **Test Failures**: Review the error messages and stack traces. Common issues include shape mismatches in TensorFlow models or incorrect mock setups.

For further assistance, contact the development team or refer to the documentation in `src/ai/`.