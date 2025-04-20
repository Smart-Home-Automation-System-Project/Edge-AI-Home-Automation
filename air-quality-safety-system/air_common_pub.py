import json
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def publish_message(topic, message, retain):
    """
    Generic MQTT publisher that publishes a message to a specified topic.
    
    Args:
        topic (str): The MQTT topic to publish to
        message (any): The message to publish (will be converted to JSON if not a string)
        retain (bool): Whether to retain the message on the broker
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # === MQTT Setup ===
        broker_ip = os.getenv("MQTT_BROKER")  # IP of Broker (from .env)
        if not broker_ip:
            print("⚠️ Error: MQTT_BROKER environment variable not set")
            return False
            
        client = mqtt.Client()
        client.connect(broker_ip, 1883)
        
        # Convert message to JSON string if it's not already a string
        if not isinstance(message, str):
            payload = json.dumps(message)
        else:
            payload = message
            
        # === Publish to MQTT ===
        result = client.publish(topic, payload, retain=retain)
        client.disconnect()
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"📤 Message published to {topic}: {payload}")
            return True
        else:
            print(f"⚠️ Failed to publish message, return code: {result.rc}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error publishing message: {str(e)}")
        return False

# Example usage:
if __name__ == "__main__":
    # Example 1: Publish a dictionary
    data = {"sensor": "air_quality", "CO2_level": 950, "status": "warning"}
    publish_message("home/air/quality", data)
    
    # Example 2: Publish a string with retain flag
    publish_message("home/status", "System online", retain=True)
