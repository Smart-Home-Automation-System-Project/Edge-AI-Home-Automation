import os
import csv
import random
import time
from datetime import datetime

# Write to this file path, random sensor data
csv_file_path = os.path.join(os.path.dirname(__file__), '../air.csv')

# Flag to toggle between random and fixed data
USE_FIXED_VALUES = True  # Set to True to use fixed rows instead of random data

# Fixed set of rows for testing (to showcase specific features)
fixed_data_rows = [
    # 1st Scenario: CO2 high
    ['2025-03-28', '15:09:31', 1500, 60, 45, 20],

    # 2nd Scenario: CO2 goes below the level and fan off
    ['2025-03-28', '15:09:41', 700, 55, 30, 20],

    # 3rd Scenario: Cooking smoke detected
    ['2025-03-28', '15:09:51', 900, 80, 44, 70],

    # 4th Scenario: Fire hazards
    ['2025-03-28', '15:10:01', 900, 140, 85, 50],

    # 5th Scenario: Gas leak
    ['2025-03-28', '15:10:11', 900, 30, 10, 350],

]

def generate_random_sensor_data():
    """Generate random sensor data based on the structure of air.csv."""
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    co2_level = random.randint(400, 1500)  # Random CO2 level
    smoke_density = random.randint(10, 150)  # Random smoke density
    co_level = random.randint(5, 75)  # Random CO level
    gas_level = random.randint(30, 350)  # Random gas level
    return [date, time_str, co2_level, smoke_density, co_level, gas_level]

def write_sensor_data_to_csv(file_path, data):
    """Append sensor data (either random or fixed) to the CSV file and print the written data."""
    # Write to the CSV file
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

    # Print the data that was written to the terminal
    print(f"[air.csv] Data written: {data}")

if __name__ == "__main__":
    # Ensure header is written to file only once
    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['date', 'time', 'CO2_level', 'smoke_density', 'co_level', 'gas_level'])

    # Start with the fixed data index
    fixed_data_index = 0

    while True:
        if USE_FIXED_VALUES:
            # Use the fixed data rows for demonstration purposes
            sensor_data = fixed_data_rows[fixed_data_index]
            # Increment the index to move to the next scenario
            fixed_data_index = (fixed_data_index + 1) % len(fixed_data_rows)  # Loop back to start after the last row
        else:
            # Use random sensor data
            sensor_data = generate_random_sensor_data()

        # Write data to the CSV file
        write_sensor_data_to_csv(csv_file_path, sensor_data)

        # Wait for 10 seconds before adding new data
        time.sleep(10)
