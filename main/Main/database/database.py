import sqlite3
from threading import Lock
import uuid
import os
from flask import jsonify

DB_NAME = os.path.join(os.path.dirname(__file__), "database1.db")
db_lock = Lock()

def add_sensor(client_id, name, category):
    try:
        with db_lock:
            conn = sqlite3.connect(DB_NAME)
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


def remove_sensor(sensor_id):
    try:
        with db_lock:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sensors WHERE id = ?", (sensor_id,))
            conn.commit()
            if cursor.rowcount:
                print(f"Sensor removed: {sensor_id}")
            else:
                print(f"Sensor not found: {sensor_id}")
    finally:
        try:
            conn.close()
        except:
            pass


def add_sensor_data(timestamp, day_of_week, hour, l1, l2, l3, t1, t2, t3):
    try:
        with db_lock:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sensor_data (timestamp, day_of_week, hour, l1, l2, l3, t1, t2, t3)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, day_of_week, hour, l1, l2, l3, t1, t2, t3))
            conn.commit()
            print(f"Data added for timestamp: {timestamp}")
    except sqlite3.IntegrityError:
        print(f"Timestamp already exists: {timestamp}")
    finally:
        try:
            conn.close()
        except:
            pass


def get_all_modules():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, catagory, last_val FROM sensors")
    rows = cursor.fetchall()
    conn.close()
    modules = [
        {"id": r[0], "name": r[1], "category": r[2], "last_val": r[3]} for r in rows
    ]
    return modules