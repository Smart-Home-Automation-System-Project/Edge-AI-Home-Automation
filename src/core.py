from sensor.s_module import init_modules
from threading import Thread
import time
from utils.console import *
from utils.utils import get_local_ip
from zeroconf import ServiceInfo, Zeroconf
import socket
from sensor.S_server import init_data_server
import utils.globals

ip = get_local_ip()
zeroconf = Zeroconf()
info1 = ServiceInfo(
    "_mqtt._tcp.local.",
    "Main MQTT._mqtt._tcp.local.",
    addresses=[socket.inet_aton(ip)],
    port=1883,
    properties={},
    server="mqtt.local."
)

info2 = ServiceInfo(
    "_http._tcp.local.",
    "My Dashboard._http._tcp.local.",
    addresses=[socket.inet_aton(ip)],
    port=80,
    properties={},
    server="home.local."
)


if __name__ == "__main__":
    print(f"""
===================================================
AI Home Automation System - Central Control Unit
Version: 1.0.0 (Stable)
Status: {GREEN}Running...{RESET}
===================================================
""")
    print(f"Registering MQTT service at {ip}...")
    zeroconf.register_service(info1)
    zeroconf.register_service(info2)
    utils.globals.client_id = 'central_main'
    init_modules()
    init_data_server()

    try:
        print("Press CTRL+C to quit")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        zeroconf.unregister_service(info1)
        zeroconf.unregister_service(info2)
        zeroconf.close()
        print("Stopped")
