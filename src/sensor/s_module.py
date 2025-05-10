import json
from utils.mqtt import MQTTConnection
from utils.utils import get_localtime
from database.database import *
from sensor.topics import *
from utils.console import *
import time

client = MQTTConnection.get_client()

light_power_data = {}

def on_message(client, userdata, msg):
    print(f"{GREEN} TOPIC : {msg.topic}, MSG : {msg.payload.decode()}")
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
        id = db_get_id(data["client_id"])

        if data["data"] != "imOnline":
            if data["type"] == 'switch':
                pass
            elif data["type"] == 'light':
                modules = db_get_available_all_modules()
                for mod in modules:
                    if mod['category'] == 'temp' or mod['category'] == 'light':
                        if mod['id'] == id:
                            db_add_sensor_data(data["time"], mod['id'], data["data"])
                        else:
                            db_add_sensor_data(data["time"], mod['id'], mod["last_val"])
                light_power_data[data["client_id"]] = data["power"]
                return

            elif data["type"] == 'radar':
                pass
            elif data["type"] == 'temp':
                modules = db_get_available_all_modules()
                for mod in modules:
                    if mod['category'] == 'temp' or mod['category'] == 'light':
                        if mod['id'] == id:
                            db_add_sensor_data(data["time"], mod['id'], data["data"])
                        else:
                            db_add_sensor_data(data["time"], mod['id'], mod["last_val"])
                return
            elif data["type"] == 'door':
                if data["data"] == "LOCK":
                    data["data"] = 1
                else:
                    data["data"] = 0
            
            db_add_sensor_data(data["time"], id, data["data"])
        else:
            if data["type"] == 'light':
                light_power_data[data["client_id"]] = 0
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
        name = data['name']
        if "ALL" not in name:
        # Single Mode
            cid = db_get_client_id(name)
            mod_type = db_get_module_type(cid)
            
            if mod_type == 'door':
                state = data['state']
                client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'state': state}))
                print(f"Command received. Setting client {cid} to state {state}.")
            elif mod_type == 'light':
                if 'irgb' in data:
                    irgb = data['irgb']
                    print(f"Command received. Setting client {cid} to color {irgb}.")
                    client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'irgb': irgb}))
                elif 'state' in data:
                    state = data['state']
                    print(f"Command received. Setting client {cid} to state {state}.")
                    client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'state': state}))
            elif mod_type == 'switch':
                state = data['state']
                print(f"Command received. Setting client {cid} to state {state}.")
                client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'state': state}))
            elif mod_type == 'temp':
                value = data['value']
                print(f"Command received. Setting client {cid} to value {value}C.")
                client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'value': value}))
        # Batch Mode
        else:
            modules = db_get_available_all_modules()
            if 'SWITCH' in name:
                for i, mod in enumerate(modules):
                    if mod['category'] == 'switch':
                        state = data['state']
                        cid = mod['client_id']
                        client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'state': state}))
                print(f"Command received. Setting all switches to state {state}.")
            elif 'LIGHT' in name:
                for i, mod in enumerate(modules):
                    if mod['category'] == 'light':
                        state = data['state']
                        cid = mod['client_id']
                        client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'state': state}))
                print(f"Command received. Setting all lights to state {state}.")
            elif 'DOOR' in name:
                for i, mod in enumerate(modules):
                    if mod['category'] == 'door':
                        state = data['state']
                        cid = mod['client_id']
                        client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'state': state}))
                print(f"Command received. Setting all doors to state {state}.")

    except json.JSONDecodeError as e:
        print("JSON decode failed:", e)
        print("Raw message:", msg.payload)
    except Exception as e:
        print("Unexpected error in on_message:", e)

def get_module_current_power_data():
    results = db_get_module_current_power_data()
    for mod in results:
        if mod['category'] == 'light':
            mod['power'] = str(light_power_data[mod["client_id"]])
    return results

def get_available_all_modules_ctrl():
    return db_get_available_all_modules_ctrl()

def init_modules():
    client.subscribe(T_SENSOR_PUBLISH)
    client.subscribe(T_SENSOR_MAIN_CTRL)
    client.on_message = on_message

    # Turn off all modules when load the system
    modules = db_get_available_all_modules()
    
    for mod in modules:
        if mod['category'] == 'light' or mod['category'] == 'switch':
            cid = mod['client_id']
            if mod['category'] == 'light':
                light_power_data[cid] = 0
            client.publish(f"{T_SENSOR_CTRL_PREFIX}/{cid}", json.dumps({'state': 0}))

