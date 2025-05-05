import json
from ..utils.mqtt import MQTTConnection
from ..utils.utils import get_localtime
from ..database.database import *
from ..sensor.topics import *
from ..utils.console import *

client = MQTTConnection.get_client()

def on_message(client, userdata, msg):
    try:
        if msg.topic == T_SENSOR_PUBLISH:
            sensor_publish_handler(client, userdata, msg)
        elif msg.topic == T_SENSOR_MAIN_CTRL:
            sensor_ctrl_handler(client, userdata, msg)
        else:
            print(f"Unhandled topic: {msg.topic}")
    except Exception as e:
        print("Error dispatching message:", e)

def sensor_publish_handler(client, userdata, msg):
    try:
        payload = str(msg.payload.decode())
        data = json.loads(payload)
        print(f"{BLUE} --> Received message from {msg.topic}: {data}{RESET}")

        data["time"] = get_localtime(data["time"])

        if data["data"] != "imOnline":
            if data["type"] == 'switch':
                pass
            if data["type"] == 'light':
                pass
            elif data["type"] == 'door':
                if data["data"] == "LOCK":
                    data["data"] = 1
                else:
                    data["data"] = 0
            
            db_add_sensor_data(data["time"], data["client_id"], data["data"])

        else:
            db_add_module(data["client_id"], None, data["type"])
            
    except json.JSONDecodeError as e:
        print("JSON decode failed:", e)
        print("Raw message:", msg.payload)
    except Exception as e:
        print("Unexpected error in on_message:", e)

def sensor_ctrl_handler(client, userdata, msg):
    try:
        payload = str(msg.payload.decode())
        data = json.loads(payload)
        id = data['id']
        cid = db_get_client_id(id)

        if 'irgb' in data:
            irgb = data['irgb']
            print(f"Command received. Setting client {cid} to color {irgb}.")
            client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'irgb': irgb}))
        elif 'state' in data:
            state = data['state']
            print(f"Command received. Setting client {cid} to state {state}.")
            client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'state': state}))
        else:
            pass
    
    except json.JSONDecodeError as e:
        print("JSON decode failed:", e)
        print("Raw message:", msg.payload)
    except Exception as e:
        print("Unexpected error in on_message:", e)



def init_modules():
    client.subscribe(T_SENSOR_PUBLISH)
    client.subscribe(T_SENSOR_MAIN_CTRL)
    client.on_message = on_message