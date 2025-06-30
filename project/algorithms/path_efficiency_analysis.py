from typing import List, Dict, Any

# 计算路径效率

def calculate_efficiency(path_stops, total_distance, wait_times: dict, speed: float = 23.0) -> float:
    """
    计算路径效率
    :param path_stops: Stop对象列表
    :param total_distance: 路径总距离(km)
    :param wait_times: 各类型站点的等候时间字典
    :param speed: 行驶速度，默认23km/h
    :return: 效率值(km/h)
    """
    if len(path_stops) < 2:
        return 0.0
    wait_time = sum(
        wait_times.get(stop.zone_type, 3)
        for stop in path_stops[:-1]
    )
    travel_time = total_distance / speed
    total_time = travel_time + (wait_time / 60.0)
    return total_distance / total_time if total_time > 0 else 0.0

# 查找最高效路径

def find_most_efficient_path(all_paths: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    从所有路径中找出效率最高的路径
    :param all_paths: [{'path': [...], 'distance': ..., 'efficiency': ...}, ...]
    :return: 最高效路径的字典
    """
    if not all_paths:
        return {}
    return max(all_paths, key=lambda x: x['efficiency'])

# 比较最短路径和最高效路径

def compare_paths_by_efficiency_and_distance(
    dijkstra_path_stops,
    dijkstra_distance,
    all_paths: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    比较最短路径和最高效路径
    :param dijkstra_path_stops: 最短路径的Stop对象列表
    :param dijkstra_distance: 最短路径距离
    :param all_paths: 所有路径及其效率
    :return: 结果字典
    """
    if not all_paths:
        return None
    eff_path = find_most_efficient_path(all_paths)
    dijkstra_path = [s.stop_ID for s in dijkstra_path_stops] if dijkstra_path_stops else []
    return {
        'dijkstra_path': dijkstra_path,
        'dijkstra_distance': dijkstra_distance,
        'efficiency_path': eff_path.get('path', []),
        'efficiency_value': eff_path.get('efficiency', 0.0),
        'efficiency_distance': eff_path.get('distance', 0.0),
        'is_same': dijkstra_path == eff_path.get('path', [])
    } 