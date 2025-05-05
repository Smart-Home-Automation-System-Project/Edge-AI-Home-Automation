import json
import paho.mqtt.client as mqtt
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.database import (
    db_get_latest_prediction_rows,
    db_get_radar_sensor_data,
    db_get_light_sensor_names
)


def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    return os.getenv("MQTT_BROKER")


def setup_mqtt_client(broker_ip):
    """Set up and return an MQTT client connected to the broker."""
    client = mqtt.Client()
    client.connect(broker_ip, 1883)
    return client


def get_latest_predictions():
    """Get and process the latest prediction data from the database."""
    prediction_rows = db_get_latest_prediction_rows()

    # Find latest timestamp
    latest_timestamp = prediction_rows[0]['timestamp'] if prediction_rows else None

    # Create prediction dictionary
    preds = {}
    for row in prediction_rows:
        if row['timestamp'] == latest_timestamp:  # Only use the most recent predictions
            sensor_name = row['sensor_name'].lower()  # Convert to lowercase for consistency
            preds[sensor_name] = row['predicted_value']

    return preds


def get_radar_data():
    """Get and process the latest radar sensor data from the database."""
    radar_rows = db_get_radar_sensor_data()

    # Get the most recent timestamp for radar data
    latest_radar_timestamp = None
    for row in radar_rows:
        if latest_radar_timestamp is None:
            latest_radar_timestamp = row['timestamp']
        elif row['timestamp'] != latest_radar_timestamp:
            break

    # Create radar dictionary with default values
    radar = {f'room{i}': 0 for i in range(1, 9)}  # Assuming 8 radar sensors

    # Fill in actual values
    for row in radar_rows:
        if row['timestamp'] == latest_radar_timestamp:
            # Extract the number from radar name (e.g., "R1" -> "1")
            radar_num = row['name'].lower().replace('r', '')
            radar[f'room{radar_num}'] = int(row['sensor_value'])

    return radar


def adjust_predictions(preds, radar, light_keys):
    """
    Apply business logic to adjust predictions based on radar presence data.
    """
    adjusted_preds = {}

    # Process light predictions
    for i, light_key in enumerate(light_keys):
        radar_key = f'room{i + 1}'
        light_value = int(preds.get(light_key, 0))
        presence = int(radar.get(radar_key, 0))

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

    # Add temperature predictions as is
    for i in range(1, 5):
        temp_key = f't{i}'
        adjusted_preds[temp_key] = preds.get(temp_key, 20.0)  # Default to 20 if not found

    return adjusted_preds


def publish_predictions(client, topic, predictions):
    """Publish predictions to MQTT broker and print the result."""
    payload = json.dumps(predictions)
    client.publish(topic, payload)
    print(f"Prediction sent: {payload}")
    client.disconnect()


def main():
    """Main function to orchestrate the prediction and publishing process."""
    # Load environment and setup
    broker_ip = load_environment()
    mqtt_client = setup_mqtt_client(broker_ip)
    mqtt_topic = "home/automation/predictions"

    # Get data
    predictions = get_latest_predictions()
    radar_data = get_radar_data()
    light_keys = db_get_light_sensor_names()

    # Process and adjust predictions
    adjusted_predictions = adjust_predictions(predictions, radar_data, light_keys)

    # Publish results
    publish_predictions(mqtt_client, mqtt_topic, adjusted_predictions)


if __name__ == "__main__":
    main()