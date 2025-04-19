import os
import csv
import random
import time
from datetime import datetime

# Write to this file path, random sensor data
csv_file_path = os.path.join(os.path.dirname(__file__), '../air.csv')

def generate_random_sensor_data():
    """Generate random sensor data based on the structure of air.csv."""
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    co2_level = random.randint(400, 1500)
    smoke_density = random.randint(10, 150)
    co_level = random.randint(5, 75)
    gas_level = random.randint(30, 350)
    return [date, time_str, co2_level, smoke_density, co_level, gas_level]

def write_sensor_data_to_csv(file_path):
    """Append random sensor data to the CSV file."""
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(generate_random_sensor_data())

if __name__ == "__main__":
    while True:
        write_sensor_data_to_csv(csv_file_path)
        time.sleep(10)