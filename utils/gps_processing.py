def calculate_distance(coord1, coord2):
    # Calculate the distance between two GPS coordinates using the Haversine formula
    from math import radians, sin, cos, sqrt, atan2

    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Radius of Earth in kilometers (use 3956 for miles)
    radius = 6371.0
    distance = radius * c

    return distance

def filter_gps_data(gps_data, start_time, end_time):
    # Filter GPS data based on a time range
    filtered_data = [entry for entry in gps_data if start_time <= entry['timestamp'] <= end_time]
    return filtered_data

def convert_gps_to_decimal(degree, minutes, seconds, direction):
    # Convert GPS coordinates from degrees, minutes, seconds to decimal format
    decimal = degree + (minutes / 60) + (seconds / 3600)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

# This file is intentionally left blank.