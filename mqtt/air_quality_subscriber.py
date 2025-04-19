import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import time
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Topics to subscribe to
TOPICS = [
    "home/automation/fan",       # CO2 control
    "home/automation/exhaust",   # Smoke and Gas ventilation
    "home/automation/alarm",     # Fire and Gas alarms
    "home/automation/email",     # Emergency notifications
    "home/automation/gas_appliance"  # Gas appliance control
]

def on_message(client, userdata, msg):
    """
    Callback function triggered when a message is received.
    Prints the topic, the message payload, and the retain value.
    """
    try:
        payload = msg.payload.decode('utf-8')
        print(f"Topic: {msg.topic}, Value: {payload}, Retain: {msg.retain}")
    except Exception as e:
        print(f"Error decoding message: {e}")

# MQTT client setup
client = mqtt.Client()
client.on_message = on_message

# Connect to the broker
broker_ip = os.getenv("MQTT_BROKER")
if broker_ip:
    client.connect(broker_ip, 1883)
    for topic in TOPICS:
        client.subscribe(topic)
        print(f"Subscribed to topic: {topic}")
    client.loop_forever()
else:
    print("⚠️ Error: MQTT_BROKER environment variable not set")
