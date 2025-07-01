from math import sin, cos, sqrt, atan2, radians

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # 经纬度差
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    # 哈弗辛公式
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance

def calculate_distance_between_stops(stop1, stop2):
    return calculate_haversine_distance(
        stop1['lat'], stop1['lon'],
        stop2['lat'], stop2['lon']
    )

def calculate_distance_between_stops_by_id(data_manager, stop1_id, stop2_id):
    if stop1_id in data_manager.stations and stop2_id in data_manager.stations:
        stop1 = data_manager.stations[stop1_id]
        stop2 = data_manager.stations[stop2_id]
        return calculate_distance_between_stops(stop1, stop2)
    return 0 