"""
Set a cron job to run every Sunday at 11.59 PM.
But for demonstration run every 10s or 20s or just make it run only once.
"""

import os
import pandas as pd
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv


def load_environment():
    # Load environment variables from the .env file
    load_dotenv()

    # Retrieve the project path from environment variable
    project_path = os.getenv('PATH_TO_PROJECT')
    return project_path


def load_and_preprocess_data(project_path):
    # === Load CSV ===
    data_path = os.path.join(project_path, 'train.csv')  # train data path
    df = pd.read_csv(data_path)

    # === Normalize time features ===
    df['hour'] = df['hour'] / 23.0  # Normalize hour (0–23 → 0–1)
    df['day_of_week'] = df['day_of_week'] / 6.0  # Normalize day (0–6 → 0–1)

    df['t1'] = (df['t1'] - 20) / 10.0
    df['t2'] = (df['t2'] - 20) / 10.0
    df['t3'] = (df['t3'] - 20) / 10.0
    df['t4'] = (df['t4'] - 20) / 10.0

    # === Select input features ===
    features = ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 't1', 't2', 't3', 't4', 'hour', 'day_of_week']
    target_features = ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 't1', 't2', 't3', 't4']

    # === Convert to numpy ===
    data = df[features].values.astype(np.float32)

    return data, features, target_features


def prepare_sequences(data, features):
    SEQ_LEN = 24  # Use last 24 hours for prediction
    X, y = [], []

    for i in range(len(data) - SEQ_LEN):
        X.append(data[i:i + SEQ_LEN])  # 24 hours of data
        y.append(data[i + SEQ_LEN][:12])  # Predict next hour's light/temp only

    X = np.array(X)
    y = np.array(y)

    return X, y, SEQ_LEN


def create_lstm_model(SEQ_LEN, features):
    # === Define LSTM model ===
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(SEQ_LEN, len(features))),
        tf.keras.layers.LSTM(64, return_sequences=False),
        tf.keras.layers.Dense(12, activation='linear')  # 6 outputs: l1–l3, t1–t3
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
    data, features, target_features = load_and_preprocess_data(project_path)
    X, y, SEQ_LEN = prepare_sequences(data, features)
    model = create_lstm_model(SEQ_LEN, features)
    model = train_model(model, X, y)
    save_model(model, project_path)


if __name__ == "__main__":
    main()