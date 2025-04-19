import csv
import os
import time
from air_common_pub import publish_message

# Initial state of devices/actions
fanOn = False
exhuastOn = False
alarmOn = False
email_send = False
gas_applianceOn = False
gas_val_close = False

def check_air_quality(CO2_level, smoke_density, co_level, gas_level, 
                      threshold_smoke=100, threshold_co=60, gas_threshold=250):
    global fanOn, exhuastOn, alarmOn, email_send, gas_applianceOn, gas_val_close
    
    # CO2 control
    if CO2_level >= 1000 and not fanOn:
        # Turn on exhaust fan for CO2 control
        fanOn = True
        publish_message(topic='home/automation/fan',message="Turn on exhaust fan for CO2 control",retain=fanOn)
    elif CO2_level <= 800 and fanOn:
        # Turn off exhaust fan when CO2 returns to normal
        fanOn = False
        publish_message(topic='home/automation/fan',message="Turn off exhaust fan when CO2 returns to normal",retain=fanOn)

    # Fan state remains unchanged for CO2 control

    # Smoke control
    if smoke_density > threshold_smoke and co_level < threshold_co and not exhuastOn:
        # Turn on exhaust fan for cooking smoke
        exhuastOn = True        
        publish_message(topic='home/automation/exhaust',message="Turn on exhaust fan for cooking smoke",retain=exhuastOn)

    elif smoke_density > threshold_smoke and co_level > threshold_co:
        # Turn on exhaust fan for fire smoke
        if not exhuastOn:
            exhuastOn = True
            publish_message(topic='home/automation/exhaust',message="Turn on exhaust fan for fire smoke",retain=exhuastOn)
           
        # Trigger alarm for fire detection
        if not alarmOn:
            alarmOn = True
            publish_message(topic='home/automation/alarm',message="Trigger alarm for fire detection",retain=alarmOn)
        # Send email alerts via Firebase for fire detection
        email_send = True
        '''
            Send email alerts via Firebase for gas leak 
        '''

    # Gas leak detection
    if gas_level >= gas_threshold:
        # Turn off gas appliances due to leak
        if gas_applianceOn:
            gas_applianceOn = False
            publish_message(topic='home/automation/gas_appliance',message="Turn off gas appliances due to leak",retain=gas_applianceOn)
        # Close gas valve for safety
        if not gas_applianceOn:
            gas_val_close = True
            publish_message(topic='home/automation/gas_appliance',message="Close gas valve for safety",retain=gas_applianceOn)
        # Turn on exhaust fan to ventilate
        if not exhuastOn:
            exhuastOn = True
            publish_message(topic='home/automation/exhaust',message="Turn on exhaust fan to ventilate gas",retain=exhuastOn)
        # Trigger alarm for gas leak
        if not alarmOn:
            alarmOn = True
            publish_message(topic='home/automation/alarm',message="Trigger alarm for gas leak",retain=alarmOn)
        # Send email alerts via Firebase for gas leak
        email_send = True
        '''
            Send email alerts via Firebase for gas leak 
        '''

def read_and_process_csv(file_path):
    while True:
        try:
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    print(f"\n--- Processing data for {row['date']} {row['time']} ---")
                    
                    # Convert string values to appropriate types
                    CO2_level = int(row['CO2_level'])
                    smoke_density = int(row['smoke_density'])
                    co_level = int(row['co_level'])
                    gas_level = int(row['gas_level'])
                    
                    # Run air quality check for this data point
                    check_air_quality(
                        CO2_level=CO2_level,
                        smoke_density=smoke_density,
                        co_level=co_level,
                        gas_level=gas_level,
                        threshold_smoke=100,
                        threshold_co=60,
                        gas_threshold=250
                    )
        except Exception as e:
            print(f"Error reading or processing CSV file: {e}")
        time.sleep(10)

# Read data from CSV and process each row
csv_file_path = os.path.join(os.path.dirname(__file__), '../air.csv')

if __name__ == "__main__":
    if not os.path.isfile(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}. Please ensure the file exists.")
    else:
        read_and_process_csv(csv_file_path)
