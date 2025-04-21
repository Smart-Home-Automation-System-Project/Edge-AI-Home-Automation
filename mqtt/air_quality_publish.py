import json
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

load_dotenv()

def publish_message(topic, message, retain=False):

    try:
        broker_ip = os.getenv("MQTT_BROKER")
        if not broker_ip:
            print("⚠️ MQTT_BROKER not set in .env")
            return False

        client = mqtt.Client()
        client.connect(broker_ip, 1883)

        payload = json.dumps(message) if isinstance(message, dict) else message
        result = client.publish(topic, payload, retain=retain)
        client.disconnect()

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"📤 Published to [{topic}]: {payload}")
            return True
        else:
            print(f"⚠️ Failed to publish to [{topic}], code: {result.rc}")
            return False

    except Exception as e:
        print(f"❌ Error publishing to MQTT: {str(e)}")
        return False
