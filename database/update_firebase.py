import sqlite3
from datetime import date

today = date.today()

try:
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()


    # print(today)

    query = f"select sensor_data where timestamp like '{today}'"

    # Execute query
    cursor.execute(query)

    # Fetch the result
    result = cursor.fetchall()
    
    
finally:
    if conn:
        conn.close()
        print("Connection closed!")