# To enter 15-minute interval sensor data for the past 7 days to db

import sqlite3
from datetime import datetime, timedelta
import random


# Generate random sample data
def generate_sample_data(current_time):
    return (
        current_time.strftime('%Y-%m-%d %H:%M:%S'),  # timestamp
        current_time.weekday(),  # day_of_week
        current_time.hour,  # hour
        random.randint(0, 1),  # l1
        random.randint(0, 1),  # l2
        random.randint(0, 1),  # l3
        round(random.uniform(12.0, 40.0), 2),  # t1
        round(random.uniform(12.0, 40.0), 2),  # t2
        round(random.uniform(12.0, 40.0), 2)  # t3
    )


# Insert data for 7 days (15-minute intervals for each day)
def insert_data_for_entire_week():
    # Connect to the SQLite database
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()

    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    # Loop through 7 days (7 * 96 intervals = 672 entries)
    for _ in range(7):  # 7 days
        for i in range(96):  # 96 intervals per day (every 15 minutes)
            timestamp = now - timedelta(minutes=15 * i)
            data = generate_sample_data(timestamp)
            try:
                cursor.execute('''
                INSERT INTO sensor_data (timestamp, day_of_week, hour, l1, l2, l3, t1, t2, t3)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)
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
