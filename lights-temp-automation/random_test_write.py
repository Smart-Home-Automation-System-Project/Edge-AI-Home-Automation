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


# Generate a random datetime within the past 30 days
def get_random_datetime():
    now = datetime.now()
    random_days = random.randint(0, 30)
    random_seconds = random.randint(0, 86400)
    random_timestamp = now - timedelta(days=random_days, seconds=random_seconds)
    return random_timestamp


# Function to generate test.csv data
def generate_test_data():
    rand_time = get_random_datetime()
    timestamp = rand_time.strftime('%Y-%m-%d %H:%M:%S')
    day_of_week = rand_time.weekday()
    hour = rand_time.hour

    return [
        timestamp,
        day_of_week,
        hour,
        random.randint(0, 1),  # l1
        random.randint(0, 1),  # l2
        random.randint(0, 1),  # l3
        round(random.uniform(12.0, 40.0), 2),  # t1
        round(random.uniform(12.0, 40.0), 2),  # t2
        round(random.uniform(12.0, 40.0), 2)   # t3
    ]


# Function to generate radar_sensors.csv data
def generate_radar_data():
    return [random.randint(0, 1) for _ in range(3)]  # room1, room2, room3


# Function to write both CSV files
def write_data_to_csv():
    while True:
        # === Write test.csv ===
        test_data = generate_test_data()

        with open(test_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'timestamp', 'day_of_week', 'hour', 'l1', 'l2', 'l3', 't1', 't2', 't3'
            ])
            writer.writerow(test_data)
            print(f"[test.csv] Data written: {test_data}")

        # === Write radar_sensors.csv ===
        radar_data = generate_radar_data()

        with open(radar_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['room1', 'room2', 'room3'])
            writer.writerow(radar_data)
            print(f"[radar_sensors.csv] Data written: {radar_data}")

        time.sleep(5)  # Change to 30 for production use


if __name__ == "__main__":
    write_data_to_csv()
