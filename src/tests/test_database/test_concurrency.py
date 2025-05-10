import threading
import sqlite3

from test_base import DatabaseTestBase
from src.database import database

class TestDatabaseConcurrency(DatabaseTestBase):
    """Tests for database concurrency handling."""

    def test_db_concurrent_access(self):
        """Test concurrent access to the database."""
        # Add a sensor
        sensor_id = database.db_add_sensor("concurrent", "Concurrent Sensor", "temp", self.test_db_path)

        # Define a function to add sensor data
        def add_data(thread_id):
            timestamp = f"2023-01-01 {thread_id:02d}:00:00"
            database.db_add_sensor_data(timestamp, sensor_id, thread_id, self.test_db_path)

        # Create and start threads
        threads = []
        for i in range(1, 11):  # 10 threads
            thread = threading.Thread(target=add_data, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all data was added correctly
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sensor_data WHERE sensor_id = ?", (sensor_id,))
            count = cursor.fetchone()[0]

        self.assertEqual(count, 10)

    def test_db_lock_contention(self):
        """Test database lock contention handling."""
        # Add a sensor
        sensor_id = database.db_add_sensor("lock_test", "Lock Test Sensor", "temp", self.test_db_path)
        
        # Create a long-running transaction in one thread
        def long_transaction():
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            cursor.execute("BEGIN EXCLUSIVE TRANSACTION")
            # Insert some data
            cursor.execute("""
                INSERT INTO sensor_data (sensor_id, timestamp, sensor_value)
                VALUES (?, ?, ?)
            """, (sensor_id, "2023-01-01 00:00:00", 20.0))
            # Sleep to simulate a long transaction
            import time
            time.sleep(1)
            conn.commit()
            conn.close()
        
        # Create another thread that tries to access the database while locked
        def concurrent_access():
            # This should wait for the lock to be released
            database.db_add_sensor_data("2023-01-01 01:00:00", sensor_id, 21.0, self.test_db_path)
        
        # Start the long transaction
        t1 = threading.Thread(target=long_transaction)
        t1.start()
        
        # Give it a moment to acquire the lock
        import time
        time.sleep(0.1)
        
        # Start the concurrent access
        t2 = threading.Thread(target=concurrent_access)
        t2.start()
        
        # Wait for both to complete
        t1.join()
        t2.join()
        
        # Verify both data points were added
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sensor_data WHERE sensor_id = ?", (sensor_id,))
            count = cursor.fetchone()[0]
        
        self.assertEqual(count, 2)

if __name__ == '__main__':
    unittest.main()