from sensor.s_module import init_modules
from threading import Thread

if __name__ == "__main__":
    init_modules()
    try:
        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Stopped.")
