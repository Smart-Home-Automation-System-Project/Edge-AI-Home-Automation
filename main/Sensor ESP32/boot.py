import ujson
import network
import time
import machine
from machine import Pin
import os

RESET_PIN = Pin(12, Pin.IN, Pin.PULL_UP)  # GPIO12, active LOW

def check_reset():
    if RESET_PIN.value() == 0:
        print("Reset pin held LOW — erasing config...")
        try:
            os.remove("config.json")
            print("Config erased.")
        except:
            print("No config file found.")
        time.sleep(2)  # Delay so user can release the button

def load_config():
    try:
        with open("config.json", "r") as f:
            return ujson.load(f)
    except:
        return None

def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="SE-GD-SensorModule", password="12345678")
    print("Access Point started, connect to: SE-GD-SensorModule, go to 192.168.4.1")
    import webserver  # Serve setup page

def connect_wifi(config):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    time.sleep(1)  # Give Wi-Fi driver time to wake up
    wlan.connect(config["ssid"], config["password"])

    print("Connecting to Wi-Fi...")
    for i in range(30):  # Wait up to 15 seconds
        if wlan.isconnected():
            print("Connected to Wi-Fi:", wlan.ifconfig())
            return True
        elif wlan.status() < 0 or wlan.status() >= 3:
            print("Wi-Fi status:", wlan.status())
        time.sleep(0.5)
    return False


# MAIN LOGIC
check_reset()
config = load_config()

if config:
    success = connect_wifi(config)
    if success:
        import main  # Run main logic
    else:
        print("Wi-Fi Failed, starting AP mode...")
        start_ap()
else:
    print("No config found, starting AP mode...")
    start_ap()

