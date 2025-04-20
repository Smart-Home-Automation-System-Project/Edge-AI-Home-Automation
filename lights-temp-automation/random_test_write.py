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
file_path = os.path.join(project_path, 'test.csv')


# Generate a random datetime within the past 30 days
def get_random_datetime():
    now = datetime.now()
    random_days = random.randint(0, 30)
    random_seconds = random.randint(0, 86400)  # number of seconds in a day
    random_timestamp = now - timedelta(days=random_days, seconds=random_seconds)
    return random_timestamp


def generate_test_data():
    rand_time = get_random_datetime()
    timestamp = rand_time.strftime('%Y-%m-%d %H:%M:%S')
    day_of_week = rand_time.weekday()  # 0 = Monday, 6 = Sunday
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


def write_data_to_csv():
    while True:
        test_data = generate_test_data()

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow([
                'timestamp', 'day_of_week', 'hour', 'l1', 'l2', 'l3', 't1', 't2', 't3'
            ])
            writer.writerow(test_data)
            print(f"Data written: {test_data}")

        time.sleep(5)  # Change to 30 for real intervals


if __name__ == "__main__":
    write_data_to_csv()
