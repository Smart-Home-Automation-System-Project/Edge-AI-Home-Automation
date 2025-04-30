from web.server import init_webui
from utils.mqtt import MQTTConnection

if __name__ == "__main__":
    client = MQTTConnection.get_client("central_main_ui")
    # Start Flask web server
    init_webui(client)

    try:
        print("Press CTRL+C to quit")
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopped")
