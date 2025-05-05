import os
import sqlite3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import date


today = date.today()
yesterday = today.replace(day=today.day-1)

def upload_to_firestore(data):
    # Dynamically determine the absolute path of the credentials file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cred_path = os.path.join(current_dir, "edgeaihomeauto-firebase-adminsdk-fbsvc-e3ff352f44.json")  # Updated file name

    cred = credentials.Certificate(cred_path)
    app = firebase_admin.initialize_app(cred)

    db = firestore.client()

    doc_ref = db.collection("sensor_data").document(f"{yesterday}")
    doc_ref.set(data)

    db.close()
    
def return_sensor_data_yesterday():
    try:
        conn = sqlite3.connect('database1.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()


        # print(today)

        '''
            This is the actual query for sending a days data. 
            Should assign a cron job to run after the day has ended.
        '''
        # query = f"select * from sensor_data where timestamp like '{yesterday}'"

        """
            This is for testing only
        """
        query = "select * from sensor_data"
        
        
        # Execute query
        cursor.execute(query)

        # Fetch the result
        result = [dict(row) for row in cursor.fetchall()]
        if not result:
            result = None
        
        
    finally:
        if conn:
            conn.close()
            print("Connection closed!")
        return result

if __name__ == '__main__':
    sensor_data = return_sensor_data_yesterday()
    
    tag_sensor_data_for_yesterday = {"sensor":sensor_data}
    
    # for data in sensor_data:
    #     print(data)
    
    if sensor_data is not None:
        upload_to_firestore(tag_sensor_data_for_yesterday)
    else:
        print("No data was uploaded")
