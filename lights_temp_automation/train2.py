"""
Set a cron job to run every Sunday at 11.59 PM.
But for demonstration run every 10s or 20s or just make it run only once.
"""

import os
import pandas as pd
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta
from database.database import db_get_light_sensors, db_get_temp_sensors, db_get_sensor_data

def load_environment():
    # Load environment variables from the .env file
    load_dotenv()

    # Retrieve the project path from environment variable
    project_path = os.getenv('PATH_TO_PROJECT')
    return project_path


# def get_sensor_data_from_db(project_path):
#     # Path to the database
#     db_path = os.path.join(project_path, 'database', 'database.db')
#
#     # Connect to the database
#     conn = sqlite3.connect(db_path)
#
#     # First, get the light and temperature sensor IDs
#     cursor = conn.cursor()
#
#     # Get all light sensors
#     cursor.execute("""
#         SELECT id, name FROM sensors
#         WHERE catagory = 'light'
#     """)
#     light_sensors = {row[1]: row[0] for row in cursor.fetchall()}
#
#     # Get all temperature sensors
#     cursor.execute("""
#         SELECT id, name FROM sensors
#         WHERE catagory = 'temp'
#     """)
#     temp_sensors = {row[1]: row[0] for row in cursor.fetchall()}
#
#     # Calculate the timeframe for data retrieval (e.g., past week)
#     end_time = datetime.now()
#     start_time = end_time - timedelta(days=7)
#
#     # Format timestamps for SQL query
#     start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
#     end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
#
#     # Create a dataframe to store the sensor data with timestamps
#     data = []
#
#     # For each hour in the timeframe
#     current_time = start_time
#     while current_time <= end_time:
#         # Store numerical values for hour and day of week instead of datetime
#         hour_data = {
#             'hour': current_time.hour,
#             'day_of_week': current_time.weekday()
#         }
#
#         time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
#
#         # Get data for each light sensor
#         for sensor_name, sensor_id in light_sensors.items():
#             cursor.execute("""
#                 SELECT sensor_value FROM sensor_data
#                 WHERE sensor_id = ? AND timestamp = ?
#             """, (sensor_id, time_str))
#             result = cursor.fetchone()
#             hour_data[sensor_name] = result[0] if result else 0
#
#         # Get data for each temperature sensor
#         for sensor_name, sensor_id in temp_sensors.items():
#             cursor.execute("""
#                 SELECT sensor_value FROM sensor_data
#                 WHERE sensor_id = ? AND timestamp = ?
#             """, (sensor_id, time_str))
#             result = cursor.fetchone()
#             hour_data[sensor_name] = result[0] if result else 20  # Default to 20°C if no data
#
#         data.append(hour_data)
#         current_time += timedelta(hours=1)
#
#     conn.close()
#
#     # Convert to dataframe
#     df = pd.DataFrame(data)
#
#     # Handle any missing values
#     df = df.ffill()  # Forward fill
#     df = df.bfill()  # Backward fill for any remaining NaNs
#
#     return df
def get_sensor_data_from_db():
    # Get sensor mapping from database
    light_sensors = db_get_light_sensors()
    temp_sensors = db_get_temp_sensors()

    # Calculate the timeframe for data retrieval
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    # Create a dataframe to store the sensor data
    data = []

    # For each hour in the timeframe
    current_time = start_time
    while current_time <= end_time:
        hour_data = {
            'hour': current_time.hour,
            'day_of_week': current_time.weekday()
        }

        time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

        # Get data for each light sensor
        for sensor_name, sensor_id in light_sensors.items():
            sensor_value = db_get_sensor_data(sensor_id, time_str)
            hour_data[sensor_name] = sensor_value if sensor_value is not None else 0

        # Get data for each temperature sensor
        for sensor_name, sensor_id in temp_sensors.items():
            sensor_value = db_get_sensor_data(sensor_id, time_str)
            hour_data[sensor_name] = sensor_value if sensor_value is not None else 20

        data.append(hour_data)
        current_time += timedelta(hours=1)

    # Convert to dataframe
    df = pd.DataFrame(data)
    df = df.ffill().bfill()  # Handle missing values

    return df

def preprocess_data(df):
    # === Normalize time features ===
    df['hour'] = df['hour'] / 23.0  # Normalize hour (0–23 → 0–1)
    df['day_of_week'] = df['day_of_week'] / 6.0  # Normalize day (0–6 → 0–1)

    # Get all temperature sensor columns
    temp_columns = [col for col in df.columns if col.startswith('t')]

    # Normalize temperature values
    for col in temp_columns:
        df[col] = (df[col] - 20) / 10.0

    # === Select input features ===
    light_columns = [col for col in df.columns if col.startswith('l')]
    features = light_columns + temp_columns + ['hour', 'day_of_week']
    target_features = light_columns + temp_columns

    # === Convert to numpy ===
    data = df[features].values.astype(np.float32)

    return data, features, target_features


def prepare_sequences(data, features):
    SEQ_LEN = 24  # Use last 24 hours for prediction
    X, y = [], []

    for i in range(len(data) - SEQ_LEN):
        X.append(data[i:i + SEQ_LEN])  # 24 hours of data
        # Get the number of target features (lights + temps)
        num_targets = len([f for f in features if f.startswith('l') or f.startswith('t')])
        y.append(data[i + SEQ_LEN][:num_targets])  # Predict next hour's light/temp only

    X = np.array(X)
    y = np.array(y)

    return X, y, SEQ_LEN


def create_lstm_model(SEQ_LEN, features, num_targets):
    # === Define LSTM model ===
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(SEQ_LEN, len(features))),
        tf.keras.layers.LSTM(64, return_sequences=False),
        tf.keras.layers.Dense(num_targets, activation='linear')  # outputs: lights + temperatures
    ])

    model.compile(optimizer='adam', loss='mse')
    return model


def train_model(model, X, y):
    # === Train ===
    model.fit(X, y, epochs=10, batch_size=32)
    return model


def save_model(model, project_path):
    # === Save .h5 model ===
    model_save_path = os.path.join(project_path, 'model.h5')
    model.save(model_save_path)


def main():
    project_path = load_environment()

    # Get data from database instead of CSV
    df = get_sensor_data_from_db(project_path)

    # Check if we have enough data to train
    if len(df) < 25:  # Need at least SEQ_LEN + 1 rows
        print("Not enough data in the database. Need at least 25 time points.")
        return

    # Preprocess the data
    data, features, target_features = preprocess_data(df)

    # Prepare sequences for LSTM
    X, y, SEQ_LEN = prepare_sequences(data, features)

    # Count the number of target features for the model output layer
    num_targets = len(target_features)

    # Create and train the model
    model = create_lstm_model(SEQ_LEN, features, num_targets)
    model = train_model(model, X, y)

    # Save the trained model
    save_model(model, project_path)


if __name__ == "__main__":
    main()