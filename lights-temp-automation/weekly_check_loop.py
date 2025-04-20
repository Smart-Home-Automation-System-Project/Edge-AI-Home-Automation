import os
import subprocess
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# ====== MANUAL OVERRIDE FLAG ======
# Set this to True to force training for demonstration, regardless of day or time
FORCE_TRAINING = False  # Change this to True to demonstrate model training
# ==================================

# Retrieve the project path and mqtt_publish path from environment variables
project_path = os.getenv('PATH_TO_PROJECT')

# Paths to train.py and predict.py inside 'lights-temp-automation' directory
train_path = os.path.join(project_path, 'lights-temp-automation', 'train.py')
predict_path = os.path.join(project_path, 'lights-temp-automation', 'predict.py')

# MQTT publish path from the environment
mqtt_publish_path = os.path.join(project_path, 'mqtt', 'lights_temp_publish.py')

# Global variable to track if training has been done in the current time window
training_done_today = False
last_training_date = None


# Function to check if it's the end of the week (Sunday) and the time is between 11:30 PM and 11:59 PM
def is_training_time():
    # If manual override is active, always return True
    if FORCE_TRAINING:
        return True

    now = datetime.now()

    # Sunday is day 6 (0 is Monday, 6 is Sunday)
    is_sunday = now.weekday() == 6

    # Check if time is between 11:30 PM and 11:59 PM
    is_time_window = 23 <= now.hour < 24 and 30 <= now.minute < 60

    return is_sunday and is_time_window


# Function to run predictions and publish data
def run_predictions_and_publish():
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


# Main script logic
def main():
    global training_done_today, last_training_date

    current_date = datetime.now().date()

    # Reset the training flag if it's a new day
    if last_training_date != current_date:
        training_done_today = False
        last_training_date = current_date

    # Check if it's training time and we haven't trained today (or if force training is enabled)
    if is_training_time() and (not training_done_today or FORCE_TRAINING):
        if FORCE_TRAINING:
            print("MANUAL OVERRIDE: Forcing model training for demonstration...")
        else:
            print("It's Sunday between 11:30 PM and 11:59 PM! Training model...")

        # Call train.py to train the model
        result = subprocess.run(['python', train_path], capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print("Model trained successfully.")
            # Mark that we've done training today
            training_done_today = True

            # After training, run predictions and publish
            run_predictions_and_publish()
        else:
            print("Error while training the model.")
            print(result.stderr)
    else:
        # If it's not training time, just run predictions
        if is_training_time() and training_done_today:
            print("Already trained model during this time window. Running predictions only.")
        else:
            print("It's not training time. Running predictions only.")

        run_predictions_and_publish()


if __name__ == "__main__":
    # Display whether we're in manual override mode
    if FORCE_TRAINING:
        print("MANUAL OVERRIDE MODE: Will train model on next cycle regardless of day/time")

    while True:
        main()  # Run the main logic once
        print(
            f"Waiting for 15 minutes before running again... (Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        time.sleep(10)  # Wait for 15 minutes (900 seconds) before repeating the process. For demonstration, it's set to 10s