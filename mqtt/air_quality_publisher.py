from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import os
import time
import random
import json

load_dotenv() 

broker_ip = os.getenv("MQTT_BROKER")
topic = "home/automation/air"

# Update client creation to use VERSION2 of the API
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(broker_ip, 1883)

while True:
    CO2_level = random.randint(400, 2000)  # CO2 level in ppm
    smoke_density = random.randint(0, 200)  # Smoke density in arbitrary units
    co_level = random.randint(0, 100)  # CO level in ppm
    gas_level = random.randint(0, 500)  # Gas level in arbitrary unit

    data = {
        "CO2_level": CO2_level,
        "smoke_density": smoke_density,
        "co_level": co_level,
        "gas_level": gas_level
    }
    
    client.publish(topic, json.dumps(data))  # Publish the JSON data
    print(f"Published: CO2={CO2_level}ppm, Smoke={smoke_density}, CO={co_level}ppm, Gas={gas_level}")
    time.sleep(2)  # Delay for 2 seconds