# To enter 15-minute interval sensor data for the past 7 days to db

import sqlite3
from datetime import datetime, timedelta
import random


# Generate random sample data for a single timestamp
def generate_sample_data(current_time):
    sensors = {
        '101': ('l1', random.randint(0, 1)),
        '102': ('l2', random.randint(0, 1)),
        '103': ('l3', random.randint(0, 1)),
        '104': ('t1', round(random.uniform(12.0, 40.0), 2)),
        '105': ('t2', round(random.uniform(12.0, 40.0), 2)),
        '106': ('t3', round(random.uniform(12.0, 40.0), 2))
    }

    data_rows = []
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')

    for sensor_id, (name, value) in sensors.items():
        data_rows.append((sensor_id, timestamp, name, value))

    return data_rows


# Insert data for 7 days (15-minute intervals for each day)
def insert_data_for_entire_week():
    # Connect to the SQLite database
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()

    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    # Loop through 7 days (7 * 96 intervals = 672 entries)
    for day in range(7):  # 7 days
        for interval in range(96):  # 96 intervals per day (every 15 minutes)
            timestamp = now - timedelta(minutes=15 * interval)
            data_rows = generate_sample_data(timestamp)

            for data_row in data_rows:
                try:
                    cursor.execute('''
                    INSERT INTO sensor_data (sensor_id, timestamp, name, sensor_value)
                    VALUES (?, ?, ?, ?)
                    ''', data_row)
                except sqlite3.IntegrityError:
                    continue

        now -= timedelta(days=1)  # Adjust 'now' for the next day's timestamp

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("✅ 15-minute interval sensor data for the past 7 days inserted into the database.")


# Main function to control data insertion type
def main():
    insert_data_for_entire_week()  # Insert data for the entire week


if __name__ == "__main__":
    main()