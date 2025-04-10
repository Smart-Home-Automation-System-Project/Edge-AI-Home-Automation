# Laptop B (Publisher - Group 13)

import json
import pandas as pd
import paho.mqtt.client as mqtt

# === MQTT Setup ===
broker_ip = "192.168.1.22"  # IP of Broker
topic = "home/automation/predictions"
client = mqtt.Client()
client.connect(broker_ip, 1883)

# === Load predictions ===
predictions_path = r"C:\Users\sahan\OneDrive\Desktop\Project\predictions.csv"
df_preds = pd.read_csv(predictions_path)
preds = df_preds.iloc[0].to_dict()  # Take first row

# === Load radar sensor presence data ===
radar_path = r"C:\Users\sahan\OneDrive\Desktop\Project\radar_sensors.csv"
df_radar = pd.read_csv(radar_path)
radar = df_radar.iloc[0].to_dict()  # Get first (latest) radar data

# === Logic: Override OFF command if person is detected ===
adjusted_preds = {}
for i, light_key in enumerate(['l1', 'l2', 'l3']):
    radar_key = f'room{i+1}'
    light_value = int(preds[light_key])
    presence = int(radar[radar_key])

    # If model says OFF (0), but person is present, override to ON (1)
    if light_value == 0 and presence == 1:
        adjusted_preds[light_key] = 1
    else:
        adjusted_preds[light_key] = light_value

# Keep temperature predictions as is
adjusted_preds['t1'] = preds['t1']
adjusted_preds['t2'] = preds['t2']
adjusted_preds['t3'] = preds['t3']

# === Publish to MQTT ===
payload = json.dumps(adjusted_preds)
client.publish(topic, payload)
print(f"📤 Adjusted Prediction sent: {payload}")

client.disconnect()

# Radar	      Prediction (l1,l2,l3)	  Sent Value	      Reason
# Room1: 1	  l1 = 0	               1	              Model said off, but person detected
# Room2: 0	  l2 = 0	               0	              No person, model says off
# Room3: 1	  l3 = 1	               1	              Already ON, allowed
