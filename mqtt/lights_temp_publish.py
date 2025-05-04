import json
import sqlite3
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === MQTT Setup ===
broker_ip = os.getenv("MQTT_BROKER")  # IP of Broker (from .env)
topic = "home/automation/predictions"
client = mqtt.Client()
client.connect(broker_ip, 1883)

# === Database connection ===
DB_NAME = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "database.db")
conn = sqlite3.connect(DB_NAME)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# === Get latest predictions from database ===
cursor.execute("""
    SELECT timestamp, sensor_name, predicted_value 
    FROM predictions 
    ORDER BY timestamp DESC
    LIMIT 20
""")
prediction_rows = cursor.fetchall()
latest_timestamp = prediction_rows[0]['timestamp'] if prediction_rows else None

# Create prediction dictionary
preds = {}
for row in prediction_rows:
    if row['timestamp'] == latest_timestamp:  # Only use the most recent predictions
        sensor_name = row['sensor_name'].lower()  # Convert to lowercase for consistency
        preds[sensor_name] = row['predicted_value']

# === Get latest radar sensor data ===
cursor.execute("""
    SELECT s.name, sd.sensor_value 
    FROM sensor_data sd
    JOIN sensors s ON sd.sensor_id = s.id
    WHERE s.catagory = 'radar'
    ORDER BY sd.timestamp DESC
""")
radar_rows = cursor.fetchall()

# Get the most recent timestamp for radar data
latest_radar_timestamp = None
for row in radar_rows:
    if latest_radar_timestamp is None:
        latest_radar_timestamp = row['timestamp']
    elif row['timestamp'] != latest_radar_timestamp:
        break

# Create radar dictionary
radar = {}
for i in range(1, 9):  # Assuming 8 radar sensors
    radar[f'room{i}'] = 0  # Default value if no data exists

# Fill in actual values
for row in radar_rows:
    if row['timestamp'] == latest_radar_timestamp:
        # Extract the number from radar name (e.g., "R1" -> "1")
        radar_num = row['name'].lower().replace('r', '')
        radar[f'room{radar_num}'] = int(row['sensor_value'])

# === Logic: Override OFF command if person is detected ===
adjusted_preds = {}
for i, light_key in enumerate(['l1', 'l2', 'l3','l4', 'l5', 'l6','l7', 'l8']):
    radar_key = f'room{i+1}'
    light_value = int(preds.get(light_key, 0))
    presence = int(radar.get(radar_key, 0))

    if light_key in ['l5', 'l6']:
        # For l5 and l6: Turn on if person is present, but never turn off due to absence
        if light_value == 0 and presence == 1:
            # If model says OFF but person is present, override to ON
            adjusted_preds[light_key] = 2
        else:
            # Otherwise keep model prediction (don't turn off if no presence)
            adjusted_preds[light_key] = light_value
    else:
        # For other lights: standard presence logic
        if light_value == 0 and presence == 1:
            # If model says OFF but person is present, override to ON
            adjusted_preds[light_key] = 2
        elif light_value in [1, 2, 3] and presence == 0:
            # If model says ON but no person present, override to OFF
            adjusted_preds[light_key] = 0
        else:
            adjusted_preds[light_key] = light_value

# Keep temperature predictions as is
for i in range(1, 5):
    temp_key = f't{i}'
    adjusted_preds[temp_key] = preds.get(temp_key, 20.0)  # Default to 20 if not found

# Close database connection
conn.close()

# === Publish to MQTT ===
payload = json.dumps(adjusted_preds)
client.publish(topic, payload)
print(f"Prediction sent: {payload}")

client.disconnect()