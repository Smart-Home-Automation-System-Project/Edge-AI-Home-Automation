"""
FOR DEMONSTRATION
-----------------
To populate 'sensors' db table easily with sample sensors .
"""
from database import db_add_sensor

# Sample sensors with client_id, name, and category information
sample_sensors = [
    # lights
    ("L-2025.04.19-21.09-0001", "l1", "light"),
    ("L-2025.04.19-21.09-0002", "l2", "light"),
    ("L-2025.04.19-21.09-0003", "l3", "light"),
    ("L-2025.04.19-21.09-0004", "l4", "light"),
    ("L-2025.04.19-21.09-0005", "l5", "light"),
    ("L-2025.04.19-21.09-0006", "l6", "light"),
    ("L-2025.04.19-21.09-0007", "l7", "light"),
    ("L-2025.04.19-21.09-0008", "l8", "light"),

    # temperature sensors
    ("T-2025.04.19-21.09-0001", "t1", "temp"),
    ("T-2025.04.19-21.09-0002", "t2", "temp"),
    ("T-2025.04.19-21.09-0003", "t3", "temp"),
    ("T-2025.04.19-21.09-0004", "t4", "temp"),

    # radar_sensors
    ("R-2025.04.19-21.09-0001", "r1", "radar"),
    ("R-2025.04.19-21.09-0002", "r2", "radar"),
    ("R-2025.04.19-21.09-0003", "r3", "radar"),
    ("R-2025.04.19-21.09-0004", "r4", "radar"),
    ("R-2025.04.19-21.09-0005", "r5", "radar"),
    ("R-2025.04.19-21.09-0006", "r6", "radar"),
    ("R-2025.04.19-21.09-0007", "r7", "radar"),
    ("R-2025.04.19-21.09-0008", "r8", "radar"),

    # other devices
    ("D-2025.04.19-21.09-0001", "Front Door", "door"),
    ("SW-2025.04.19-21.09-0001", "LivingRoom TV", "switch")
]

# Insert each sensor using the db_add_sensor function
for client_id, name, category in sample_sensors:
    db_add_sensor(client_id, name, category)

print("Sensors inserted into the database.")
