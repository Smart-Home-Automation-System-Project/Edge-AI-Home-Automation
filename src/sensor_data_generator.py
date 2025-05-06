"""
Sensor Data Generator – Inserts new sensor data for multiple timestamps every 5 seconds.
Simulates data received from sensors every 10 minutes.
Used to demonstrate how predictions change when the input to the model changes.
"""

import sqlite3
import time
import random
import os
import sys
import datetime
from threading import Thread

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import DB_NAME, db_get_light_and_temp_sensors

def generate_random_sensor_value(sensor_type):
    """Generate random sensor values based on sensor type"""
    if sensor_type == 'light':
        return random.randint(0, 3)
    elif sensor_type == 'temp':
        return round(random.uniform(18.0, 26.0), 2)
    elif sensor_type == 'radar':
        return random.randint(0, 1)  # 0 for no motion, 1 for motion detected
    else:
        return 0

def get_sensor_ids_by_category():
    """Get all sensor IDs grouped by category"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, catagory 
        FROM sensors 
        WHERE catagory IN ('light', 'temp', 'radar')
    """)

    results = cursor.fetchall()
    conn.close()

    # Group by category
    sensors = {'light': [], 'temp': [], 'radar': []}
    for sensor_id, category in results:
        sensors[category].append(sensor_id)

    return sensors

def insert_sensor_data_for_timestamp(timestamp, sensors_dict):
    """Insert data for all sensors for a specific timestamp"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # Insert data for each sensor category
        for category, sensor_ids in sensors_dict.items():
            for sensor_id in sensor_ids:
                value = generate_random_sensor_value(category)
                cursor.execute("""
                    INSERT OR REPLACE INTO sensor_data (sensor_id, timestamp, sensor_value)
                    VALUES (?, ?, ?)
                """, (sensor_id, timestamp, value))

        conn.commit()
        print(f"Inserted data for timestamp: {timestamp}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def generate_timestamps(num_timestamps=12, interval_minutes=5):
    """Generate a list of timestamps at specified intervals"""
    timestamps = []
    now = datetime.datetime.now()

    # Generate timestamps in the past
    for i in range(num_timestamps):
        # Calculate time delta (starting with the oldest)
        delta_minutes = (num_timestamps - 1 - i) * interval_minutes
        timestamp = now - datetime.timedelta(minutes=delta_minutes)
        timestamps.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

    return timestamps

def main():
    print("Starting sensor data generator...")

    try:
        # Get sensor IDs by category
        sensors_dict = get_sensor_ids_by_category()
        print(f"Found sensors: {sum(len(ids) for ids in sensors_dict.values())} total")

        cycle = 0
        while True:
            cycle += 1
            print(f"\n--- Cycle {cycle} ---")

            # Generate 12 timestamps
            timestamps = generate_timestamps(12, 5)

            # Insert data for each timestamp
            for timestamp in timestamps:
                insert_sensor_data_for_timestamp(timestamp, sensors_dict)

            print(f"Completed inserting {len(timestamps)} timestamps × {sum(len(ids) for ids in sensors_dict.values())} sensors")
            print(f"Sleeping for 5 seconds...")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping sensor data generator.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()