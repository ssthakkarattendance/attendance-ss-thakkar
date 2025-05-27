from math import radians, cos, sin, asin, sqrt

def is_within_radius(user_lat, user_lon, office_lat, office_lon, max_distance_m=100):
    # Convert degrees to radians
    user_lat, user_lon, office_lat, office_lon = map(radians, [user_lat, user_lon, office_lat, office_lon])

    # Haversine formula
    dlon = office_lon - user_lon
    dlat = office_lat - user_lat
    a = sin(dlat / 2)**2 + cos(user_lat) * cos(office_lat) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    earth_radius = 6371000  # meters

    distance = c * earth_radius
    return distance <= max_distance_m
