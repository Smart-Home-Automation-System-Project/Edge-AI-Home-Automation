import csv
import random
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve the project path from environment variable
project_path = os.getenv('PATH_TO_PROJECT')

# Define the file path using the loaded environment variable
file_path = os.path.join(project_path, 'test.csv')


# Function to generate random test data
def generate_test_data():
    return [
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # timestamp
        random.randint(0, 6),  # day_of_week (0=Monday, 6=Sunday)
        random.randint(0, 23),  # hour (0-23)
        random.randint(0, 1),  # l1 (light 1 status)
        random.randint(0, 1),  # l2 (light 2 status)
        random.randint(0, 1),  # l3 (light 3 status)
        round(random.uniform(12.0, 40.0), 2),  # t1 (temperature 1)
        round(random.uniform(12.0, 40.0), 2),  # t2 (temperature 2)
        round(random.uniform(12.0, 40.0), 2)  # t3 (temperature 3)
    ]


# Function to overwrite the existing CSV with random test data every 30 seconds
def write_data_to_csv():
    while True:
        # Generate random test data
        test_data = generate_test_data()

        # Open the file in write mode to overwrite the existing file
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the header every time the file is overwritten
            writer.writerow([
                'timestamp', 'day_of_week', 'hour', 'l1', 'l2', 'l3', 't1', 't2', 't3'
            ])

            # Write the generated data to the file
            writer.writerow(test_data)
            print(f"Data written: {test_data}")

        # Wait for 30 seconds before generating the next entry
        time.sleep(5)


# Main execution
if __name__ == "__main__":
    write_data_to_csv()
