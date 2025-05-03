import paho.mqtt.client as mqtt
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === MQTT Setup ===
broker_ip = os.getenv("MQTT_BROKER")  # IP of Broker (from .env)
topic = "home/automation/predictions"


def on_connect(client, userdata, flags, rc):
    print("Connected to broker.")
    client.subscribe(topic)
    print(f"Subscribed to topic: {topic}")


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"\nReceived prediction: {data}")

    # Simulate actuator behavior with brightness levels
    for i in range(1, 4):
        brightness_level = int(data[f"l{i}"])

        if brightness_level == 0:
            status = "OFF"
        elif brightness_level == 1:
            status = "LOW brightness"
        elif brightness_level == 2:
            status = "MEDIUM brightness"
        elif brightness_level == 3:
            status = "HIGH brightness"
        else:
            status = f"Unknown state: {brightness_level}"

        print(f"Light {i}: {status}")

    for i in range(1, 4):
        print(f" AC {i} set to: {data[f't{i}']}C")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_ip, 1883)
client.loop_forever()