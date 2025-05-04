"""
Database queries.
"""
import sqlite3
from threading import Lock
import uuid
import os
from datetime import datetime, timedelta
import pandas as pd

DB_NAME = os.path.join(os.path.dirname(__file__), "database.db")
db_lock = Lock()

# UI and sensor handling
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

def db_get_sensor_id_by_client_id(client_id):
    try:
        with db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id FROM sensors
                WHERE client_id = ?
            """, (client_id,))
            result = cursor.fetchone()

            if result:
                return result[0]  # UUID-based sensor ID
            else:
                return None  # Not found
    finally:
        try:
            conn.close()
        except:
            pass


#train.py
def db_get_sensor_types():
    """Get all sensors with their types from database"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, catagory
        FROM sensors
        WHERE name IS NOT NULL
    """)

    sensors = cursor.fetchall()
    conn.close()

    # Create mappings of sensor names to ids
    sensor_map = {row[1]: row[0] for row in sensors}
    sensor_categories = {row[0]: row[2] for row in sensors}

    return sensor_map, sensor_categories

def db_get_sensors_by_category(category):
    """Get all sensors of a specific category"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name
        FROM sensors
        WHERE catagory = ? AND name IS NOT NULL
    """, (category,))

    sensors = cursor.fetchall()
    conn.close()

    return {row[1]: row[0] for row in sensors}  # Map name to id

def db_get_sensor_data(sensor_id, days=7):
    """Get data for a specific sensor for the last X days"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    # Calculate date X days ago
    days_ago = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        SELECT timestamp, sensor_value
        FROM sensor_data
        WHERE sensor_id = ? AND timestamp >= ?
        ORDER BY timestamp
    """, (sensor_id, days_ago))

    data = cursor.fetchall()
    conn.close()

    return data

def db_get_all_sensor_data(days=7):
    """Get data for all sensors for the last X days"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    # Get all sensor IDs
    cursor.execute("""
        SELECT id, name, catagory
        FROM sensors
        WHERE name IS NOT NULL AND (catagory = 'light' OR catagory = 'temp')
    """)

    sensors = cursor.fetchall()

    # Calculate date X days ago
    days_ago = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

    # Create a dictionary to store data for each sensor
    sensor_data = {}

    for sensor_id, sensor_name, sensor_category in sensors:
        cursor.execute("""
            SELECT timestamp, sensor_value
            FROM sensor_data
            WHERE sensor_id = ? AND timestamp >= ?
            ORDER BY timestamp
        """, (sensor_id, days_ago))

        data = cursor.fetchall()
        sensor_data[sensor_name] = {'id': sensor_id, 'category': sensor_category, 'data': data}

    conn.close()

    return sensor_data


# predict.py
def db_get_sensor_data_for_prediction(days=1):
    """Get the last X days of sensor data for prediction in the format needed by predict.py"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    # Get light and temperature sensors
    cursor.execute("""
        SELECT id, name, catagory 
        FROM sensors 
        WHERE catagory IN ('light', 'temp') AND name IS NOT NULL
    """)
    sensors = cursor.fetchall()

    # Calculate timestamp for X days ago
    days_ago = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

    # Prepare data dictionary
    data_dict = {'timestamp': []}

    # Add column for each sensor
    for sensor_id, name, category in sensors:
        data_dict[name] = []

    # Get unique timestamps (sorted)
    cursor.execute("""
        SELECT DISTINCT timestamp 
        FROM sensor_data 
        WHERE timestamp >= ? 
        ORDER BY timestamp
    """, (days_ago,))

    timestamps = [row[0] for row in cursor.fetchall()]
    data_dict['timestamp'] = timestamps

    # For each timestamp, get sensor values
    for ts in timestamps:
        for sensor_id, name, category in sensors:
            cursor.execute("""
                SELECT sensor_value 
                FROM sensor_data 
                WHERE sensor_id = ? AND timestamp = ?
            """, (sensor_id, ts))

            result = cursor.fetchone()
            value = result[0] if result else None
            data_dict[name].append(value)

    conn.close()

    # Convert to DataFrame
    df = pd.DataFrame(data_dict)

    # Extract time features
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek

    return df

def db_get_light_and_temp_sensors():
    """Get the names of all light and temperature sensors"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    # Get light sensors
    cursor.execute("""
        SELECT name FROM sensors 
        WHERE catagory = 'light' AND name IS NOT NULL
    """)
    light_sensors = [row[0] for row in cursor.fetchall()]

    # Get temperature sensors
    cursor.execute("""
        SELECT name FROM sensors 
        WHERE catagory = 'temp' AND name IS NOT NULL
    """)
    temp_sensors = [row[0] for row in cursor.fetchall()]

    conn.close()

    return light_sensors, temp_sensors

def db_save_predicted_values(predictions_dict):
    """Save predicted values to database"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    # Get mapping of sensor names to IDs
    cursor.execute("""
        SELECT name, id FROM sensors 
        WHERE catagory IN ('light', 'temp') AND name IS NOT NULL
    """)
    name_to_id = {row[0]: row[1] for row in cursor.fetchall()}

    # Current timestamp for predictions
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save light predictions
    for light_name, value in predictions_dict['lights'].items():
        if light_name in name_to_id:
            sensor_id = name_to_id[light_name]
            cursor.execute("""
                INSERT OR REPLACE INTO sensor_data (sensor_id, timestamp, sensor_value)
                VALUES (?, ?, ?)
            """, (sensor_id, current_time, value))

    # Save temperature predictions
    for temp_name, value in predictions_dict['temperatures'].items():
        if temp_name in name_to_id:
            sensor_id = name_to_id[temp_name]
            cursor.execute("""
                INSERT OR REPLACE INTO sensor_data (sensor_id, timestamp, sensor_value)
                VALUES (?, ?, ?)
            """, (sensor_id, current_time, value))

    conn.commit()
    conn.close()


# predictions database table
def db_save_predictions(timestamp, predictions_dict):
    """Save predictions to database instead of CSV, removing all previous predictions"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    try:
        # First, delete all existing prediction records
        cursor.execute("DELETE FROM predictions")

        # Save light predictions
        for light_name, value in predictions_dict['lights'].items():
            cursor.execute("""
                INSERT INTO predictions (timestamp, sensor_name, predicted_value, category)
                VALUES (?, ?, ?, ?)
            """, (timestamp, light_name, value, 'light'))

        # Save temperature predictions
        for temp_name, value in predictions_dict['temperatures'].items():
            cursor.execute("""
                INSERT INTO predictions (timestamp, sensor_name, predicted_value, category)
                VALUES (?, ?, ?, ?)
            """, (timestamp, temp_name, value, 'temp'))

        conn.commit()
        print(f"Previous predictions cleared. New predictions saved to database for timestamp: {timestamp}")
    except sqlite3.Error as e:
        print(f"Error saving predictions to database: {e}")
    finally:
        conn.close()


# mqtt publish
def db_get_latest_prediction_rows():
    """Get the latest 20 prediction rows from the database"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, sensor_name, predicted_value 
        FROM predictions 
        ORDER BY timestamp DESC
        LIMIT 20
    """)

    prediction_rows = cursor.fetchall()
    conn.close()

    return prediction_rows

def db_get_radar_sensor_data():
    """Get latest radar sensor data from the database"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name, sd.sensor_value, sd.timestamp
        FROM sensor_data sd
        JOIN sensors s ON sd.sensor_id = s.id
        WHERE s.catagory = 'radar'
        ORDER BY sd.timestamp DESC
    """)

    radar_rows = cursor.fetchall()
    conn.close()

    return radar_rows

def db_get_light_sensor_names():
    """Get all light sensor names from the database"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sensors
        WHERE catagory = 'light' AND name IS NOT NULL
        ORDER BY name
    """)

    light_sensors = [row[0].lower() for row in cursor.fetchall()]
    conn.close()

    return light_sensors

def db_get_latest_predictions():
    """Get the most recent predictions from database"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Get the latest timestamp first
        cursor.execute("SELECT MAX(timestamp) as latest_time FROM predictions")
        latest_time = cursor.fetchone()['latest_time']

        if not latest_time:
            return None

        # Get all predictions for that timestamp
        cursor.execute("""
            SELECT sensor_name, predicted_value, category 
            FROM predictions 
            WHERE timestamp = ?
            ORDER BY category, sensor_name
        """, (latest_time,))

        results = {
            'lights': {},
            'temperatures': {},
            'timestamp': latest_time
        }

        for row in cursor.fetchall():
            if row['category'] == 'light':
                results['lights'][row['sensor_name']] = int(row['predicted_value'])
            elif row['category'] == 'temp':
                results['temperatures'][row['sensor_name']] = float(row['predicted_value'])

        return results
    finally:
        conn.close()

# export files
def db_get_light_and_temp_sensors_with_details():
    """Get all light and temperature sensors with their details"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, catagory 
        FROM sensors 
        WHERE catagory IN ('light', 'temp') AND name IS NOT NULL
        ORDER BY catagory, name
    """)

    sensors = cursor.fetchall()
    conn.close()

    return sensors

def db_get_recent_timestamps(limit=24):
    """Get the most recent distinct timestamps"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT timestamp 
        FROM sensor_data 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))

    timestamps = [row['timestamp'] for row in cursor.fetchall()]
    timestamps.reverse()  # Chronological order (oldest first)
    conn.close()

    return timestamps

def db_get_timestamps_since(days_ago):
    """Get all distinct timestamps from the past X days"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Calculate date X days ago
    days_ago_str = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        SELECT DISTINCT timestamp 
        FROM sensor_data 
        WHERE timestamp >= ?
        ORDER BY timestamp
    """, (days_ago_str,))

    timestamps = [row['timestamp'] for row in cursor.fetchall()]
    conn.close()

    return timestamps

def db_get_sensor_readings_for_timestamp(timestamp):
    """Get all sensor readings for a specific timestamp"""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name, sd.sensor_value, s.catagory
        FROM sensor_data sd
        JOIN sensors s ON sd.sensor_id = s.id
        WHERE sd.timestamp = ? AND s.catagory IN ('light', 'temp')
    """, (timestamp,))

    readings = cursor.fetchall()
    conn.close()

    return readings