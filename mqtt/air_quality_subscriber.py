import paho.mqtt.client as mqtt
import json
import os
from dotenv import load_dotenv
import time
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../air-quality-safety-system'))
from main import check_air_quality

# Load environment variables from .env file
load_dotenv()

# === MQTT Setup ===
broker_ip = os.getenv("MQTT_BROKER")  # IP of Broker (from .env)
topic = "home/automation/air"

# Update the callback function - VERSION2 callbacks include connection_result parameter
def on_connect(client, userdata, flags, rc, properties=None):
    print("✅ Connected to broker.")
    client.subscribe(topic)
    print(f"📡 Subscribed to topic: {topic}")

# Update the on_message callback too for consistency
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    CO2_level = payload.get("CO2_level", None)
    smoke_density = payload.get("smoke_density", None)
    co_level = payload.get("co_level", None)
    gas_level = payload.get("gas_level", None)
    
    print(f"\nReceived data: CO2={CO2_level}ppm, Smoke={smoke_density}, CO={co_level}ppm, Gas={gas_level}")
    check_air_quality(CO2_level=CO2_level, smoke_density=smoke_density, co_level=co_level, gas_level=gas_level)

# Client setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

try:
    print(f"Connecting to MQTT broker at {broker_ip}...")
    client.connect(broker_ip, 1883)
    # Use loop_forever instead of a custom while loop
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopping subscriber...")
    client.disconnect()
except Exception as e:
    print(f"Error connecting to broker: {e}")
    print("Make sure the MQTT broker is running")