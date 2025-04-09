import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras

# Path to your saved model
model_h5_path = 'C:/Users/sahan/OneDrive/Desktop/Project/model.h5'
test_csv_path = 'C:/Users/sahan/OneDrive/Desktop/Project/test.csv'

# Load the model without compiling (fixes the 'mse' issue)
print("✅ Model loaded.")
model = keras.models.load_model(model_h5_path, compile=False)

# === Load test input from CSV ===
df = pd.read_csv(test_csv_path)

# Drop timestamp (not used as input for the model)
df = df.drop('timestamp', axis=1)

# Normalize hour (0–23 → 0–1) and day_of_week (0–6 → 0–1)
df['hour'] = df['hour'] / 23.0
df['day_of_week'] = df['day_of_week'] / 6.0

# Select input features for the model
df_input = df[['l1', 'l2', 'l3', 't1', 't2', 't3', 'hour', 'day_of_week']]

# Reshape input for LSTM: (samples, timesteps, features)
input_data = df_input.to_numpy().reshape((df_input.shape[0], 1, df_input.shape[1]))

# Predict
predictions = model.predict(input_data)

# Debugging: Print input data and predictions
print("Input Data (Normalized):")
print(df_input)
print("Model Predictions (Normalized):")
print(predictions)

# Round light predictions to 0 or 1
lights_predictions = np.round(predictions[:, :3])  # l1, l2, l3

# Denormalize and clip temperatures (20–30°C range)
thermostats_predictions = predictions[:, 3:] * 10.0 + 20.0
thermostats_predictions = np.clip(thermostats_predictions, 20.0, 30.0)

# Combine and round final predictions
final_predictions = np.hstack((lights_predictions, thermostats_predictions))
final_predictions = np.round(final_predictions, 2)
final_predictions[final_predictions == -0.0] = 0.0  # Replace -0.0 if needed

# Print and save predictions
print(f"✅ Final Predictions (Rounded to 2 Decimal Points): {final_predictions}")
predictions_df = pd.DataFrame(final_predictions, columns=["l1", "l2", "l3", "t1", "t2", "t3"])
predictions_df.to_csv(r'C:\Users\sahan\OneDrive\Desktop\Project\predictions.csv', index=False)
print("✅ Predictions saved to predictions.csv")
