import sqlite3
from datetime import datetime, timedelta
import random

# Mapping readable names to client IDs (must match insert_sample_sensor.py)
client_id_map = {
    'L1': "L-2025.04.19-21.09-0001",
    'L2': "L-2025.04.19-21.09-0002",
    'L3': "L-2025.04.19-21.09-0003",
    'L4': "L-2025.04.19-21.09-0004",
    'L5': "L-2025.04.19-21.09-0005",
    'L6': "L-2025.04.19-21.09-0006",
    'L7': "L-2025.04.19-21.09-0007",
    'L8': "L-2025.04.19-21.09-0008",
    'T1': "T-2025.04.19-21.09-0001",
    'T2': "T-2025.04.19-21.09-0002",
    'T3': "T-2025.04.19-21.09-0003",
    'T4': "T-2025.04.19-21.09-0004"
}


def get_sensor_ids():
    """Return mapping of logical sensor name (L1, T1...) to UUID from DB based on client_id"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    placeholders = ','.join('?' for _ in client_id_map.values())
    cursor.execute(f"""
        SELECT client_id, id FROM sensors
        WHERE client_id IN ({placeholders})
    """, list(client_id_map.values()))

    result = cursor.fetchall()
    conn.close()

    # Map readable names (L1, T1...) to sensor UUIDs
    reverse_lookup = {v: k for k, v in client_id_map.items()}
    return {reverse_lookup[client_id]: uuid for client_id, uuid in result}


def generate_sample_data(current_time, sensor_id_map):
    """Generate one timestamp worth of sensor data"""
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
    data_rows = []

    # Light sensors (0 to 3)
    for key in [f"L{i}" for i in range(1, 9)]:
        data_rows.append((sensor_id_map[key], timestamp, round(random.randint(0, 3), 2)))

    # Temp sensors (12 to 40 C)
    for key in [f"T{i}" for i in range(1, 5)]:
        data_rows.append((sensor_id_map[key], timestamp, round(random.uniform(12.0, 40.0), 2)))

    return data_rows


def insert_data_for_entire_week():
    sensor_ids = get_sensor_ids()

    if len(sensor_ids) < len(client_id_map):
        print(" ERROR: Some client IDs were not found in DB. Insert sample sensors first.")
        return

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    for day in range(7):
        for interval in range(96):  # 96 intervals per day
            timestamp = now - timedelta(minutes=15 * interval)
            data_rows = generate_sample_data(timestamp, sensor_ids)

            for row in data_rows:
                try:
                    cursor.execute('''
                        INSERT INTO sensor_data (sensor_id, timestamp, sensor_value)
                        VALUES (?, ?, ?)
                    ''', row)
                except sqlite3.IntegrityError:
                    continue

        now -= timedelta(days=1)

    conn.commit()
    conn.close()
    print(" Sensor data for past 7 days inserted.")


if __name__ == "__main__":
    insert_data_for_entire_week()
