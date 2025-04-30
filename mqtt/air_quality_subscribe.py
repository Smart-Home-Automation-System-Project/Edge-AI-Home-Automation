import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

TOPICS = [
    "home/automation/co2_control",
    "home/automation/smoke_detection",
    "home/automation/gas_detection"
]


def on_message(client, userdata, msg):

    try:
        data = json.loads(msg.payload.decode('utf-8'))

        print(f"\n📡 Topic: {msg.topic}")
        print(f"Data: {json.dumps(data, indent=2)}")

        if msg.topic == "home/automation/gas_detection":

            if data.get("actions") and len(data["actions"]) > 0:
                print(f"Gas Leak detected!")
                print(f"Actions: {', '.join(data['actions'])}")

        elif msg.topic == "home/automation/co2_control":
            if data.get("fan") is not None:
                if data.get("fan"):
                    print(f"Fan turned ON due to high CO2 levels!")
                elif data.get("fan") is False:
                    print(f"CO2 levels are normal, turning OFF fan.")

        elif msg.topic == "home/automation/smoke_detection":
            if data.get("alarm", 0):
                print(f"Alarm triggered due to Fire Hazard!")

    except Exception as e:
        print(f" Error decoding message: {e}")

# MQTT Setup
client = mqtt.Client()
client.on_message = on_message

broker_ip = os.getenv("MQTT_BROKER")
if broker_ip:
    client.connect(broker_ip, 1883)

    for topic in TOPICS:
        client.subscribe(topic)
        print(f"Subscribed to: {topic}")

    client.loop_forever()
else:
    print("Error: MQTT_BROKER not set in .env")
