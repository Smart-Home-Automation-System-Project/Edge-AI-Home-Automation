# lights_temp_automation/predict.py
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import os
from dotenv import load_dotenv
import datetime


def load_environment():
    # Load environment variables from .env file
    load_dotenv()

    # Get the project path from the .env file
    project_path = os.getenv('PATH_TO_PROJECT')

    if not project_path:
        # Default to the directory one level up from this script
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Construct paths dynamically based on the project path
    model_h5_path = os.path.join(project_path, 'model.h5')
    test_csv_path = os.path.join(project_path, 'test.csv')
    predictions_csv_path = os.path.join(project_path, 'predictions.csv')

    return project_path, model_h5_path, test_csv_path, predictions_csv_path


def load_model(model_h5_path):
    # Load the trained model
    try:
        model = keras.models.load_model(model_h5_path, compile=False)
        print(f"Model successfully loaded from {model_h5_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        exit(1)


def load_and_preprocess_data(test_csv_path):
    # Load test data from CSV
    try:
        df = pd.read_csv(test_csv_path)
        print(f"Loaded test data with {len(df)} records")

        if len(df) < 24:
            print("Warning: Test data contains fewer than 24 records. The model expects 24 time steps.")
            print(f"Current record count: {len(df)}")

        # Keep timestamp for reference but don't use it for prediction
        timestamps = df['timestamp'].tolist()

        # Normalize time features exactly as done in train.py
        df['hour'] = df['hour'] / 23.0  # Normalize hour (0-23 → 0-1)
        df['day_of_week'] = df['day_of_week'] / 6.0  # Normalize day (0-6 → 0-1)

        # Normalize temperature values just like in train.py
        df['t1'] = (df['t1'] - 20) / 10.0
        df['t2'] = (df['t2'] - 20) / 10.0
        df['t3'] = (df['t3'] - 20) / 10.0
        df['t4'] = (df['t4'] - 20) / 10.0

        # Select the same features used in training
        features = ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8',
                    't1', 't2', 't3', 't4', 'hour', 'day_of_week']
        X = df[features].values.astype(np.float32)

        # Reshape input for LSTM: (1, SEQ_LEN, features)
        # SEQ_LEN = 24 as defined in train.py
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

        return X, timestamps[-1] if timestamps else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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


# def process_predictions(predictions):
#     # Process the raw predictions to get usable values
#
#     # Extract light and temperature predictions
#     # The model outputs 12 values: 8 for lights and 4 for temperature
#     light_predictions = predictions[0, :8]  # First 8 values are for lights
#     temp_predictions = predictions[0, 8:12]  # Last 4 values are for temperature
#
#     # Process light predictions - convert to integers 0-3
#     # Map to the nearest valid level (0, 1, 2, 3)
#     processed_lights = np.round(np.clip(light_predictions, 0, 3)).astype(int)
#
#     # Process temperature predictions - denormalize as per train.py
#     # In train.py: df['t1'] = (df['t1'] - 20) / 10.0
#     # So reverse: temp = (normalized_temp * 10.0) + 20
#     processed_temps = (temp_predictions * 10.0) + 20.0
#
#     # Combine the processed predictions
#     final_predictions = np.concatenate([processed_lights, processed_temps])
#
#     # Format the results
#     results = {
#         'lights': {f'l{i + 1}': int(processed_lights[i]) for i in range(8)},
#         'temperatures': {f't{i + 1}': round(float(processed_temps[i]), 2) for i in range(4)}
#     }
#
#     return final_predictions, results


def process_predictions(predictions):
    # Process the raw predictions to get usable values

    # Extract light and temperature predictions
    light_predictions = predictions[0, :8]  # First 8 values are for lights
    temp_predictions = predictions[0, 8:12]  # Last 4 values are for temperature

    # Process light predictions - convert to integers 0-3
    processed_lights = np.round(np.clip(light_predictions, 0, 3)).astype(int)

    # Add random variation to temperature predictions
    # The random factor will change with each run
    random_variation = np.random.uniform(-2.0, 2.0, size=len(temp_predictions))

    # Apply the random variation before denormalizing
    varied_temp_predictions = temp_predictions + random_variation * 0.2  # 0.2 controls magnitude of variation

    # Process temperature predictions - denormalize as per train.py
    processed_temps = (varied_temp_predictions * 10.0) + 20.0

    # Combine the processed predictions
    final_predictions = np.concatenate([processed_lights, processed_temps])

    # Format the results
    results = {
        'lights': {f'l{i + 1}': int(processed_lights[i]) for i in range(8)},
        'temperatures': {f't{i + 1}': round(float(processed_temps[i]), 2) for i in range(4)}
    }

    return final_predictions, results

def save_predictions(final_predictions, predictions_csv_path):
    # Save predictions to CSV file
    predictions_df = pd.DataFrame([final_predictions],
                                  columns=["l1", "l2", "l3", "l4", "l5", "l6", "l7", "l8",
                                           "t1", "t2", "t3", "t4"])

    predictions_df.to_csv(predictions_csv_path, index=False, float_format='%.2f')
    print(f"Predictions saved to {predictions_csv_path}")


def main():
    print("Starting prediction process...")

    # Load environment and paths
    project_path, model_h5_path, test_csv_path, predictions_csv_path = load_environment()
    print(f"Project path: {project_path}")

    # Load the trained model
    model = load_model(model_h5_path)

    # Load and preprocess test data
    X, last_timestamp = load_and_preprocess_data(test_csv_path)
    print(f"Preprocessed data shape: {X.shape}")
    print(f"Last timestamp: {last_timestamp}")

    # Make predictions
    raw_predictions = make_predictions(model, X)

    # Process the predictions
    final_predictions, results = process_predictions(raw_predictions)
    # Save predictions to CSV file
    save_predictions(final_predictions, predictions_csv_path)
    # Print detailed results
    print("\nPrediction results:")
    print("Light levels (0-3): ", end="")
    print(" | ".join([f"{k}: {v}" for k, v in results['lights'].items()]))

    print("Temperature settings (C): ", end="")
    print(" | ".join([f"{k}: {v}" for k, v in results['temperatures'].items()]))


if __name__ == "__main__":
    main()