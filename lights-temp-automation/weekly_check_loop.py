import os
import subprocess
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the project path and mqtt_publish path from environment variables
project_path = os.getenv('PATH_TO_PROJECT')

# Paths to train.py and predict.py inside 'lights-temp-automation' directory
train_path = os.path.join(project_path, 'lights-temp-automation', 'train.py')
predict_path = os.path.join(project_path, 'lights-temp-automation', 'predict.py')

# MQTT publish path from the environment
mqtt_publish_path = os.path.join(project_path, 'mqtt', 'mqtt_publish.py')

# Function to check if it's the end of the week (Sunday)
def is_end_of_week():
    # Sunday is day 6 (0 is Monday, 6 is Sunday)
    return datetime.now().weekday() == 6


# Main script logic
def main():
    # Set this flag to True or False to simulate the end of the week
    # If you want to manually control whether it's the end of the week or not, set this to True or False
    manual_end_of_week = False  # Change this flag for manual control

    if manual_end_of_week:
        print("Manually setting end of the week...")
        # Manually set whether it's the end of the week (True = End of week, False = Not end of week)
        end_of_week = True  # Manually setting it to True (you can set it to False for testing)
    else:
        # Default check if it's the end of the week based on current day
        end_of_week = is_end_of_week()

    if end_of_week:
        print("It's the end of the week! Training model...")
        # Call train.py to train the model
        result = subprocess.run(['python', train_path], capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print("Model trained successfully. Running predictions...")
            # After training, call predict.py to make predictions
            result = subprocess.run(['python', predict_path], capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                print("Predictions completed successfully.")

                # After running predictions, invoke mqtt_publish.py to send the latest prediction data
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
        else:
            print("Error while training the model.")
            print(result.stderr)
    else:
        print("It's not the end of the week. Running predictions...")
        # If it's not the end of the week, just call predict.py
        result = subprocess.run(['python', predict_path], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("Predictions completed successfully.")

            # After running predictions, invoke mqtt_publish.py to send the latest prediction data
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


if __name__ == "__main__":
    while True:
        main()  # Run the main logic once
        print("Waiting for 15 minutes before running again...")
        time.sleep(10)  # Wait for 15 minutes (900 seconds) before repeating the process
