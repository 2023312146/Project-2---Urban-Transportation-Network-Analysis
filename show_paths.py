from project_name.module.network import TransportNetwork
from project_name.io import load_stops_from_csv, load_routes_from_csv
from project_name.algorithms import find_all_paths

if __name__ == '__main__':
    network = TransportNetwork()
    
    # 从您指定的CSV文件路径加载数据
    stops_file = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\urban_transport_network_stops.csv"
    routes_file = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\urban_transport_network_routes.csv"
    
    try:
        load_stops_from_csv(network, stops_file)
        load_routes_from_csv(network, routes_file)
    except FileNotFoundError as e:
        print(f"错误：找不到数据文件 - {e}")
        print("请确认文件路径是否正确。")
        exit()

    start_stop_id = 1
    end_stop_id = 5
    
    # 检查起点和终点是否存在
    if start_stop_id not in network.stops or end_stop_id not in network.stops:
        print(f"错误：起始站点 {start_stop_id} 或终点站 {end_stop_id} 不在网络中。")
        exit()

    print("所有路径及最短路径标注：")
    
    all_paths = find_all_paths(network, start_stop_id, end_stop_id)

    if not all_paths:
        print(f"未找到从站点 {start_stop_id} 到站点 {end_stop_id} 的路径。")
    else:
        min_distance = min(dist for _, dist in all_paths)
        for path, dist in all_paths:
            mark = " <--- shortest" if abs(dist - min_distance) < 1e-9 else ""
            print(f"Path: {path}, Distance: {dist:.2f}{mark}")