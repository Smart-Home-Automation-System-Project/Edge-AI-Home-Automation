import os
from utils.console import *
from ai.predict import ai_predict, load_model
from datetime import datetime
from sensor.topics import *
import json
import time
from database.database import db_get_light_sensor_names, db_get_radar_current_data


def adjust_predictions(preds, radar, light_keys):
    """
    Apply business logic to adjust predictions based on radar presence data.
    """
    adjusted_preds = {}

    # Process light predictions
    for i, light_key in enumerate(light_keys):
        light_value = (preds['lights'][f'l{i + 1}'])
        presence = int(float(radar[i]))

        if light_key in ['l5', 'l6']:
            # For l5 and l6: Turn on if person is present, but never turn off due to absence
            if light_value == 0 and presence == 1:
                # If model says OFF but person is present, override to ON
                adjusted_preds[light_key] = 2
            else:
                # Otherwise keep model prediction (don't turn off if no presence)
                adjusted_preds[light_key] = light_value
        else:
            # For other lights: standard presence logic
            if light_value == 0 and presence == 1:
                # If model says OFF but person is present, override to ON
                adjusted_preds[light_key] = 2
            elif light_value in [1, 2, 3] and presence == 0:
                # If model says ON but no person present, override to OFF
                adjusted_preds[light_key] = 0
            else:
                adjusted_preds[light_key] = light_value
    
    return (adjusted_preds)

def run_predictions_and_publish(model, client):
    # Function to run predictions and publish data
    try:
        print("Running predictions...")
        results = ai_predict(model)

        if results:
            print("Predictions completed successfully.")
            light_keys = db_get_light_sensor_names()
            radar_data = db_get_radar_current_data()

            # Process and adjust light_predictions
            print('Process and adjust light predictions')
            adjusted_light_predictions = adjust_predictions(results, radar_data, light_keys)
            print(adjusted_light_predictions)

            # After running predictions, invoke lights_temp_publish.py
            print("Sending prediction data via MQTT...")
            for k, v in results['temperatures'].items():
                client.publish(T_SENSOR_MAIN_CTRL, json.dumps({"name": k, "value": v}))
                
            for k, v in adjusted_light_predictions.items():
                irgb_value = f"{v},N,N,N"  # TODO : fix the RBG part
                client.publish(T_SENSOR_MAIN_CTRL, json.dumps({"name": k, "irgb": irgb_value}))

    except Exception as e:
        print(f"Exception in run_predictions_and_publish: {e}")

def init_ai(client):
    global model
    model_h5_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.h5")
    new_model_h5_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_new.h5")
    model = load_model(model_h5_path)

    while True:
        try:
            if os.path.isfile(new_model_h5_path):
                print(f"{YELLOW}New version found, Updating to new model{RESET}")
                if os.path.isfile(model_h5_path):
                    os.remove(model_h5_path)
                os.rename(new_model_h5_path, model_h5_path)
                model = load_model(model_h5_path)
                # TODO : Improve the update logic
            
            print(f"{GREEN}Using {model_h5_path}{RESET}")
            run_predictions_and_publish(model, client)
        except Exception as e:
            print(f"Exception in main: {e}")

        print(f"Waiting for 15 mins before running again... (Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        time.sleep(10)

