import os
import subprocess
from datetime import datetime
import time
from dotenv import load_dotenv


def load_environment():
    # Load environment variables from the .env file
    load_dotenv()

    # Retrieve the project path from environment variables
    project_path = os.getenv('PATH_TO_PROJECT')

    # Path to predict.py inside 'lights_temp_automation' directory
    predict_path = os.path.join(project_path, 'lights_temp_automation', 'predict.py')

    # MQTT publish path from the environment
    mqtt_publish_path = os.path.join(project_path, 'mqtt', 'lights_temp_publish.py')

    return project_path, predict_path, mqtt_publish_path


def run_predictions_and_publish(predict_path, mqtt_publish_path):
    # Function to run predictions and publish data
    print("Running predictions...")
    result = subprocess.run(['python', predict_path], capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0:
        print("Predictions completed successfully.")

        # After running predictions, invoke lights_temp_publish.py to send the latest prediction data
        print("Sending prediction data via MQTT...")
        result = subprocess.run(['python', mqtt_publish_path], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("Data successfully sent via MQTT.")
        else:
            print("Error while sending data via MQTT.")
            print(result.stderr)
    else:
        print("Error while making predictions.")
        print(result.stderr)


def main():
    _, predict_path, mqtt_publish_path = load_environment()
    run_predictions_and_publish(predict_path, mqtt_publish_path)


if __name__ == "__main__":
    while True:
        main()  # Run the main logic once
        print(
            f"Waiting for 15 minutes before running again... (Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        time.sleep(10)  # Wait for 15 minutes (900 seconds) before repeating the process. For demonstration, it's set to 10s