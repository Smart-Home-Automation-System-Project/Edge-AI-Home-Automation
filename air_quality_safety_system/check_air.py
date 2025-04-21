import csv
import os
import time
from mqtt.air_quality_publish import publish_message

# Initial states
exhaustOn = False
alarmOn_smoke = False
alarmOn_gas = False
gas_applianceOn = True
gas_val_close = True

def check_air_quality(CO2_level, smoke_density, co_level, gas_level,
                      threshold_smoke=70, threshold_co=50, gas_threshold=250):
    global exhaustOn, alarmOn_smoke, alarmOn_gas, gas_applianceOn, gas_val_close

    # ==== CO2 CONTROL ====
    co2_action = None
    if CO2_level >= 1000 :
        exhaustOn = True
        co2_action = "Turn ON exhaust fan (CO2 high)"
    elif CO2_level <= 800:
        exhaustOn = False
        co2_action = "Turn OFF exhaust fan (CO2 normal)"

    if co2_action:
        publish_message("home/automation/co2_control", {
            "co2_level": CO2_level,
            "exhaust_fan": int(exhaustOn),
            "action": co2_action
        })
    # ==== SMOKE DETECTION ====
    smoke_action = None
    smoke_alert = None

    if smoke_density > threshold_smoke:
        if co_level < threshold_co:
            # Cooking smoke (no alarm)
            exhaustOn = True
            smoke_action = "Turn ON exhaust fan (cooking smoke)"
            alarmOn_smoke = False  # Ensure alarm stays off during cooking
        else:
            # Fire smoke
            exhaustOn = True
            smoke_action = "Turn ON exhaust fan (fire smoke)"
            alarmOn_smoke = True
            smoke_alert = "Trigger smoke alarm (fire smoke)"
          # 📬 SEND EMAIL ALERT - FIRE SMOKE DETECTED
          # TODO: call your send_email_alert() function here for fire smoke
    else:
        # No smoke or smoke has cleared
        alarmOn_smoke = False  # Reset alarm when no fire smoke

    if smoke_action or smoke_alert:
        publish_message("home/automation/smoke_detection", {
            "smoke_density": smoke_density,
            "co_level": co_level,
            "exhaust_fan": int(exhaustOn),
            "alarm": int(alarmOn_smoke),
            "action": smoke_action or smoke_alert
        })

    # ==== GAS LEAK DETECTION ====
    gas_action = []

    if gas_level >= gas_threshold:
            gas_applianceOn = False
            gas_action.append("Turn OFF gas appliances")
            gas_val_close = True
            gas_action.append("Close gas valve")
            exhaustOn = True
            gas_action.append("Turn ON exhaust fan")
            alarmOn_gas = True
            gas_action.append("Trigger gas alarm")

            # 📬 SEND EMAIL ALERT - GAS LEAK
            # TODO: call your send_email_alert() function here for gas leak            

    if gas_action:
        publish_message("home/automation/gas_detection", {
            "gas_level": gas_level,
            "gas_appliance": int(gas_applianceOn),
            "gas_valve_closed": int(gas_val_close),
            "exhaust_fan": int(exhaustOn),
            "alarm": int(alarmOn_gas),
            "actions": gas_action
        })

def read_and_process_csv(file_path):
    while True:
        try:
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                rows = list(csv_reader)
                if rows:
                    last_row = rows[-1]
                    print(f"\n--- Processing {last_row['date']} {last_row['time']} ---")
                    CO2_level = int(last_row['CO2_level'])
                    smoke_density = int(last_row['smoke_density'])
                    co_level = int(last_row['co_level'])
                    gas_level = int(last_row['gas_level'])

                    check_air_quality(
                        CO2_level, smoke_density, co_level, gas_level
                    )
                else:
                    print("No data in CSV.")
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
        time.sleep(10)

csv_file_path = os.path.join(os.path.dirname(__file__), '../air.csv')

if __name__ == "__main__":
    if not os.path.isfile(csv_file_path):
        print(f"❌ air.csv not found at: {csv_file_path}")
    else:
        read_and_process_csv(csv_file_path)
