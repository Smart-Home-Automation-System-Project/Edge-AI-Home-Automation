from utils.mqtt import MQTTConnection
from threading import Thread
from database.database import *
from sensor.topics import *
from utils.console import *
from datetime import datetime
import ast, json
from utils.console import *
import time
import random
import utils.globals

# Client ID to exclude from this virtual module
Exclusions = ['SW-2025.04.19-21.09-0001']
Light_Brightness = {}



def on_message(client, userdata, msg):
    print(f"{BLUE}\n --> Received message from {msg.topic}: {msg.payload.decode()}")

    client_id = msg.topic.split('/')[2]
    # Current time
    timestamp = datetime.now()

    # Subtract 5 hours and 30 minutes
    adjusted_time = timestamp - timedelta(hours=5, minutes=30)

    # Format to string if needed
    formatted = adjusted_time.strftime("%Y-%m-%d %H:%M:%S")

    S_TYPE = None
    for mod in modules:
        if mod['client_id'] == client_id:
            S_TYPE = mod['category']
    _data = ast.literal_eval(msg.payload.decode())
    data_val = None

    if S_TYPE == 'switch':
        if (_data['state'] == 'on'):
            data_val = random.randint(2, 40)
        else:
            data_val = 0
    elif S_TYPE == 'light':
        if 'state' in _data:
            if (_data['state'] == 'on'):
                if client_id in Light_Brightness:
                    data_val = Light_Brightness[client_id]
                else:
                    data_val = Light_Brightness[client_id] = 3
            else:
                data_val = 0
        elif 'irgb' in _data:
            values = _data['irgb'].strip("()").split(",")
            val = int(values[0])
            if (val > 0):
                Light_Brightness[client_id] = val
                data_val = val
            elif val == 0:
                data_val = 0
            print(f" --> Color changed to {_data['irgb']}, I {data_val}")

        data = {
                "type": S_TYPE,
                "time": formatted,
                'client_id': client_id,
                "data": data_val,
                "power": data_val * random.randint(8, 11)
        }
        
        client.publish(T_SENSOR_PUBLISH, json.dumps(data))
        print(f'{RESET}')
        return
    
    elif S_TYPE == 'door':
        if _data['state'] == "lock":
            data_val = "LOCK"
        else:
            data_val = "UNLOCK"

    elif S_TYPE == 'temp':
        data_val = _data['value']

    data = {
            "type": S_TYPE,
            "time": formatted,
            'client_id': client_id,
            "data": data_val
    }
    
    client.publish(T_SENSOR_PUBLISH, json.dumps(data))
    print(f'{RESET}')

def load_modules():
    global modules
    modules = db_get_available_all_modules()
    # Exclusions
    for module in modules:
        if module['client_id'] in Exclusions:
            modules.remove(module)
        else:
            client.subscribe(f"{T_SENSOR_CTRL_PREFIX}/{module['client_id']}")
    client.on_message = on_message

def main_page():
    load_modules()
    print(f"\n{GREEN}Available Sensors:")
    print(f"{'Index':<6} {'Name':<25} {'Category':<20} {'Last Value':<15}")
    print("-" * 70)
    
    for i, mod in enumerate(modules):
        name = mod['name'] if mod['name'] else "Unnamed"
        category = mod['category'] if mod['category'] else "Unknown"
        last_val = mod['last_val'] if mod['last_val'] else "-"
        
        print(f"{i:<6} {name:<25} {category:<20} {YELLOW}{last_val:<15}{GREEN}")
    try:
        print(f"\n{RESET}Please select a sensor : ", end='')
        _input = int(input())
        if (0 <=  _input and _input < len(modules)):
            return _input
        else:
            return -1
    except:
        return -1

def update_page(modIndex):
    mod = modules[modIndex]
    name = mod['name'] if mod['name'] else "Unnamed"
    client_id = mod['client_id'] if mod['client_id'] else "NULL"
    category = mod['category'] if mod['category'] else "Unknown"
    last_val = mod['last_val'] if mod['last_val'] else "-"
    
    print(f"\nSelected sensor\nName : {name}\nCategory : {category}\nvalue : {last_val}")
  
    try:
        print(f"\n{RESET}Set new value (type exit to terminate): ", end='')
        _input = int(input())

        if (str(_input).upper() == 'EXIT'):
            return -1
        
        if (0 <=  _input and _input < 5000):
            timestamp = datetime.now()

            # Subtract 5 hours and 30 minutes
            adjusted_time = timestamp - timedelta(hours=5, minutes=30)

            # Format to string if needed
            formatted = adjusted_time.strftime("%Y-%m-%d %H:%M:%S")
            data = {
                    "type": category,
                    "time": formatted,
                    'client_id': client_id,
                    "data": _input
            }

            client.publish(T_SENSOR_PUBLISH, json.dumps(data))
            time.sleep(2)

            return 1
        else:
            return -1
    except:
        return -1




if __name__ == "__main__":
    print(f"""
===================================================
AI Home Automation System - Virtual Module
Version: 1.0.0 (Stable)
Status: {GREEN}Running...{RESET}
===================================================
""")
    global client
    utils.globals.client_id = "virtual_module"
    client = MQTTConnection.get_client("virtual_module")
    load_modules()

    while True:
        modIndex = main_page()
        if (modIndex == -1):
            print(f"{RED}[Index error] : No matching index found. Try again !{RESET}")
            continue
        else:
            if (update_page(modIndex)):
                print("Success")
            else:
                print("Error")


    
