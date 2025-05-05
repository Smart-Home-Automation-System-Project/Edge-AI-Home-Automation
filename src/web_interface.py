from web.server import init_webui
from utils.mqtt import MQTTConnection
import time
from utils.console import *

if __name__ == "__main__":
    print(f"""
===================================================
AI Home Automation System - Web UI
Version: 1.0.0 (Stable)
Status: {GREEN}Running...{RESET}
===================================================
""")

    client = MQTTConnection.get_client("central_main_ui")
    init_webui(client)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped")
