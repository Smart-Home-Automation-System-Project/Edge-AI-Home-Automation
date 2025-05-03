import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import os
from dotenv import load_dotenv


def load_environment():
    # Load environment variables from .env file
    load_dotenv()

    # Get the project path from the .env file
    project_path = os.getenv('PATH_TO_PROJECT')

    # Construct paths dynamically based on the project path
    model_h5_path = os.path.join(project_path, 'model.h5')
    test_csv_path = os.path.join(project_path, 'test.csv')
    predictions_csv_path = os.path.join(project_path, 'predictions.csv')

    return project_path, model_h5_path, test_csv_path, predictions_csv_path


def load_model(model_h5_path):
    # Load the model without compiling (fixes the 'mse' issue)
    print("Model loaded.")
    model = keras.models.load_model(model_h5_path, compile=False)
    return model


def load_and_preprocess_data(test_csv_path):
    # === Load test input from CSV ===
    df = pd.read_csv(test_csv_path)

    # Drop timestamp (not used as input for the model)
    df = df.drop('timestamp', axis=1)

    # Normalize hour (0–23 → 0–1) and day_of_week (0–6 → 0–1)
    df['hour'] = df['hour'] / 23.0
    df['day_of_week'] = df['day_of_week'] / 6.0

    # Select input features for the model
    df_input = df[['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 't1', 't2', 't3', 't4', 'hour', 'day_of_week']]

    # Reshape input for LSTM: (samples, timesteps, features)
    input_data = df_input.to_numpy().reshape((df_input.shape[0], 1, df_input.shape[1]))

    return df_input, input_data


def map_to_brightness(value):
    # For light predictions, map the model outputs to the range 0-3
    # Based on the observed outputs, the model seems to output values that need proper scaling
    # Using sigmoid-like mapping with thresholds for the 4 states
    if value < -0.5:
        return 0  # OFF
    elif value < 0.25:
        return 1  # LOW
    elif value < 0.75:
        return 2  # MEDIUM
    else:
        return 3  # HIGH


def process_predictions(predictions):
    # Apply the mapping function to light predictions
    lights_predictions = np.array([[map_to_brightness(val) for val in row[:8]] for row in predictions])

    # Denormalize and clip temperatures (20–30°C range)
    thermostats_predictions = predictions[:, 8:12] * 10.0 + 20.0
    thermostats_predictions = np.clip(thermostats_predictions, 20.0, 30.0)

    # Combine and round final predictions
    final_predictions = np.hstack((lights_predictions, thermostats_predictions))
    final_predictions = np.round(final_predictions, 2)
    final_predictions[final_predictions == -0.0] = 0.0  # Replace -0.0 if needed

    return final_predictions


def save_predictions(final_predictions, predictions_csv_path):
    # Print and save predictions
    print(f"Final Predictions (Rounded to 2 Decimal Points): {final_predictions}")
    predictions_df = pd.DataFrame(final_predictions, columns=["l1", "l2", "l3", "l4", "l5", "l6", "l7", "l8",
                                                              "t1", "t2", "t3", "t4"])
    predictions_df.to_csv(predictions_csv_path, index=False)
    print(f"Predictions saved to {predictions_csv_path}")


def main():
    project_path, model_h5_path, test_csv_path, predictions_csv_path = load_environment()
    model = load_model(model_h5_path)
    df_input, input_data = load_and_preprocess_data(test_csv_path)

    # Predict
    predictions = model.predict(input_data)

    # Debugging: Print input data and predictions
    print("Input Data (Normalized):")
    print(df_input)
    print("Model Predictions (Normalized):")
    print(predictions)

    final_predictions = process_predictions(predictions)
    save_predictions(final_predictions, predictions_csv_path)


if __name__ == "__main__":
    main()