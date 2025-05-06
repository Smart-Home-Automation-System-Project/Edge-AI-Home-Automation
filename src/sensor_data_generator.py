"""
Sensor Data Generator – Inserts new sensor data for multiple timestamps every 5 seconds.
Simulates data received from sensors every 10 minutes.
Used to demonstrate how predictions change when the input to the model changes.
"""

import time
import os
import sys
import datetime
from threading import Thread

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import db_get_sensor_ids_by_category, db_insert_sensor_data_for_timestamp

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
        sensors_dict = db_get_sensor_ids_by_category()
        print(f"Found sensors: {sum(len(ids) for ids in sensors_dict.values())} total")

        cycle = 0
        while True:
            cycle += 1
            print(f"\n--- Cycle {cycle} ---")

            # Generate 12 timestamps
            timestamps = generate_timestamps(12, 5)

            # Insert data for each timestamp
            for timestamp in timestamps:
                db_insert_sensor_data_for_timestamp(timestamp, sensors_dict)

            print(f"Completed inserting {len(timestamps)} timestamps × {sum(len(ids) for ids in sensors_dict.values())} sensors")
            print(f"Sleeping for 5 seconds...")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping sensor data generator.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()