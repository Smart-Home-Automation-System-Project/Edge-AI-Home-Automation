"""
Not Used Currently
"""

import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv


def load_environment():
    # Load environment variables from the .env file
    load_dotenv()

    # ====== MANUAL OVERRIDE FLAG ======
    # Set this to True to force training for demonstration, regardless of day or time
    FORCE_TRAINING = False  # Change this to True to demonstrate model training
    # ==================================

    # Retrieve the project path from environment variables
    project_path = os.getenv('PATH_TO_PROJECT')

    # Path to train.py inside 'lights_temp_automation' directory
    train_path = os.path.join(project_path, 'lights_temp_automation', 'train.py')

    return FORCE_TRAINING, project_path, train_path


def is_training_time(FORCE_TRAINING):
    # Function to check if it's the end of the week (Sunday) and the time is between 11:30 PM and 11:59 PM

    # If manual override is active, always return True
    if FORCE_TRAINING:
        return True

    now = datetime.now()

    # Sunday is day 6 (0 is Monday, 6 is Sunday)
    is_sunday = now.weekday() == 6

    # Check if time is between 11:30 PM and 11:59 PM
    is_time_window = 23 <= now.hour < 24 and 30 <= now.minute < 60

    return is_sunday and is_time_window


def train_model(train_path, force=False):
    # Determine if we should train based on time or force parameter
    if force or is_training_time(force):
        if force:
            print("MANUAL OVERRIDE: Forcing model training...")
        else:
            print("It's Sunday between 11:30 PM and 11:59 PM! Training model...")

        # Call train.py to train the model
        result = subprocess.run(['python', train_path], capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print("Model trained successfully.")
            return True
        else:
            print("Error while training the model.")
            print(result.stderr)
            return False
    else:
        print("It's not training time. Skipping model training.")
        return False


def main():
    FORCE_TRAINING, _, train_path = load_environment()

    # Display whether we're in manual override mode
    if FORCE_TRAINING:
        print("MANUAL OVERRIDE MODE: Will train model regardless of day/time")

    # Train the model based on schedule or manual override
    train_model(train_path, FORCE_TRAINING)


if __name__ == "__main__":
    main()