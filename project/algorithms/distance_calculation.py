from project.algorithms.coordinate_utils import CoordinateUtils

# 为了向后兼容，保留原函数名但使用CoordinateUtils实现
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    return CoordinateUtils.calculate_haversine_distance(lat1, lon1, lat2, lon2)

def calculate_distance_between_stops(stop1, stop2):
    return CoordinateUtils.calculate_distance_between_stops(stop1, stop2)

def calculate_distance_between_stops_by_id(data_manager, stop1_id, stop2_id):
    return CoordinateUtils.calculate_distance_between_stops_by_id(data_manager, stop1_id, stop2_id) 