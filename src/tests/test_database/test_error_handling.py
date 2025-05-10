import sqlite3
import os
import tempfile
import unittest
import uuid

from test_base import DatabaseTestBase
from src.database import database
# Use DatabaseError from the database module
# Instead of: from src.database import database, DatabaseError

class TestDatabaseErrorHandling(DatabaseTestBase):
    """Tests for database error handling."""

    def test_db_integrity_error(self):
        """Test handling of integrity errors (duplicate keys)."""
        # Add a sensor
        sensor_id = str(uuid.uuid4())
        client_id = "unique_client"
        
        # Insert directly to bypass the error handling in db_add_module
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sensors (id, client_id, name, category, last_val)
                VALUES (?, ?, ?, ?, ?)
            """, (sensor_id, client_id, "Test Sensor", "light", None))
        
        # Try to add another sensor with the same client_id
        result = database.db_add_module(client_id, "Duplicate Sensor", "light", self.test_db_path)
        
        # Should return None due to integrity error
        self.assertIsNone(result)

    def test_db_operational_error_handling(self):
        """Test handling of operational errors."""
        # Create a database file that will cause operational errors
        bad_db = tempfile.NamedTemporaryFile(delete=False).name
        
        try:
            # Create an invalid database (missing tables)
            with sqlite3.connect(bad_db) as conn:
                # Don't create any tables
                pass
            
            # Mock the client_id to match the UI client ID to trigger the exception
            original_client_id = database.ui_client_id
            database.ui_client_id = 'test_client'  # This matches our MockGlobals.client_id
            
            # This should raise DatabaseError since the required tables don't exist
            with self.assertRaises(database.DatabaseError):  # Use database.DatabaseError instead
                database.db_get_available_all_modules(bad_db)
            
            # Restore the original client_id
            database.ui_client_id = original_client_id
        finally:
            # Clean up
            try:
                os.remove(bad_db)
            except:
                pass

    def test_db_connection_error(self):
        """Test handling of connection errors."""
        # Create a path to a non-existent directory
        nonexistent_dir = "/nonexistent_dir_" + str(uuid.uuid4())
        bad_db_path = os.path.join(nonexistent_dir, "database.db")
        
        # Mock the client_id to match the UI client ID to trigger the exception
        original_client_id = database.ui_client_id
        database.ui_client_id = 'test_client'  # This matches our MockGlobals.client_id
        
        # This should raise DatabaseError since the directory doesn't exist
        with self.assertRaises(database.DatabaseError):  # Use database.DatabaseError instead
            database.db_get_available_all_modules(bad_db_path)
        
        # Restore the original client_id
        database.ui_client_id = original_client_id

if __name__ == '__main__':
    unittest.main()