import time
import ntptime
import ujson
import network
import os
from machine import Pin, reset
from umqtt.simple import MQTTClient
import random

# Constants
client_id = "L-21.09-0001"
csv_file = "buffer.csv"
T_SENSOR_PUBLISH = b"sensor/publish"
T_SENSOR_CTRL_PREFIX = b"sensor/update/" + client_id.encode()
S_TYPE = 'light'

# Load config
try:
    with open("config.json") as f:
        config = ujson.load(f)
except Exception as e:
    print("Config load failed:", e)
    reset()

# Setup Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def connect_wifi():
    global wlan
    if wlan.isconnected():
        return True
        
    print("Connecting to Wi-Fi...")
    try:
        wlan.connect(config["ssid"], config["password"])
        
        for _ in range(20):
            if wlan.isconnected():
                print("Wi-Fi Connected! IP:", wlan.ifconfig()[0])
                return True
            time.sleep(0.5)
            
        print("Wi-Fi timeout")
        return False
    except Exception as e:
        print("Wi-Fi error:", e)
        return False

def sync_time():
    for _ in range(3):
        try:
            ntptime.settime()
            print("Time synced:", time.localtime())
            return True
        except Exception as e:
            print("NTP sync failed, retrying...", e)
            time.sleep(1)
    return False

# MQTT
client = None
mqtt_ok = False
wifi_ok = False
local_mqtt_address = "mqtt.local"

def connect_mqtt():
    global client
    try:
        if client:
            try:
                client.disconnect()
            except:
                pass
                
        client = MQTTClient(
            client_id,
            local_mqtt_address,
            user=config["mqtt_user"],
            password=config["mqtt_pass"],
            keepalive=30
        )
        client.set_callback(mqtt_callback)
        client.connect()
        client.subscribe(T_SENSOR_CTRL_PREFIX)
        print("MQTT connected and subscribed:", T_SENSOR_CTRL_PREFIX)
        return True
    except Exception as e:
        print("MQTT connection failed:", e)
        return False

# GPIO Setup
button = Pin(14, Pin.IN, Pin.PULL_UP)
OUTPUT = Pin(5, Pin.OUT)  # OUTPUT pin
switch_state = False
last_button_state = 1
brightness = 3


def save_to_csv(timestamp, state):
    try:
        data = {
            "type": S_TYPE,
            "time": timestamp,
            'client_id': client_id,
            "data": state,
            "power": '0' #####################
        }
        with open(csv_file, "a") as f:
            f.write(ujson.dumps(data) + "\n")
    except Exception as e:
        print("CSV write error:", e)
        try:
            with open(csv_file, "w") as f:
                f.write(ujson.dumps(data) + "\n")
        except:
            print("Failed to create CSV")

def flush_csv():
    try:
        if csv_file not in os.listdir():
            return
            
        with open(csv_file, "r") as f:
            lines = f.readlines()
        os.remove(csv_file)
        
        for line in lines:
            try:
                msg_obj = ujson.loads(line.strip())
                client.publish(T_SENSOR_PUBLISH, ujson.dumps(msg_obj))
                print("Flushed:", msg_obj)
                time.sleep(0.1)
            except Exception as e:
                print("Failed to process line:", line, "Error:", e)
                save_to_csv(msg_obj["time"], msg_obj["data"])
                
    except Exception as e:
        print("Flush failed:", e)


def mqtt_submit_current_state():
    global mqtt_ok
    global SENSOR_READ

    msg = {
        "client_id": client_id,
        "type": S_TYPE,
        "time": timestamp,
        "data":SENSOR_READ,
        "power": '0' #####################
    }

    if not wlan.isconnected():
        wifi_ok = connect_wifi()
        if wifi_ok:
            sync_time()

    if not client:
        mqtt_ok = connect_mqtt()

    if mqtt_ok:
        try:
            flush_csv()
            client.publish(T_SENSOR_PUBLISH, ujson.dumps(msg))
            print(f"Published: {msg}")
        except Exception as e:
            print("Publish failed, saving to CSV:", e)
            save_to_csv(timestamp, SENSOR_READ)
            mqtt_ok = False
    else:
        print("Offline. Saving to CSV")
        save_to_csv(timestamp, SENSOR_READ)
        mqtt_ok = connect_mqtt()


def set_color(i,r,g,b):
    pass
    


def mqtt_callback(topic, msg):
    global switch_state
    global SENSOR_READ
    print("Received message:", topic, msg)

    try:
        payload = ujson.loads(msg)
        
        # Normalize the command to uppercase
        cmd = payload["state"].upper()
        if cmd in ["ON", "OFF"]:
            switch_state = (cmd == "ON")
            OUTPUT.value(switch_state)
            if switch_state:
                SENSOR_READ = brightness;
            else:
                SENSOR_READ = 0;
            print("OUTPUT set via MQTT:", cmd)
            mqtt_submit_current_state()
            
    except Exception as e:
        print("Callback error:", e)



# Initial connections
wifi_ok = connect_wifi()
if wifi_ok:
    sync_time()
    
mqtt_ok = connect_mqtt()

# Subscribe to control topic
client.set_callback(mqtt_callback)
client.subscribe(T_SENSOR_CTRL_PREFIX + ("/").encode() + client_id.encode())


now = time.localtime()
timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*now[:6])
client.publish(T_SENSOR_PUBLISH, ujson.dumps({
                "client_id": client_id,
                "type": S_TYPE,
                "time": timestamp,
                "data": "imOnline",
            }));

# Main loop
while True:
    try:
        # Check for incoming MQTT messages
        try:
            client.check_msg()
        except Exception as e:
            print("MQTT check_msg error:", e)
            mqtt_ok = connect_mqtt()

        
        now = time.localtime()
        timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*now[:6])

        state = button.value()
        if state == 0 and last_button_state == 1:
            switch_state = not switch_state
            OUTPUT.value(switch_state)
            if switch_state:
                SENSOR_READ = brightness;
            else:
                SENSOR_READ = 0;
            
            mqtt_submit_current_state()

            time.sleep(0.5)  # Debounce

        last_button_state = state
        time.sleep(0.05)
        
    except Exception as e:
        print("Main loop error:", e)
        time.sleep(5)
        if not wlan.isconnected():
            print("Still offline... will retry")


