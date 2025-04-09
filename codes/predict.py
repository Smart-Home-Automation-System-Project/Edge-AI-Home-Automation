import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras

# Path to your saved model
model_h5_path = 'C:/Users/sahan/OneDrive/Desktop/Project/model.h5'

# Load the model without compiling (fixes the 'mse' issue)
print("✅ Model loaded.")
model = keras.models.load_model(model_h5_path, compile=False)

# Dummy test data based on your format (timestamp, day_of_week, hour, l1, l2, l3, t1, t2, t3)
test_data = [
    ['2025-03-31 00:00:00', 0, 0, 0, 0, 0, 20.08, 19.92, 21.32],
    ['2025-03-31 01:00:00', 0, 1, 0, 0, 0, 20.41, 21.6, 22.22],
    ['2025-03-31 02:00:00', 0, 2, 0, 0, 0, 21.45, 22.35, 21.99]
]

# Convert test data to DataFrame
df = pd.DataFrame(test_data, columns=['timestamp', 'day_of_week', 'hour', 'l1', 'l2', 'l3', 't1', 't2', 't3'])

# Drop timestamp
df = df.drop('timestamp', axis=1)

# Select input features
df_input = df[['l1', 'l2', 'l3', 't1', 't2', 't3']]

# Reshape input for LSTM: (samples, timesteps, features)
input_data = df_input.to_numpy().reshape((df_input.shape[0], 1, df_input.shape[1]))

# Predict
predictions = model.predict(input_data)

# Round lights to 0 or 1, thermostats to 2 decimal places
lights_predictions = np.round(predictions[:, :3])
thermostats_predictions = np.round(predictions[:, 3:], 2)

# Combine predictions
final_predictions = np.hstack((lights_predictions, thermostats_predictions))

# Replace -0.0 with 0.0
final_predictions[final_predictions == -0.0] = 0.0

# Display
print(f"✅ Predictions: {final_predictions}")

# Save to CSV
predictions_df = pd.DataFrame(final_predictions, columns=["l1", "l2", "l3", "t1", "t2", "t3"])
predictions_df.to_csv(r'C:\Users\sahan\OneDrive\Desktop\Project\predictions.csv', index=False)
print("✅ Predictions saved to predictions.csv")
