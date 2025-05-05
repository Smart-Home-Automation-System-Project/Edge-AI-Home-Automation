import threading
import os
import sys
from datetime import datetime

# Add the parent directory to path to import other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.console import *
from ai.make_predictions import main as run_predictions


def init_ai(mqtt_client):
    """
    Initialize the AI controller
    This function is called from ai_main.py
    """
    print(f"{BLUE}Initializing AI controller...{RESET}")

    # Set up MQTT subscriptions
    mqtt_client.subscribe("home/ai/commands")

    # Start the prediction script in a background thread
    prediction_thread = threading.Thread(target=start_prediction_loop, daemon=True)
    prediction_thread.start()

    print(f"{GREEN}AI controller initialized successfully{RESET}")
    return True


def start_prediction_loop():
    """
    Start the prediction loop from your existing make_predictions.py
    """
    print(f"{GREEN}Starting AI prediction service{RESET}")
    try:
        # Import here to avoid circular imports
        from ai.make_predictions import main

        # Call the main function directly
        main()
    except Exception as e:
        print(f"{RED}Error starting prediction service: {e}{RESET}")