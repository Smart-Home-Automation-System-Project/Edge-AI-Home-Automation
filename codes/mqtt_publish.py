import json
import paho.mqtt.client as mqtt

broker_ip = "192.168.1.101"  # IP of Broker
topic = "home/automation/predictions"

client = mqtt.Client()
client.connect(broker_ip, 1883)

# Simulated prediction
prediction = {
    "l1": 0,
    "l2": 0,
    "l3": 1,
    "t1": 22.5,
    "t2": 21.7,
    "t3": 20.9
}

payload = json.dumps(prediction)
client.publish(topic, payload)
print(f"📤 Prediction sent: {payload}")

client.disconnect()
