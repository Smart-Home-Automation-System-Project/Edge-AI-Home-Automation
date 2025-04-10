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

# Query past week's data
query = '''
SELECT * FROM sensor_data
WHERE timestamp >= ?
ORDER BY timestamp ASC
'''
df = pd.read_sql_query(query, conn, params=(seven_days_ago.strftime('%Y-%m-%d %H:%M:%S'),))

# Save as train.csv in the specified directory
df.to_csv(csv_path, index=False)

conn.close()
print("✅ Data from past 7 days exported to train.csv")
