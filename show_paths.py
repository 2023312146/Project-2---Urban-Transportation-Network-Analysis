from project.module.network import TransportNetwork
from project.module.get_from_csv import load_stops_from_csv, load_routes_from_csv
from project.algorithms.algorithms import find_all_paths

if __name__ == '__main__':
    network = TransportNetwork()
    
    # 从您指定的CSV文件路径加载数据
    stops_file = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_stops.csv"
    routes_file = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_routes.csv"
    
    try:
        load_stops_from_csv(network, stops_file)
        print("已加载站点ID：", list(network.stops.keys()))
        load_routes_from_csv(network, routes_file)
    except FileNotFoundError as e:
        print(f"错误：找不到数据文件 - {e}")
        print("请确认文件路径是否正确。")
        exit()

    start_stop_id = 1
    end_stop_id = 5
    
    # 获取Stop对象而不是ID
    start_stop = network.stops.get(start_stop_id)
    end_stop = network.stops.get(end_stop_id)
    
    # 检查起点和终点是否存在
    if start_stop is None or end_stop is None:
        print(f"错误：起始站点 {start_stop_id} 或终点站 {end_stop_id} 不在网络中。")
        exit()

    print("所有路径及最短路径标注：")
    
    all_paths = find_all_paths(network, start_stop, end_stop)

    if not all_paths:
        print(f"未找到从站点 {start_stop_id} 到站点 {end_stop_id} 的路径。")
    else:
        min_distance = min(dist for _, dist in all_paths)
        for path, dist in all_paths:
            # 将Stop对象转换为ID显示
            path_ids = [stop.stop_id for stop in path]
            mark = " <--- shortest" if abs(dist - min_distance) < 1e-9 else ""
            print(f"Path: {path_ids}, Distance: {dist:.2f}{mark}")