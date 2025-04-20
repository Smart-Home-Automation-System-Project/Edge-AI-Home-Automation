import paho.mqtt.client as mqtt
from ..utils.utils import *
from dotenv import load_dotenv
import os

load_dotenv()
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_PORT = os.getenv("MQTT_PORT")

class MQTTConnection:
    _client = None

    @staticmethod
    def get_client():
        if MQTTConnection._client is None:
            MQTTConnection._client = mqtt.Client(client_id="central_main")  # Set your own ID
            MQTTConnection._client.username_pw_set(str(MQTT_USERNAME), str(MQTT_PASSWORD))
            MQTTConnection._client.connect(get_local_ip(), int(MQTT_PORT))
            MQTTConnection._client.loop_start()  # Run network loop in background
        return MQTTConnection._client
