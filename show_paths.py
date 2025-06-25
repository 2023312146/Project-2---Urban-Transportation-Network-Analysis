from project.module.network import TransportNetwork
from project.module.get_from_csv import load_stops_from_csv, load_routes_from_csv
from project.algorithms.algorithms import find_all_paths

def get_all_paths_and_print(stops_file, routes_file, start_stop_id, end_stop_id):
    """
    加载站点和路线数据，查找并打印两个站点之间的所有路径。
    """
    network = TransportNetwork()
    
    try:
        load_stops_from_csv(network, stops_file)
        # 打印加载的站点用于调试
        # print("已加载站点ID：", list(network.stops.keys()))
        load_routes_from_csv(network, routes_file)
    except FileNotFoundError as e:
        print(f"错误：找不到数据文件 - {e}")
        print("请确认文件路径是否正确。")
        return None

    start_stop = network.stops.get(start_stop_id)
    end_stop = network.stops.get(end_stop_id)
    
    if start_stop is None or end_stop is None:
        print(f"错误：起始站点 {start_stop_id} 或终点站 {end_stop_id} 不在网络中。")
        return None

    all_paths = find_all_paths(network, start_stop, end_stop)

    if not all_paths:
        print(f"未找到从站点 {start_stop_id} 到站点 {end_stop_id} 的路径。")
    else:
        print("All paths & the shortest path：")
        min_distance = min(dist for _, dist in all_paths)
        for path, dist in all_paths:
            path_ids = [stop.stop_ID for stop in path]
            mark = " <--- shortest" if abs(dist - min_distance) < 1e-9 else ""
            print(f"Path: {path_ids}, Distance: {dist:.2f}{mark}")
            
    return all_paths