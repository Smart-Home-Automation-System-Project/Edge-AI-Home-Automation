import os
import pandas as pd
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the project path from environment variable
project_path = os.getenv('PATH_TO_PROJECT')

# === Load CSV ===
data_path = os.path.join(project_path, 'train.csv')  # train data path
df = pd.read_csv(data_path)

# === Normalize time features ===
df['hour'] = df['hour'] / 23.0             # Normalize hour (0–23 → 0–1)
df['day_of_week'] = df['day_of_week'] / 6.0  # Normalize day (0–6 → 0–1)

df['t1'] = (df['t1'] - 20) / 10.0
df['t2'] = (df['t2'] - 20) / 10.0
df['t3'] = (df['t3'] - 20) / 10.0

# === Select input features ===
features = ['l1', 'l2', 'l3', 't1', 't2', 't3', 'hour', 'day_of_week']
target_features = ['l1', 'l2', 'l3', 't1', 't2', 't3']

# === Convert to numpy ===
data = df[features].values.astype(np.float32)

SEQ_LEN = 24  # Use last 24 hours for prediction
X, y = [], []

for i in range(len(data) - SEQ_LEN):
    X.append(data[i:i + SEQ_LEN])  # 24 hours of data
    y.append(data[i + SEQ_LEN][:6])  # Predict next hour's light/temp only

X = np.array(X)
y = np.array(y)

# === Define LSTM model ===
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(SEQ_LEN, len(features))),
    tf.keras.layers.LSTM(64, return_sequences=False),
    tf.keras.layers.Dense(6, activation='linear')  # 6 outputs: l1–l3, t1–t3
])

model.compile(optimizer='adam', loss='mse')

# === Train ===
model.fit(X, y, epochs=10, batch_size=32)

# === Save .h5 model ===
model_save_path = os.path.join(project_path, 'model.h5')
model.save(model_save_path)
