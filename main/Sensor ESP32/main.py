import time
import ntptime
import ujson
import network
import os
from machine import Pin, reset
from umqtt.simple import MQTTClient

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

client = None

def connect_mqtt():
    global client
    try:
        if client:
            try:
                client.disconnect()
            except:
                pass
                
        client = MQTTClient(
            "S00000000000001",
            config["mqtt"],
            user=config["mqtt_user"],
            password=config["mqtt_pass"],
            keepalive=30
        )
        client.connect()
        print("MQTT connected")
        return True
    except Exception as e:
        print("MQTT connection failed:", e)
        return False

# GPIO Setup
button = Pin(14, Pin.IN, Pin.PULL_UP)
switch_state = False
last_button_state = 1
topic = b"sensor/publish"
csv_file = "buffer.csv"

def save_to_csv(timestamp, state):
    try:
        data = {
            "type": "switch",
            "time": timestamp,
            "data": state
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
                client.publish(topic, ujson.dumps(msg_obj))
                print("Flushed:", msg_obj)
                time.sleep(0.1)
            except Exception as e:
                print("Failed to process line:", line, "Error:", e)
                save_to_csv(msg_obj["time"], msg_obj["data"])
                
    except Exception as e:
        print("Flush failed:", e)

# Initial connections
wifi_ok = connect_wifi()
if wifi_ok:
    sync_time()
    
mqtt_ok = connect_mqtt()

now = time.localtime()
timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*now[:6])
client.publish(topic, ujson.dumps({
                "type": "switch",
                "time": timestamp,
                "data": "imOnline"
            }));

# Main loop
while True:
    try:
        
        now = time.localtime()
        timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*now[:6])

        state = button.value()
        if state == 0 and last_button_state == 1:
            switch_state = not switch_state
            msg_value = "ON" if switch_state else "OFF"

            # JSON message
            msg = {
                "type": "switch",
                "time": timestamp,
                "data": msg_value
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
                    client.publish(topic, ujson.dumps(msg))
                    print(f"Published: {msg}")
                except Exception as e:
                    print("Publish failed, saving to CSV:", e)
                    save_to_csv(timestamp, msg_value)
                    mqtt_ok = False
            else:
                print("Offline. Saving to CSV")
                save_to_csv(timestamp, msg_value)
                mqtt_ok = connect_mqtt()

            time.sleep(0.5)  # Debounce

        last_button_state = state
        time.sleep(0.05)
        
    except Exception as e:
        print("Main loop error:", e)
        time.sleep(5)
        if not wlan.isconnected():
            reset()

