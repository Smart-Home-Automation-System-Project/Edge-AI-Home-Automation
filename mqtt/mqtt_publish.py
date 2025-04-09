# Laptop B (Publisher - Group 13)

import json
import pandas as pd
import paho.mqtt.client as mqtt

# === MQTT Setup ===
broker_ip = "192.168.1.22"  # IP of Broker
topic = "home/automation/predictions"
client = mqtt.Client()
client.connect(broker_ip, 1883)

# === Load prediction from CSV (only first row) ===
predictions_path = r"C:\Users\sahan\OneDrive\Desktop\Project\predictions.csv"
df = pd.read_csv(predictions_path)

# Take the first row and convert to dictionary
first_prediction = df.iloc[0].to_dict()

# Convert to JSON and publish
payload = json.dumps(first_prediction)
client.publish(topic, payload)
print(f"📤 Prediction sent: {payload}")

client.disconnect()
