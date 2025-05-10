# Database Tests

This directory (`src/tests/test_database/`) contains unit tests for the database functionality of the project. The tests cover various aspects of the database operations, including setup, core functionality, concurrency, initialization, predictions, category queries, error handling, and table deletion.

## Files Overview

Below is a summary of the test files included in this directory:

- **`test_db_setup.py`**: Tests the initial database setup, including:
  - Database file creation
  - Table structure verification (e.g., `sensors` and `sensor_data` tables)
  - Trigger functionality (e.g., updating `last_val` in the `sensors` table)
  - Primary key constraints

- **`test_database_core.py`**: Tests core database operations, such as:
  - Adding and retrieving modules
  - Assigning names to modules
  - Adding sensor data
  - Retrieving IDs and client IDs
  - Replacing and deleting modules
  - Fetching sensor data

- **`test_initialization.py`**: Tests database initialization scenarios, including:
  - Handling empty databases
  - Creating and verifying the `last_val` trigger

- **`test_delete_tables.py`**: Tests table deletion functionality, including:
  - Clearing the `sensor_data` table
  - Clearing the `sensors` table
  - Clearing both tables while ensuring other tables remain unaffected

- **`test_prediction.py`**: Tests prediction-related database functions, such as:
  - Retrieving sensor data for predictions
  - Saving predictions to the database
  - Fetching light and temperature sensors

- **`test_error_handling.py`**: Tests error handling in database operations, including:
  - Integrity errors (e.g., duplicate keys)
  - Operational errors (e.g., missing tables)
  - Connection errors (e.g., non-existent directories)

- **`test_category_queries.py`**: Tests category-based database queries, such as:
  - Retrieving control modules (light, switch, door)
  - Fetching current power data for modules
  - Querying sensors by category
  - Retrieving module types by client ID

- **`test_concurrency.py`**: Tests database concurrency handling, including:
  - Concurrent access to the database by multiple threads
  - Lock contention scenarios to ensure proper transaction handling

- **`test_base.py`**: Provides a base class (`DatabaseTestBase`) for all database tests, including:
  - Setup and teardown methods for creating and cleaning up temporary test databases
  - Common table creation logic for `sensors`, `sensor_data`, and `predictions`

- **`run_all_tests.py`**: A script to run all database tests in this directory, aggregating test suites from the above files and providing a unified test runner.

## Prerequisites

To run these tests, ensure the following dependencies are installed:

- Python 3.x
- Required Python packages (listed in the project's `requirements.txt` or equivalent):
  - `unittest` (standard library)
  - `sqlite3` (standard library)
  - `tempfile` (standard library)
  - `uuid` (standard library)
  - `datetime` (standard library)
  - Project-specific modules (e.g., `src.database.database`)

The tests assume the project structure includes a `src/database/` directory with the `database.py` module containing the database operations being tested.

## Running the Tests

To run all tests, execute the `run_all_tests.py` script from the command line:

```bash
python src/tests/test_database/run_all_tests.py
```

This will discover and run all test cases in the directory, outputting the results with verbosity level 2 for detailed feedback.

To run individual test files, use:

```bash
python src/tests/test_database/<test_file>.py
```

For example:

```bash
python src/tests/test_database/test_database_core.py
```

## Test Environment

The tests use temporary SQLite databases created in the system's temporary directory to avoid affecting the production database. Each test sets up a fresh database with the required schema and tears it down after completion to ensure isolation.

The `DatabaseTestBase` class configures the database with Write-Ahead Logging (WAL) mode to support concurrent access testing.

## Notes

- The tests use a mocked `globals` module to simulate client IDs (`test_client`) for consistency.
- Some tests involve concurrency and threading; ensure your system supports multiple threads for `test_concurrency.py`.
- The `tearDown` method in `test_base.py` includes retry logic to handle potential file permission issues when deleting temporary files on certain systems.

For issues or contributions, please refer to the project's main README or contact the repository maintainers.