from sensor.s_module import init_modules
from threading import Thread
import time
from utils.console import *
from utils.utils import get_local_ip
from zeroconf import ServiceInfo, Zeroconf
import socket
from sensor.S_server import init_data_server

ip = get_local_ip()
info = ServiceInfo(type_="_mqtt._tcp.local.", name="MQTT Broker._mqtt._tcp.local.",
    addresses=[socket.inet_aton(ip)], port=1883, properties={}, server="mqtt.local.")
zeroconf = Zeroconf()


if __name__ == "__main__":
    print(f"""
===================================================
AI Home Automation System - Central Control Unit
Version: 1.0.0 (Stable)
Status: {GREEN}Running...{RESET}
===================================================
""")
    print(f"Registering MQTT service at {ip}...")
    zeroconf.register_service(info)
    init_modules()
    init_data_server()

    try:
        print("Press CTRL+C to quit")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        zeroconf.unregister_service(info)
        zeroconf.close()
        print("Stopped")
