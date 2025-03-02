import sqlite3
import json
from datetime import datetime
from geopy.distance import geodesic

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

def retrieve_routes():
    conn = sqlite3.connect('road_monitoring.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM road_conditions')
    rows = cursor.fetchall()
    conn.close()

    routes = {}
    for row in rows:
        route_key = row[3]  # video_creation_time
        if route_key not in routes:
            routes[route_key] = []
        routes[route_key].append({
            'latitude': row[1],
            'longitude': row[2],
            'video_creation_time': row[3],
            'road_type': row[4],
            'road_condition': row[5],
            'pothole_data': json.loads(row[6]),
            'frame_base64': row[7]
        })

    # Process routes to handle intersections and prioritize recent data
    processed_routes = []
    for route_key, points in routes.items():
        points.sort(key=lambda x: datetime.strptime(x['video_creation_time'], '%Y-%m-%d %H:%M:%S'))
        processed_routes.append(points)

    # Flatten the list of routes
    all_points = [point for route in processed_routes for point in route]

    # Handle intersections with a 10m approximation
    final_points = []
    for point in all_points:
        is_new_point = True
        for final_point in final_points:
            distance = geodesic((point['latitude'], point['longitude']), (final_point['latitude'], final_point['longitude'])).meters
            if distance < 10:
                if datetime.strptime(point['video_creation_time'], '%Y-%m-%d %H:%M:%S') > datetime.strptime(final_point['video_creation_time'], '%Y-%m-%d %H:%M:%S'):
                    final_points.remove(final_point)
                    final_points.append(point)
                is_new_point = False
                break
        if is_new_point:
            final_points.append(point)

    return final_points

create_database()