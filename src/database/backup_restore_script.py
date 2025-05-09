import os
import sqlite3
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import json

class DatabaseBackupRestore:
    def __init__(self, db_path, collection_prefix='backup'):
        """Initialize with database path and Firestore collection prefix"""
        self.db_path = db_path
        self.collection_prefix = collection_prefix
        self.firebase_app = None
        self.db = None
        
    def connect_firestore(self, cred_path):
        """Connect to Firestore using the provided credentials"""
        try:
            if not self.firebase_app:
                cred = credentials.Certificate(cred_path)
                self.firebase_app = firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("Successfully connected to Firestore")
            return True
        except Exception as e:
            print(f"Error connecting to Firestore: {e}")
            return False
    
    def get_sqlite_connection(self):
        """Get a connection to the SQLite database"""
        return sqlite3.connect(self.db_path)
    
    def backup_database(self, days_to_keep=10):
        """
        Backup the SQLite database to Firestore
        Only includes sensor_data from the last X days
        """
        if not self.db:
            print("Firestore not connected. Please connect first.")
            return False
            
        # Get current timestamp for backup ID
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"{self.collection_prefix}_{timestamp}"
        
        # Calculate cutoff date for sensor data (last X days)
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days_to_keep)).strftime("%Y-%m-%d")
        
        try:
            print(f"Starting backup {backup_id}...")
            conn = self.get_sqlite_connection()
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall() if table[0] != "sqlite_sequence"]
            
            # Create a batch for more efficient writing
            batch = self.db.batch()
            count = 0
            batch_size = 500  # Firestore batch size limit is 500
            
            # Create metadata document
            metadata_ref = self.db.collection(backup_id).document('_metadata')
            metadata = {
                'timestamp': timestamp,
                'tables': tables,
                'days_kept': days_to_keep,
                'cutoff_date': cutoff_date
            }
            batch.set(metadata_ref, metadata)
            count += 1
            
            # Process each table
            for table in tables:
                print(f"Backing up table: {table}")
                
                if table == 'sensor_data':
                    # For sensor_data, only get last X days
                    cursor.execute(f"SELECT * FROM {table} WHERE timestamp >= ?", (cutoff_date,))
                else:
                    # For other tables, get everything
                    cursor.execute(f"SELECT * FROM {table}")
                
                # Get column names
                column_names = [description[0] for description in cursor.description]
                
                # Process rows
                rows = cursor.fetchall()
                print(f"Found {len(rows)} rows in {table}")
                
                # Create a subcollection for each table
                for i, row in enumerate(rows):
                    # Convert row to dictionary
                    row_dict = {column_names[j]: row[j] for j in range(len(column_names))}
                    
                    # Create document reference
                    if table == 'sensor_data':
                        # Use composite key for sensor_data
                        doc_id = f"{row_dict['sensor_id']}_{row_dict['timestamp']}"
                    elif table == 'sensors':
                        # Use composite key for sensors
                        doc_id = f"{row_dict['id']}_{row_dict['client_id']}"
                    else:
                        # Fallback
                        doc_id = f"row_{i}"
                    
                    # Add to batch
                    doc_ref = self.db.collection(backup_id).document(table).collection('data').document(doc_id)
                    batch.set(doc_ref, row_dict)
                    count += 1
                    
                    # If batch is full, commit and create a new one
                    if count >= batch_size:
                        batch.commit()
                        batch = self.db.batch()
                        count = 0
                        print(f"Committed batch - continuing backup")
            
            # Commit any remaining writes
            if count > 0:
                batch.commit()
                
            print(f"Backup completed successfully: {backup_id}")
            return backup_id
            
        except Exception as e:
            print(f"Error during backup: {e}")
            return False
        finally:
            conn.close()
    
    def restore_database(self, backup_id, target_db_path=None):
        """
        Restore the database from Firestore backup
        If target_db_path is None, restore to the original path
        """
        if not self.db:
            print("Firestore not connected. Please connect first.")
            return False
            
        target_path = target_db_path if target_db_path else self.db_path
        
        # Check if target exists and create backup if needed
        if os.path.exists(target_path):
            backup_file = f"{target_path}.bak"
            try:
                os.rename(target_path, backup_file)
                print(f"Created backup of existing database: {backup_file}")
            except Exception as e:
                print(f"Warning: Could not create backup of existing database: {e}")
        
        try:
            print(f"Starting restore from backup {backup_id}...")
            
            # Get metadata
            metadata_doc = self.db.collection(backup_id).document('_metadata').get()
            if not metadata_doc.exists:
                print(f"Error: Backup {backup_id} not found or missing metadata")
                return False
                
            metadata = metadata_doc.to_dict()
            tables = metadata.get('tables', [])
            
            # Create new database
            conn = sqlite3.connect(target_path)
            cursor = conn.cursor()
            
            # Recreate schema (using the same SQL from original script)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                sensor_id TEXT,
                timestamp TEXT,
                sensor_value REAL,
                PRIMARY KEY (sensor_id, timestamp)
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensors (
                id TEXT,
                client_id TEXT,
                name TEXT,
                category TEXT,
                last_val TEXT,
                PRIMARY KEY (id, client_id)
            )
            """)
            
            cursor.execute("""
            CREATE TRIGGER update_last_val
            AFTER INSERT ON sensor_data
            FOR EACH ROW
            BEGIN
                UPDATE sensors
                SET last_val = NEW.sensor_value
                WHERE id = NEW.sensor_id;
            END
            """)
            
            # Restore data for each table
            for table in tables:
                print(f"Restoring table: {table}")
                
                # Get all documents in the table's subcollection
                docs = self.db.collection(backup_id).document(table).collection('data').stream()
                
                # Process in batches for better performance
                batch_size = 1000
                count = 0
                batch_data = []
                
                for doc in docs:
                    row_dict = doc.to_dict()
                    
                    # Extract columns and values
                    columns = list(row_dict.keys())
                    values = [row_dict[col] for col in columns]
                    
                    # Build the placeholders for SQL query
                    placeholders = ','.join(['?' for _ in columns])
                    
                    # Add to batch
                    batch_data.append((
                        f"INSERT OR REPLACE INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                        values
                    ))
                    count += 1
                    
                    # Execute batch if it's full
                    if count >= batch_size:
                        with conn:
                            for query, params in batch_data:
                                cursor.execute(query, params)
                        print(f"Restored {count} rows to {table}")
                        batch_data = []
                        count = 0
                
                # Execute any remaining items
                if batch_data:
                    with conn:
                        for query, params in batch_data:
                            cursor.execute(query, params)
                    print(f"Restored {len(batch_data)} rows to {table}")
            
            conn.commit()
            print(f"Restore completed successfully to: {target_path}")
            return True
            
        except Exception as e:
            print(f"Error during restore: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def list_backups(self):
        """List all available backups in Firestore"""
        if not self.db:
            print("Firestore not connected. Please connect first.")
            return []
            
        try:
            # Get collections that match our prefix
            collections = [coll.id for coll in self.db.collections() 
                          if coll.id.startswith(self.collection_prefix)]
            
            backup_info = []
            for backup_id in collections:
                # Get metadata for each backup
                metadata_doc = self.db.collection(backup_id).document('_metadata').get()
                if metadata_doc.exists:
                    metadata = metadata_doc.to_dict()
                    backup_info.append({
                        'backup_id': backup_id,
                        'timestamp': metadata.get('timestamp'),
                        'tables': metadata.get('tables'),
                        'days_kept': metadata.get('days_kept')
                    })
                else:
                    backup_info.append({
                        'backup_id': backup_id,
                        'metadata': 'Missing'
                    })
            
            return backup_info
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
            
    def get_latest_backup(self):
        """Get the ID of the latest backup based on timestamp in the backup ID"""
        backups = self.list_backups()
        if not backups:
            return None
            
        # Sort backups by timestamp (assuming format backup_YYYYMMDD_HHMMSS)
        # This works because of the standard timestamp format we use
        sorted_backups = sorted(backups, key=lambda x: x['backup_id'], reverse=True)
        return sorted_backups[0]['backup_id'] if sorted_backups else None


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='SQLite to Firestore Backup/Restore Tool')
    parser.add_argument('action', choices=['backup', 'restore', 'list'], help='Action to perform')
    parser.add_argument('--db-path', default='database.db', help='Path to SQLite database')
    parser.add_argument('--cred-path', required=True, help='Path to Firebase credentials JSON file')
    parser.add_argument('--days', type=int, default=10, help='Days of sensor data to keep (for backup)')
    parser.add_argument('--backup-id', help='Backup ID for restore operation (latest used if not specified)')
    parser.add_argument('--target-path', help='Target path for restored database')
    parser.add_argument('--prefix', default='backup', help='Prefix for backup collections')
    
    args = parser.parse_args()
    
    # Initialize the backup/restore manager
    manager = DatabaseBackupRestore(args.db_path, args.prefix)
    
    # Connect to Firestore
    if not manager.connect_firestore(args.cred_path):
        print("Failed to connect to Firestore. Exiting.")
        exit(1)
    
    # Perform requested action
    if args.action == 'backup':
        backup_id = manager.backup_database(args.days)
        if backup_id:
            print(f"Backup completed with ID: {backup_id}")
        else:
            print("Backup failed")
            
    elif args.action == 'list':
        backups = manager.list_backups()
        if backups:
            print("\nAvailable backups:")
            for backup in backups:
                print(f"ID: {backup['backup_id']}")
                print(f"  Timestamp: {backup.get('timestamp', 'N/A')}")
                print(f"  Tables: {', '.join(backup.get('tables', ['N/A']))}")
                print(f"  Days kept: {backup.get('days_kept', 'N/A')}")
                print()
        else:
            print("No backups found")
            
    elif args.action == 'restore':
        backup_id = args.backup_id
        
        # If no backup ID is provided, get the latest one
        if not backup_id:
            backup_id = manager.get_latest_backup()
            if not backup_id:
                print("Error: No backups found and no backup-id specified")
                exit(1)
            print(f"Using latest backup: {backup_id}")
            
        success = manager.restore_database(backup_id, args.target_path)
        if success:
            print("Restore completed successfully")
        else:
            print("Restore failed")