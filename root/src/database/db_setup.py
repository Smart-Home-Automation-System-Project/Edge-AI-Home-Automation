import sqlite3

# Connect to the new database name
conn = sqlite3.connect("database1.db")
cursor = conn.cursor()

# Create table named 'sensor_data'
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    timestamp TEXT PRIMARY KEY,
    day_of_week INTEGER,
    hour INTEGER,
    l1 INTEGER,
    l2 INTEGER,
    l3 INTEGER,
    t1 REAL,
    t2 REAL,
    t3 REAL
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
print("Database and table created: database1.db")
