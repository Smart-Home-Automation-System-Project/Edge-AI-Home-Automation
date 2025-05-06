from sensor.s_module import init_modules
from threading import Thread
import time
from utils.console import *

if __name__ == "__main__":
    print(f"""
===================================================
AI Home Automation System - Central Control Unit
Version: 1.0.0 (Stable)
Status: {GREEN}Running...{RESET}
===================================================
""")

    init_modules()

    try:
        print("Press CTRL+C to quit")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped")
