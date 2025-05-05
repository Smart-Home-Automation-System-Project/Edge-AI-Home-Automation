import os
import subprocess
from datetime import datetime
import time
from dotenv import load_dotenv
import sys


def load_environment():
    # Load environment variables from the .env file in src/config folder
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', '.env')
        load_dotenv(config_path)

        # Retrieve the project path from environment variables
        project_path = os.getenv('PATH_TO_PROJECT')

        if not project_path:
            # Default to the directory two levels up from this script if not found
            project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Just use the direct path to predict.py in the same directory
        predict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'predict.py')

        # MQTT publish path
        mqtt_publish_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mqtt', 'lights_temp_publish.py')

        return project_path, predict_path, mqtt_publish_path
    except Exception as e:
        print(f"Error in load_environment: {e}")
        sys.exit(1)


def run_predictions_and_publish(predict_path, mqtt_publish_path):
    # Function to run predictions and publish data
    try:
        print("Running predictions...")
        # Run predict.py directly with current environment
        result = subprocess.run(['python', predict_path], capture_output=True, text=True)

        if result.returncode == 0:
            print("Predictions completed successfully.")

            # After running predictions, invoke lights_temp_publish.py
            print("Sending prediction data via MQTT...")
            mqtt_result = subprocess.run(['python', mqtt_publish_path], capture_output=True, text=True)

            if mqtt_result.returncode == 0:
                print("Data successfully sent via MQTT.")
            else:
                print(f"Error while sending data via MQTT. Exit code: {mqtt_result.returncode}")
        else:
            print(f"Error while making predictions. Exit code: {result.returncode}")
    except Exception as e:
        print(f"Exception in run_predictions_and_publish: {e}")


def main():
    try:
        _, predict_path, mqtt_publish_path = load_environment()
        run_predictions_and_publish(predict_path, mqtt_publish_path)
    except Exception as e:
        print(f"Exception in main: {e}")


if __name__ == "__main__":
    try:
        while True:
            main()  # Run the main logic once
            print(f"Waiting for 15 mins before running again... (Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
            time.sleep(10)  # Wait for 15 minutes (900 seconds) before repeating the process. For demonstration, it's set to 10s
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"Unhandled exception: {e}")