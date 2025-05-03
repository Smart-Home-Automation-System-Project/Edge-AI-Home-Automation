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

conn.commit()
conn.close()
print("Database and table created: database.db")
