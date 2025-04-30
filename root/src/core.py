from sensor.s_module import init_modules
from threading import Thread
import time

if __name__ == "__main__":
    init_modules()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped")
