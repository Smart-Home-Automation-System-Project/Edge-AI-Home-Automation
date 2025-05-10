# delete_tables.py

import sqlite3


def clear_sensor_data_table(db_name="database1.db"):
    conn = None # Ensure conn is defined in the outer scope for the finally block
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sensor_data")
        conn.commit()
        print(f"All data deleted from 'sensor_data' table in {db_name}.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    clear_sensor_data_table()
