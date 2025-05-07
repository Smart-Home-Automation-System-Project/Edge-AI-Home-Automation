import sqlite3
from datetime import date, timedelta
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

today = date.today()

def fetch_sensor_data_week():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cred_path = os.path.join(current_dir, "edgeaihomeauto-firebase-adminsdk-fbsvc-e3ff352f44.json")  # Updated file name

    cred = credentials.Certificate(cred_path)
    app = firebase_admin.initialize_app(cred)
    
    
    db = firestore.client()
    
    # Run backwords 7 days and fetch all days
    for i in range(1,8):
        head = today - timedelta(days=i)
        doc_ref = db.collection("sensor_data").document(f"{head}")
        doc = doc_ref.get()
        
        if doc.exists:
            # One day at a time is reupdated
            write_data_to_local_db(doc.to_dict()["sensor"])
        else:
            print(f"No document found for date: {head}")
            
            
def write_data_to_local_db(data):
    try:
        conn =sqlite3.connect('database1.db')
        cursor = conn.cursor()
        
        query = "insert into sensor_data (sensor_id, timestamp, sensor_value) values "
    
        for row in data:
            # Here the data only entered for missing sensor_id + timestamp
            cursor.execute(
                "INSERT OR IGNORE INTO sensor_data (sensor_id, timestamp, sensor_value) VALUES (?, ?, ?)",
                (row['sensor_id'], row['timestamp'], float(row['sensor_value']))
            )
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    
    finally:
        if conn:
            conn.close()
            print("Connection closed!")

if __name__ == '__main__':
    fetch_sensor_data_week()