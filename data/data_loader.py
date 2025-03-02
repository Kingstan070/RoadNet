import sqlite3
import json

def create_database():
    conn = sqlite3.connect('road_monitoring.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS road_conditions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            video_creation_time TEXT NOT NULL,
            road_type TEXT NOT NULL,
            road_condition TEXT NOT NULL,
            pothole_data TEXT NOT NULL,
            frame_base64 TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_data(data):
    try:
        conn = sqlite3.connect('road_monitoring.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO road_conditions (latitude, longitude, video_creation_time, road_type, road_condition, pothole_data, frame_base64)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['latitude'],
            data['longitude'],
            data['video_creation_time'],
            data['road_type'],
            data['road_condition'],
            json.dumps(data['pothole_data']),
            data['frame_base64']
        ))
        conn.commit()
        conn.close()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")

create_database()