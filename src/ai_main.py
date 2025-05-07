from utils.console import *
from utils.mqtt import MQTTConnection

print(f"""
===================================================
AI Home Automation System - AI
Version: 1.0.0 (Stable)
Status: {GREEN}Running...{RESET}
===================================================
""")
from ai.ai import init_ai


if __name__ == "__main__":

    
    client = MQTTConnection.get_client("central_main_ai")

    try:
        print("Press CTRL+C to quit")
        init_ai(client)

    except KeyboardInterrupt:
        print("Stopped")
