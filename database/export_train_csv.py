import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch the project path from the environment variables
project_path = os.getenv("PATH_TO_PROJECT")

# === ONLY CHANGE ABSOLUTE PATHS ===
# Absolute paths
csv_path = os.path.join(project_path, 'train.csv')

# Connect to DB
conn = sqlite3.connect('database1.db')

# Calculate 7-day window
now = datetime.now()
seven_days_ago = now - timedelta(days=7)

# Query past week's data from the new database structure
query = '''
SELECT sensor_id, timestamp, sensor_value
FROM sensor_data
WHERE timestamp >= ?
ORDER BY timestamp ASC
'''

df = pd.read_sql_query(query, conn, params=(seven_days_ago.strftime('%Y-%m-%d %H:%M:%S'),))

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

# Convert to the required format
# First, pivot the data to get each sensor in its own column
pivot_df = df.pivot_table(
    index='timestamp',
    columns='sensor_name',
    values='sensor_value',
    aggfunc='first'  # In case of duplicates, take the first value
).reset_index()

# Add calculated columns for day_of_week and hour
pivot_df['day_of_week'] = pd.to_datetime(pivot_df['timestamp']).dt.dayofweek
pivot_df['hour'] = pd.to_datetime(pivot_df['timestamp']).dt.hour

# Reorder columns to match the desired format
final_df = pivot_df[['timestamp', 'day_of_week', 'hour', 'l1', 'l2', 'l3','l4', 'l5', 'l6','l7', 'l8','t1', 't2', 't3','t4']]

# Save as train.csv in the specified directory
final_df.to_csv(csv_path, index=False, float_format='%.2f')

conn.close()
print("Data from past 7 days exported to train.csv")