from datetime import datetime, timedelta
import socket

def get_localtime(utc_time_str):
    # Parse the UTC time string
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")
    # Add 5 hours 30 minutes for Sri Lanka timezone
    local_time = utc_time + timedelta(hours=5, minutes=30)
    local_time_str = local_time.strftime("%Y-%m-%d %H:%M:%S")
    return local_time_str

def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        return f"Error: {e}"