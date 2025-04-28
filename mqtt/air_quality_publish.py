import json
import paho.mqtt.client as mqtt
import os
import sys
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


# When run as a script via subprocess
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Read from the temp file path passed as argument
        try:
            with open(sys.argv[1], 'r') as f:
                data = json.load(f)
                topic = data.get('topic')
                message = data.get('message')

                if topic and message:
                    publish_message(topic, message)
                else:
                    print("❌ Missing topic or message in data file")
                    sys.exit(1)
        except Exception as e:
            print(f"❌ Error reading data file: {str(e)}")
            sys.exit(1)
    else:
        # Keep the module functionality for backward compatibility
        print("This script can be imported or run directly with a JSON data file path")