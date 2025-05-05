import sqlite3
from datetime import date
from dotenv import load_dotenv  # Correct import for dotenv
import pymongo
import os

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection string from environment variables
MONGO_DB = os.getenv("MONGO_DB")

today = date.today()
yesterday = today.replace(day=today.day-1)

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

def upload_to_mongodb(list):            
    myclient = pymongo.MongoClient(MONGO_DB)
    mydb = myclient["sensor_data"]
    mycol = mydb["database1"]

    # mycol.insert_one({"test":"this is a test"})
    
    mycol.insert_one(list)
    
if __name__ == '__main__':
    sensor_data = return_sensor_data_yesterday()
    
    tag_sensor_data_for_yesterday = {f"{yesterday}":sensor_data}
    
    # for data in sensor_data:
    #     print(data)
    
    if sensor_data is not None:
        upload_to_mongodb(tag_sensor_data_for_yesterday)
    else:
        print("No data was uploaded")
