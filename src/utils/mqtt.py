import paho.mqtt.client as mqtt
from utils.utils import *
from utils.console import *
from dotenv import load_dotenv
import os, time

load_dotenv(dotenv_path='config/.env')
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_PORT = os.getenv("MQTT_PORT")

class MQTTConnection:
    _client = None

    @staticmethod
    def get_client(client_id="central_main"):
        if MQTTConnection._client is None:
            try:
                MQTTConnection._client = mqtt.Client(client_id=client_id)  # Set your own ID
                MQTTConnection._client.username_pw_set(str(MQTT_USERNAME), str(MQTT_PASSWORD))
                MQTTConnection._client.connect(get_local_ip(), int(MQTT_PORT))
                MQTTConnection._client.loop_start()                        # Run network loop in background
            except Exception as e:
                print(f"{RED}MQTT service error{RESET}\nMake sure that mqtt broker is running")
                print("Press CTRL+C to quit")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    exit()
        return MQTTConnection._client
