"""
Set a cron job to run every Sunday at 11.59 PM.
But for demonstration run every 10s or 20s or just make it run only once.
"""

import os
import pandas as pd
import numpy as np
import tensorflow as tf
import sys

# Add database directory to path to import database module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.database import db_get_sensor_types, db_get_sensors_by_category, db_get_all_sensor_data

def load_and_preprocess_data():
    # Get all sensor data from the database
    all_sensor_data = db_get_all_sensor_data(days=14)  # Get 2 weeks of data

    # Separate light and temp sensors
    light_sensors = [name for name, info in all_sensor_data.items() if info['category'] == 'light']
    temp_sensors = [name for name, info in all_sensor_data.items() if info['category'] == 'temp']

    # Create a dataframe with all timestamps
    all_timestamps = set()
    for sensor_name, info in all_sensor_data.items():
        for timestamp, _ in info['data']:
            all_timestamps.add(timestamp)

    # Create dataframe with all timestamps
    df = pd.DataFrame(sorted(all_timestamps), columns=['timestamp'])

    # Add sensor data to dataframe
    for sensor_name, info in all_sensor_data.items():
        # Convert sensor data to dictionary for easy lookup
        sensor_dict = {timestamp: value for timestamp, value in info['data']}

        # Add sensor data to dataframe
        df[sensor_name] = df['timestamp'].map(sensor_dict)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Extract time features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek

    # Normalize time features
    df['hour'] = df['hour'] / 23.0  # Normalize hour (0–23 → 0–1)
    df['day_of_week'] = df['day_of_week'] / 6.0  # Normalize day (0–6 → 0–1)

    # Normalize temperature data dynamically
    for sensor in temp_sensors:
        # Use mean and std for normalization instead of hardcoded values
        mean_temp = df[sensor].mean()
        std_temp = df[sensor].std()
        if std_temp == 0:  # Prevent division by zero
            std_temp = 1.0
        df[sensor] = (df[sensor] - mean_temp) / std_temp

    # Drop rows with missing values
    df = df.dropna()

    # Define features dynamically based on available sensors
    features = light_sensors + temp_sensors + ['hour', 'day_of_week']
    target_features = light_sensors + temp_sensors

    # Convert to numpy
    data = df[features].values.astype(np.float32)

    return data, features, target_features


def prepare_sequences(data, features, target_features):
    SEQ_LEN = 24  # Use last 24 hours for prediction
    X, y = [], []

    for i in range(len(data) - SEQ_LEN):
        X.append(data[i:i + SEQ_LEN])  # 24 hours of data

        # Get indices of target features
        target_indices = [features.index(feature) for feature in target_features]

        # Extract target values using indices
        target_values = [data[i + SEQ_LEN][idx] for idx in target_indices]

        y.append(target_values)

    X = np.array(X)
    y = np.array(y)

    return X, y, SEQ_LEN


def create_lstm_model(SEQ_LEN, features, target_features):
    # Define LSTM model with dynamic output size
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(SEQ_LEN, len(features))),
        tf.keras.layers.LSTM(64, return_sequences=False),
        tf.keras.layers.Dense(len(target_features), activation='linear')
    ])

    model.compile(optimizer='adam', loss='mse')
    return model


def train_model(model, X, y):
    # Train
    model.fit(X, y, epochs=10, batch_size=32)
    return model


def save_model(model):
    # Save .h5 model
    ai_folder = os.path.dirname(__file__)
    model_save_path = os.path.join(ai_folder, 'model_new.h5')
    model.save(model_save_path)
    print(f"Model saved at: {model_save_path}")


def main():
    data, features, target_features = load_and_preprocess_data()
    X, y, SEQ_LEN = prepare_sequences(data, features, target_features)
    model = create_lstm_model(SEQ_LEN, features, target_features)
    model = train_model(model, X, y)
    save_model(model)

if __name__ == "__main__":
    main()