"""
Database Tables
"""

import sqlite3

# Connect to the new database name
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create table named 'sensor_data' with a composite primary key
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    sensor_id TEXT,
    timestamp TEXT,
    sensor_value REAL,
    PRIMARY KEY (sensor_id, timestamp)
)
""")

# Create table named 'sensors'
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensors (
    id TEXT,
    client_id TEXT,
    name TEXT,
    catagory TEXT,
    last_val TEXT,
    PRIMARY KEY (id, client_id)
)
""")

# Create new table named 'predictions' to store predictions
cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    sensor_name TEXT NOT NULL,
    predicted_value REAL NOT NULL,
    category TEXT NOT NULL,
    UNIQUE(timestamp, sensor_name)
)
""")

conn.commit()
conn.close()
print("Database and table created: database.db")

"""
Sets up the last_val in 'sensors' table by running a trigger.
Triggers is run everytime new data is inserted
"""
from database import db_create_last_val_trigger

if __name__ == "__main__":
    db_create_last_val_trigger()