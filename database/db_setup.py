import sqlite3

# Connect to the new database name
conn = sqlite3.connect("database1.db")
cursor = conn.cursor()

# Create table named 'sensor_data' with a composite primary key
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    sensor_id TEXT,
    timestamp TEXT,
    name TEXT,
    sensor_value REAL,
    PRIMARY KEY (sensor_id, timestamp)
)
""")

conn.commit()
conn.close()
print("✅ Database and table created: database1.db / sensor_data")