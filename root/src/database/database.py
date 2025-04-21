import sqlite3
from threading import Lock
import uuid
import os

DB_NAME = os.path.join(os.path.dirname(__file__), "database.db")
db_lock = Lock()

def db_add_module(client_id, name, category):
    try:
        with db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL;")

            cursor = conn.cursor()

            # Check if client_id already exists
            cursor.execute("SELECT id FROM sensors WHERE client_id = ?", (client_id,))
            existing = cursor.fetchone()

            if existing:
                print(f"Client ID already exists in database: {client_id} (Sensor ID: {existing[0]})")
                return  # Exit early, no insertion
            
            sensor_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO sensors (id, client_id, name, catagory, last_val)
                VALUES (?, ?, ?, ?, ?)
            """, (sensor_id, client_id, name, category, None))
            conn.commit()
            print(f"Sensor added: {sensor_id} - {name}")
    except sqlite3.IntegrityError:
        print(f"Sensor ID already exists: {sensor_id}")
    finally:
        try:
            conn.close()
        except:
            pass

def db_get_available_all_modules():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, client_id, name, catagory, last_val
        FROM sensors
        WHERE name IS NOT NULL
    """)
    rows = cursor.fetchall()
    conn.close()
    modules = [
        {"id": r[0], "client_id": r[1], "name": r[2], "category": r[3], "last_val": r[4]} for r in rows
    ]
    return modules

def db_get_new_modules():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, client_id, name, catagory, last_val
        FROM sensors
        WHERE name IS NULL
    """)
    rows = cursor.fetchall()
    conn.close()
    modules = [
        {"id": r[0], "client_id": r[1], "name": r[2], "category": r[3], "last_val": r[4]} for r in rows
    ]
    return modules

def db_assign_module(client_id, new_name):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sensors
        SET name = ?
        WHERE client_id = ?
    """, (new_name, client_id))
    
    # Commit the changes and close the connection
    conn.commit()
    # Check how many rows were affected (useful for error handling)
    rows_affected = cursor.rowcount
    conn.close()

    # Return the number of rows affected
    return rows_affected

def db_replace_module(id, new_client_id):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM sensors
        WHERE client_id = ? AND name IS NULL
    """, (new_client_id,))

    cursor.execute("""
        UPDATE sensors
        SET client_id = ?
        WHERE id = ?
    """, (new_client_id, id))


    
    # Commit the changes and close the connection
    conn.commit()
    # Check how many rows were affected (useful for error handling)
    rows_affected = cursor.rowcount
    conn.close()

    # Return the number of rows affected
    return rows_affected

def db_delete_module(id):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM sensors
        WHERE id = ? AND catagory != 'sensor' AND catagory != 'door'
    """, (id,))

    
    # Commit the changes and close the connection
    conn.commit()
    # Check how many rows were affected (useful for error handling)
    rows_affected = cursor.rowcount
    conn.close()

    # Return the number of rows affected
    return rows_affected



def db_add_sensor_data(timestamp, client_id, data):
    try:
        with db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sensors
                SET last_val = ?
                WHERE client_id = ?
            """, (data, client_id))
            conn.commit()
            print(f"Data added for timestamp: {timestamp}")
    except sqlite3.IntegrityError:
        print(f"Timestamp already exists: {timestamp}")
    finally:
        try:
            conn.close()
        except:
            pass

def db_get_client_id(id):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT client_id FROM sensors
        WHERE id = ? AND catagory != 'sensor'
    """, (id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]  # Return client_id
    else:
        return None  # Not found or is a 'sensor'

def db_add_sensor(client_id, name, category):
    try:
        with db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL;")

            cursor = conn.cursor()
            sensor_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO sensors (id, client_id, name, catagory, last_val)
                VALUES (?, ?, ?, ?, ?)
            """, (sensor_id, client_id, name, category, None))
            conn.commit()
            print(f"Sensor added: {sensor_id} - {name}")
    except sqlite3.IntegrityError:
        print(f"Sensor ID already exists: {sensor_id}")
    finally:
        try:
            conn.close()
        except:
            pass

