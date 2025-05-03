# database/export_test_to_csv.py
import os
import datetime
import csv
from datetime import timedelta
from database import (
    db_get_light_and_temp_sensors_with_details,
    db_get_recent_timestamps,
    db_get_sensor_readings_for_timestamp
)


def export_to_test_csv():
    """Export the most recent 24 records to test.csv"""
    # Get all light and temperature sensors with their names
    sensors = db_get_light_and_temp_sensors_with_details()

    light_sensors = [row['name'] for row in sensors if row['catagory'] == 'light']
    temp_sensors = [row['name'] for row in sensors if row['catagory'] == 'temp']

    # Get the 24 most recent distinct timestamps
    timestamps = db_get_recent_timestamps(24)

    if not timestamps:
        print("No sensor data available in the database")
        return

    # Create the output file path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(project_root, "test.csv")

    # Define CSV columns
    fieldnames = ['timestamp', 'day_of_week', 'hour']

    # Add all detected light and temp sensor names
    for sensor in light_sensors + temp_sensors:
        fieldnames.append(sensor)

    # Initialize rows for CSV
    csv_rows = []

    # Get all sensor data for the timestamps we need
    for timestamp_str in timestamps:
        try:
            # Parse timestamp for day_of_week and hour
            timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

            # Initialize row with time data
            row_data = {
                'timestamp': timestamp_str,
                'day_of_week': timestamp.weekday(),
                'hour': timestamp.hour
            }

            # Initialize all sensor values with defaults
            for sensor in light_sensors:
                row_data[sensor] = 0
            for sensor in temp_sensors:
                row_data[sensor] = 25.0

            # Get all sensor readings for this timestamp
            readings = db_get_sensor_readings_for_timestamp(timestamp_str)

            # Fill in actual sensor values
            for reading in readings:
                sensor_name = reading['name']
                sensor_value = reading['sensor_value']
                category = reading['catagory']

                if sensor_name in row_data:
                    if category == 'light':
                        try:
                            row_data[sensor_name] = int(float(sensor_value))
                        except (ValueError, TypeError):
                            pass  # Keep default if conversion fails
                    else:  # temperature
                        try:
                            row_data[sensor_name] = float(sensor_value)
                        except (ValueError, TypeError):
                            pass  # Keep default if conversion fails

            csv_rows.append(row_data)

        except ValueError:
            print(f"Warning: Could not parse timestamp '{timestamp_str}', skipping this entry")
            continue

    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Exported {len(csv_rows)} most recent records to {output_file}")


if __name__ == "__main__":
    export_to_test_csv()