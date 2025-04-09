# This script queries data from the past 7 days from the SQLite database and saves in train.csv.
# It retrieves all records from the 'sensor_data' table where the timestamp is within the last 7 days.


import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Connect to DB
conn = sqlite3.connect('database1.db')

# Calculate 7-day window
now = datetime.now()
seven_days_ago = now - timedelta(days=7)

# Query past week's data
query = '''
SELECT * FROM sensor_data
WHERE timestamp >= ?
ORDER BY timestamp ASC
'''
df = pd.read_sql_query(query, conn, params=(seven_days_ago.strftime('%Y-%m-%d %H:%M:%S'),))

# Save as train.csv in the specified directory
df.to_csv(r'C:\Users\sahan\OneDrive\Desktop\Project\train.csv', index=False)

conn.close()
print("✅ Data from past 7 days exported to train.csv")
