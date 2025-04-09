# Laptop C (Subscriber - Simulated Actuators)

import paho.mqtt.client as mqtt
import json

broker_ip = "192.168.1.22"  # IP of Broker
topic = "home/automation/predictions"

def on_connect(client, userdata, flags, rc):
    print("✅ Connected to broker.")
    client.subscribe(topic)
    print(f"📡 Subscribed to topic: {topic}")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"\n📥 Received prediction: {data}")

    # Simulate actuator behavior
    for i in range(1, 4):
        light = "ON" if data[f"l{i}"] == 1 else "OFF"
        print(f"💡 Light {i}: {light}")

    for i in range(1, 4):
        print(f"🌡️ Thermostat {i} set to: {data[f't{i}']}°C")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_ip, 1883)
client.loop_forever()
