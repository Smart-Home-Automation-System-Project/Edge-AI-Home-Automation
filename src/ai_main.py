from ai.air_ctrl import init_ai
import time
from utils.console import *
from utils.mqtt import MQTTConnection

if __name__ == "__main__":
    print(f"""
===================================================
AI Home Automation System - AI
Version: 1.0.0 (Stable)
Status: {GREEN}Running...{RESET}
===================================================
""")
    
    client = MQTTConnection.get_client("ai")

    init_ai(client)

    try:
        print("Press CTRL+C to quit")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped")
