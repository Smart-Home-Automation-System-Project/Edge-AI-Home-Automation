import csv
import random
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve the project path from environment variable
project_path = os.getenv('PATH_TO_PROJECT')

# File paths
test_file_path = os.path.join(project_path, 'test.csv')
radar_file_path = os.path.join(project_path, 'radar_sensors.csv')


# Function to generate test.csv data
def generate_test_data(start_time):
    data_rows = []
    for i in range(24):  # 24 rows at 15-minute intervals = 6 hours of data
        rand_time = start_time + timedelta(minutes=15 * i)
        timestamp = rand_time.strftime('%Y-%m-%d %H:%M:%S')
        day_of_week = rand_time.weekday()
        hour = rand_time.hour

        row = [
            timestamp,
            day_of_week,
            hour,
            random.randint(0, 3),  # l1
            random.randint(0, 3),  # l2
            random.randint(0, 3),  # l3
            random.randint(0, 3),  # l4
            random.randint(0, 3),  # l5
            random.randint(0, 3),  # l6
            random.randint(0, 3),  # l7
            random.randint(0, 3),  # l8
            round(random.uniform(12.0, 40.0), 2),  # t1
            round(random.uniform(12.0, 40.0), 2),  # t2
            round(random.uniform(12.0, 40.0), 2),  # t3
            round(random.uniform(12.0, 40.0), 2),  # t4
        ]
        data_rows.append(row)
    return data_rows


# Function to generate radar_sensors.csv data
def generate_radar_data():
    return [random.randint(0, 1) for _ in range(8)]  # room1, room2,... room8


# Function to write both CSV files
def write_data_to_csv():
    while True:
        # === Generate a random future start time ===
        random_days_ahead = random.randint(1, 30)
        random_seconds = random.randint(0, 86400)
        start_time = datetime.now() + timedelta(days=random_days_ahead, seconds=random_seconds)

        # === Write test.csv with 24 rows ===
        test_data_rows = generate_test_data(start_time)

        with open(test_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'timestamp', 'day_of_week', 'hour', 'l1', 'l2', 'l3', 'l4', 'l5',
                'l6', 'l7', 'l8', 't1', 't2', 't3', 't4'
            ])
            writer.writerows(test_data_rows)
            print(f"[test.csv] 24 rows written starting from {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # === Write radar_sensors.csv ===
        radar_data = generate_radar_data()

        with open(radar_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['room1', 'room2', 'room3', 'room4', 'room5', 'room6', 'room7', 'room8'])
            writer.writerow(radar_data)
            print(f"[radar_sensors.csv] Data written: {radar_data}")

        time.sleep(5)  # Adjust this delay as needed


if __name__ == "__main__":
    write_data_to_csv()
