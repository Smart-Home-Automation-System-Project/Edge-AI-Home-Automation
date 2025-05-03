# database/export_train_csv.py
import sqlite3
import os
import datetime
import csv


def get_sensor_mappings():
    """Get mapping from sensor_id to name"""
    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sensor_mappings = {}
    cursor.execute("SELECT id, name, catagory FROM sensors")
    for row in cursor.fetchall():
        sensor_id = row['id']
        name = row['name']
        category = row['catagory']
        if category in ('light', 'temp'):
            sensor_mappings[sensor_id] = name

    conn.close()
    return sensor_mappings


def get_past_week_data():
    """Get all sensor data from the past 7 days"""
    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Calculate date 7 days ago
    seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

    # Get all distinct timestamps from the past 7 days, ordered by timestamp
    cursor.execute("""
        SELECT DISTINCT timestamp
        FROM sensor_data
        WHERE timestamp >= ?
        ORDER BY timestamp
    """, (seven_days_ago,))

    timestamps = [row['timestamp'] for row in cursor.fetchall()]

    # Get all sensor data for these timestamps
    data_by_timestamp = {}

    for ts in timestamps:
        cursor.execute("""
            SELECT sensor_id, sensor_value
            FROM sensor_data
            WHERE timestamp = ?
        """, (ts,))

        readings = {}
        for row in cursor.fetchall():
            readings[row['sensor_id']] = row['sensor_value']

        data_by_timestamp[ts] = readings

    conn.close()
    return data_by_timestamp, timestamps


def export_to_train_csv():
    # Get sensor ID to name mappings
    sensor_mappings = get_sensor_mappings()

    # Get all data from past week
    data_by_timestamp, timestamps = get_past_week_data()

    if not timestamps:
        print("No sensor data available for the past 7 days")
        return

    # Reverse mapping from name to ID for easier lookup
    name_to_id = {name: id for id, name in sensor_mappings.items()}

    # Create the train.csv file in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(project_root, "train.csv")

    # Define CSV columns
    fieldnames = ['timestamp', 'day_of_week', 'hour',
                  'l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8',
                  't1', 't2', 't3', 't4']

    # Prepare data for writing to CSV
    csv_rows = []

    for timestamp_str in timestamps:
        try:
            timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"Warning: Could not parse timestamp '{timestamp_str}', skipping this entry")
            continue

        day_of_week = timestamp.weekday()
        hour = timestamp.hour

        # Initialize row with time data
        row_data = {
            'timestamp': timestamp_str,
            'day_of_week': day_of_week,
            'hour': hour
        }

        # Add sensor values
        readings = data_by_timestamp[timestamp_str]

        # Process light sensors (l1-l8)
        for i in range(1, 9):
            sensor_name = f"l{i}"
            sensor_id = name_to_id.get(sensor_name)

            if sensor_id and sensor_id in readings:
                try:
                    row_data[sensor_name] = int(float(readings[sensor_id]))
                except (ValueError, TypeError):
                    row_data[sensor_name] = 0
            else:
                row_data[sensor_name] = 0

        # Process temperature sensors (t1-t4)
        for i in range(1, 5):
            sensor_name = f"t{i}"
            sensor_id = name_to_id.get(sensor_name)

            if sensor_id and sensor_id in readings:
                try:
                    row_data[sensor_name] = float(readings[sensor_id])
                except (ValueError, TypeError):
                    row_data[sensor_name] = 25.0
            else:
                row_data[sensor_name] = 25.0

        csv_rows.append(row_data)

    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Exported {len(csv_rows)} records to {output_file}")


if __name__ == "__main__":
    export_to_train_csv()