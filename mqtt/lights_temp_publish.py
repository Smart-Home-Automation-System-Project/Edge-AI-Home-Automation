import json
import pandas as pd
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

# === Load predictions ===
predictions_path = os.path.join(os.getenv("PATH_TO_PROJECT"), 'predictions.csv')
df_preds = pd.read_csv(predictions_path)
preds = df_preds.iloc[0].to_dict()  # Take first row

# === Load radar sensor presence data ===
radar_path = os.path.join(os.getenv("PATH_TO_PROJECT"), 'radar_sensors.csv')
df_radar = pd.read_csv(radar_path)
radar = df_radar.iloc[0].to_dict()  # Get first (latest) radar data

# === Logic: Override OFF command if person is detected ===
adjusted_preds = {}
for i, light_key in enumerate(['l1', 'l2', 'l3','l4', 'l5', 'l6','l7', 'l8']):
    radar_key = f'room{i+1}'
    light_value = int(preds[light_key])
    presence = int(radar[radar_key])

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
adjusted_preds['t1'] = preds['t1']
adjusted_preds['t2'] = preds['t2']
adjusted_preds['t3'] = preds['t3']
adjusted_preds['t4'] = preds['t4']
# === Publish to MQTT ===
payload = json.dumps(adjusted_preds)
client.publish(topic, payload)
print(f"Prediction sent: {payload}")

client.disconnect()
