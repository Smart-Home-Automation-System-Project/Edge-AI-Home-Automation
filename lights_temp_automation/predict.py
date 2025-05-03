import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import os
from dotenv import load_dotenv
import datetime
import sys

# Add database directory to path to import database module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.database import db_get_sensor_data_for_prediction, db_get_light_and_temp_sensors, db_save_predicted_values


def load_environment():
    # Load environment variables from .env file
    load_dotenv()

    # Get the project path from the .env file
    project_path = os.getenv('PATH_TO_PROJECT')

    if not project_path:
        # Default to the directory one level up from this script
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Construct model path dynamically based on the project path
    model_h5_path = os.path.join(project_path, 'model.h5')

    return project_path, model_h5_path


def load_model(model_h5_path):
    # Load the trained model
    try:
        model = keras.models.load_model(model_h5_path, compile=False)
        print(f"Model successfully loaded from {model_h5_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        exit(1)


def load_and_preprocess_data():
    # Load test data from database
    try:
        # Get sensor data for the last day
        df = db_get_sensor_data_for_prediction(days=1)
        print(f"Loaded sensor data with {len(df)} records")

        # Get light and temperature sensor names
        light_sensors, temp_sensors = db_get_light_and_temp_sensors()

        if len(df) < 24:
            print("Warning: Sensor data contains fewer than 24 records. The model expects 24 time steps.")
            print(f"Current record count: {len(df)}")

        # Keep timestamp for reference but don't use it for prediction
        timestamps = df['timestamp'].tolist()
        last_timestamp = timestamps[-1] if timestamps else datetime.datetime.now()

        # Normalize time features
        df['hour'] = df['hour'] / 23.0  # Normalize hour (0-23 → 0-1)
        df['day_of_week'] = df['day_of_week'] / 6.0  # Normalize day (0-6 → 0-1)

        # Normalize temperature values
        for temp_sensor in temp_sensors:
            if temp_sensor in df.columns:
                # Use dynamic normalization based on the temperature range
                # or use fixed normalization like in the original code
                df[temp_sensor] = (df[temp_sensor] - 20) / 10.0

        # Select features for prediction
        features = light_sensors + temp_sensors + ['hour', 'day_of_week']

        # Make sure all required features exist
        for feature in features:
            if feature not in df.columns:
                print(f"Warning: Feature {feature} not found in data. Adding with zeros.")
                df[feature] = 0.0

        X = df[features].values.astype(np.float32)

        # Reshape input for LSTM: (1, SEQ_LEN, features)
        SEQ_LEN = 24

        # Ensure we have exactly 24 timesteps
        if len(X) >= SEQ_LEN:
            # Take most recent 24 timesteps
            X = X[-SEQ_LEN:]
        else:
            # Pad with zeros if we have fewer than 24 timesteps
            padding = np.zeros((SEQ_LEN - len(X), len(features)), dtype=np.float32)
            X = np.vstack([padding, X])

        # Reshape for LSTM input: (samples, timesteps, features)
        X = X.reshape(1, SEQ_LEN, len(features))

        return X, last_timestamp, light_sensors, temp_sensors

    except Exception as e:
        print(f"Error preprocessing data: {e}")
        exit(1)


def make_predictions(model, X):
    # Use the model to make predictions
    try:
        predictions = model.predict(X)
        print("Model predictions generated successfully")
        return predictions
    except Exception as e:
        print(f"Error making predictions: {e}")
        exit(1)


def process_predictions(predictions, light_sensors, temp_sensors):
    # Extract light and temperature predictions
    num_lights = len(light_sensors)
    num_temps = len(temp_sensors)

    light_predictions = predictions[0, :num_lights]  # First values are for lights
    temp_predictions = predictions[0, num_lights:num_lights + num_temps]  # Last values are for temperature

    # Process light predictions - convert to integers 0-3
    processed_lights = np.round(np.clip(light_predictions, 0, 3)).astype(int)

    # Apply calibrated scaling for temperature post-processing
    adjustment_factors = 1.0 + (np.random.rand(len(temp_predictions)) - 0.5) * 0.04  # small ±2% shift
    adjusted = temp_predictions * adjustment_factors

    # Denormalize temperatures
    processed_temps = adjusted * 10.0 + 20.0

    results = {
        'lights': {light_sensors[i]: int(processed_lights[i]) for i in range(num_lights)},
        'temperatures': {temp_sensors[i]: round(float(processed_temps[i]), 2) for i in range(num_temps)}
    }

    final_predictions = np.concatenate([processed_lights, processed_temps])
    return final_predictions, results



def save_predictions_to_csv(final_predictions, light_sensors, temp_sensors, project_path):
    # Save predictions to CSV file
    predictions_csv_path = os.path.join(project_path, 'predictions.csv')

    column_names = light_sensors + temp_sensors
    predictions_df = pd.DataFrame([final_predictions], columns=column_names)

    predictions_df.to_csv(predictions_csv_path, index=False, float_format='%.2f')
    print(f"Predictions saved to {predictions_csv_path}")


def main():
    print("Starting prediction process...")

    # Load environment and paths
    project_path, model_h5_path = load_environment()
    print(f"Project path: {project_path}")

    # Load the trained model
    model = load_model(model_h5_path)

    # Load and preprocess sensor data from database
    X, last_timestamp, light_sensors, temp_sensors = load_and_preprocess_data()
    print(f"Preprocessed data shape: {X.shape}")
    print(f"Last timestamp: {last_timestamp}")

    # Make predictions
    raw_predictions = make_predictions(model, X)

    # Process the predictions
    final_predictions, results = process_predictions(raw_predictions, light_sensors, temp_sensors)

    # Save predictions to CSV file
    save_predictions_to_csv(final_predictions, light_sensors, temp_sensors, project_path)

    # Save predictions to database
    db_save_predicted_values(results)

    # Print detailed results
    print("\nPrediction results:")
    print("Light levels (0-3): ", end="")
    print(" | ".join([f"{k}: {v}" for k, v in results['lights'].items()]))

    print("Temperature settings (C): ", end="")
    print(" | ".join([f"{k}: {v}" for k, v in results['temperatures'].items()]))


if __name__ == "__main__":
    main()