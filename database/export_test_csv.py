import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch the project path from the environment variables
project_path = os.getenv("PATH_TO_PROJECT")

# === ONLY CHANGE ABSOLUTE PATHS ===
# Absolute paths
csv_path = os.path.join(project_path, 'test.csv')


# Function to get the latest row from the sensor_data table
def get_latest_row_from_db():
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()

    # Query to get the latest row based on the timestamp (most recent entry)
    query = '''
    SELECT * FROM sensor_data
    ORDER BY timestamp DESC LIMIT 1
    '''

    # Execute the query and fetch the latest row
    cursor.execute(query)
    latest_row = cursor.fetchone()

    # Close the connection
    conn.close()

    return latest_row


# Function to save the latest row into a CSV file at the specified path
def save_to_csv(latest_row):
    # Convert the latest row to a DataFrame
    df = pd.DataFrame([latest_row], columns=['timestamp', 'day_of_week', 'hour', 'l1', 'l2', 'l3', 't1', 't2', 't3'])

    # Write the DataFrame to a CSV file in the specified path
    df.to_csv(csv_path, index=False)
    print("✅ Latest row saved to test.csv")


# Main execution
if __name__ == "__main__":
    # Get the latest row from the database
    latest_row = get_latest_row_from_db()

    if latest_row:
        # Save the latest row to test.csv
        save_to_csv(latest_row)
    else:
        print("❌ No data found in the database.")
