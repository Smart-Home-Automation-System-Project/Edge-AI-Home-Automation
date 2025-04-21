import json
from utils.mqtt import MQTTConnection
from utils.utils import get_localtime
from database.database import *


client = MQTTConnection.get_client()

def on_message(client, userdata, msg):
    try:
        payload = str(msg.payload.decode())
        data = json.loads(payload)
        data["time"] = get_localtime(data["time"])
        if data["data"] != "imOnline":
            print(f"Received message from {msg.topic}: {data}")
            #add_sensor_data();  // TODO : fix database

    except json.JSONDecodeError as e:
        print("JSON decode failed:", e)
        print("Raw message:", msg.payload)
    except Exception as e:
        print("Unexpected error in on_message:", e)

def load_modules():
    pass

def init_modules():
    topic = "sensor/publish"
    load_modules()
    client.subscribe(topic)
    client.on_message = on_message