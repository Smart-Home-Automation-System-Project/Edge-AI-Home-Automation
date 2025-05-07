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
    category TEXT,
    last_val TEXT,
    PRIMARY KEY (id, client_id)
)
""")

# Create the trigger
cursor.execute("""
CREATE TRIGGER update_last_val
AFTER INSERT ON sensor_data
FOR EACH ROW
BEGIN
    UPDATE sensors
    SET last_val = NEW.sensor_value
    WHERE id = NEW.sensor_id;
END
""")


print("Database and table created: database.db")
conn.commit()
conn.close()