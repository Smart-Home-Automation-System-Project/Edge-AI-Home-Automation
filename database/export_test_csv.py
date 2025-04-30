import os
import sqlite3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch the project path from the environment variables
project_path = os.getenv("PATH_TO_PROJECT")

# === ONLY CHANGE ABSOLUTE PATHS ===
# Absolute paths
csv_path = os.path.join(project_path, 'test.csv')

# Function to get the latest data from the sensor_data table
def get_latest_data_from_db():
    conn = sqlite3.connect('database1.db')

    # First get the most recent timestamp
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(timestamp) FROM sensor_data')
    latest_timestamp = cursor.fetchone()[0]

    if not latest_timestamp:
        conn.close()
        return None

    # Query all sensors for this timestamp
    query = '''
    SELECT sensor_id, timestamp, sensor_value
    FROM sensor_data
    WHERE timestamp = ?
    '''

    df = pd.read_sql_query(query, conn, params=(latest_timestamp,))
    conn.close()

    if df.empty:
        return None

    # Create a mapping of sensor_id to sensor name
    sensor_map = {
        '101': 'l1',
        '102': 'l2',
        '103': 'l3',
        '104': 'l4',
        '105': 'l5',
        '106': 'l6',
        '107': 'l7',
        '108': 'l8',
        '201': 't1',
        '202': 't2',
        '203': 't3',
        '204': 't4'
    }

    # Add sensor name column based on sensor_id
    df['sensor_name'] = df['sensor_id'].map(sensor_map)

    # Process the data into the required format
    pivot_df = df.pivot(index='timestamp', columns='sensor_name', values='sensor_value').reset_index()

    # Add day_of_week and hour
    timestamp_dt = pd.to_datetime(pivot_df['timestamp'].iloc[0])
    pivot_df['day_of_week'] = timestamp_dt.dayofweek
    pivot_df['hour'] = timestamp_dt.hour

    # Ensure all required columns exist
    for col in ['l1', 'l2', 'l3','l4', 'l5', 'l6','l7','l8','t1', 't2', 't3','l4']:
        if col not in pivot_df.columns:
            pivot_df[col] = None

    # Reorder columns
    result_df = pivot_df[['timestamp', 'day_of_week', 'hour', 'l1', 'l2', 'l3','l4', 'l5', 'l6','l7','l8','t1', 't2', 't3','l4']]

    return result_df

# Function to save the data to a CSV file
def save_to_csv(df):
    df.to_csv(csv_path, index=False, float_format='%.2f')
    print("Latest data saved to test.csv")

# Main execution
if __name__ == "__main__":
    # Get the latest data from the database
    latest_data = get_latest_data_from_db()

    if latest_data is not None and not latest_data.empty:
        # Save the latest data to test.csv
        save_to_csv(latest_data)
    else:
        print("No data found in the database.")