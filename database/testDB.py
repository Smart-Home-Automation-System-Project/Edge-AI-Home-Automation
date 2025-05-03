import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    while True:
        try:
            query = input("Enter query: ")
            cursor.execute(query)
            result = cursor.fetchall()
            print(result)
        except (sqlite3.Error, KeyboardInterrupt) as e:
            print("Error occurred:", e)
            break
finally:
    if conn:
        conn.close()
        print("Connection closed!")


#  select * from sensor_data where timestamp like '2025-04-20%';