from ai.ai import init_ai
from utils.console import *
from utils.mqtt import MQTTConnection
import os

if __name__ == "__main__":
    print(f"""
===================================================
AI Home Automation System - AI
Version: 1.0.0 (Stable)
Status: {GREEN}Running...{RESET}
===================================================
""")
    
    client = MQTTConnection.get_client("central_main_ai")

    try:
        print("Press CTRL+C to quit")
        init_ai(client)

    except KeyboardInterrupt:
        print("Stopped")
