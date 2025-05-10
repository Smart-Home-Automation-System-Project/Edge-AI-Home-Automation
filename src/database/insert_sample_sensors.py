"""
FOR DEMONSTRATION
-----------------
To populate 'sensors' db table easily with sample sensors .
"""
import os, sys
# Add database directory to path to import database module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import db_add_sensor


# Sample sensors with client_id, name, and category information
sample_sensors = [
    # lights
    ("L-21.09-0001", "l1", "light"),
    ("L-21.09-0002", "l2", "light"),
    ("L-21.09-0003", "l3", "light"),
    ("L-21.09-0004", "l4", "light"),
    ("L-21.09-0005", "l5", "light"),
    ("L-21.09-0006", "l6", "light"),
    ("L-21.09-0007", "l7", "light"),
    ("L-21.09-0008", "l8", "light"),

    # temperature sensors
    ("T-21.09-0001", "t1", "temp"),
    ("T-21.09-0002", "t2", "temp"),
    ("T-21.09-0003", "t3", "temp"),
    ("T-21.09-0004", "t4", "temp"),

    # radar_sensors
    ("R-21.09-0001", "r1", "radar"),
    ("R-21.09-0002", "r2", "radar"),
    ("R-21.09-0003", "r3", "radar"),
    ("R-21.09-0004", "r4", "radar"),
    ("R-21.09-0005", "r5", "radar"),
    ("R-21.09-0006", "r6", "radar"),
    ("R-21.09-0007", "r7", "radar"),
    ("R-21.09-0008", "r8", "radar"),

    # other devices
    ("D-21.09-0001", "Front Door", "door"),
    ("D-21.09-0002", "Back Door", "door"),
    ("D-21.09-0003", "Gate", "door"),

    ("SW-21.09-0001", "Living Room TV", "switch"),
    ("SW-21.09-0002", "Washing Machine", "switch"),
    ("SW-21.09-0003", "Vacuum Cleaner", "switch"),
    ("SW-21.09-0004", "Refrigerator", "switch"),
    ("SW-21.09-0005", "Microwave", "switch"),
    ("SW-21.09-0006", "Dishwasher", "switch")
]

# Insert each sensor using the db_add_sensor function
for client_id, name, category in sample_sensors:
    db_add_sensor(client_id, name, category)

print("Sensors inserted into the database.")
