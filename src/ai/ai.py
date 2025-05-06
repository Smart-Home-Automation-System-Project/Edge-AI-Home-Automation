import os
from utils.console import *
from ai.predict import ai_predict, load_model
from datetime import datetime
from sensor.topics import *
import json
import time

def run_predictions_and_publish(model, client):
    # Function to run predictions and publish data
    try:
        print("Running predictions...")
        results = ai_predict(model)

        if results:
            print("Predictions completed successfully.")

            # After running predictions, invoke lights_temp_publish.py
            print("Sending prediction data via MQTT...")
            for k, v in results['temperatures'].items():
                # TODO : fix the logic
                continue
                client.publish(T_SENSOR_MAIN_CTRL, json.dumps({"name": k, "state": v}))
                
            for k, v in results['lights'].items():
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

