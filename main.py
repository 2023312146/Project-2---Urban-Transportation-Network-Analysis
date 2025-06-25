from project.module.network import TransportNetwork
from project.algorithms.algorithms import dijkstra
import os

def main():
    # -- 构建相对于脚本位置的数据文件路径 --
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stops_file = os.path.join(script_dir, 'data', 'stops.csv')
    routes_file = os.path.join(script_dir, 'data', 'routes.csv')

    # 1. 从CSV加载网络
    print("正在加载交通网络...")
    try:
        network = TransportNetwork.load_stops_from_csv(stops_file)
        network.load_routes_from_csv(routes_file)
        print(f"网络加载成功。共加载 {len(network.stops)} 个站点和 {sum(len(routes) for routes in network.adjacency_list.values())} 条路线。")
    except FileNotFoundError as e:
        print(f"错误：找不到数据文件 {e.filename}。请检查文件路径。")
        return

    # 2. 定义起点和终点ID
    start_id = 1
    end_id = 5

    # 3. 获取Stop对象
    start_stop = network.get_stop_by_id(start_id)
    end_stop = network.get_stop_by_id(end_id)

    if not start_stop or not end_stop:
        print(f"错误：无法在网络中找到ID为 {start_id} 或 {end_id} 的站点。")
        return

    print(f"\n正在查找从 '{start_stop.name}' (ID: {start_id}) 到 '{end_stop.name}' (ID: {end_id}) 的最短路径...")

    # 4. 运行Dijkstra算法
    path, distance = dijkstra(network, start_stop, end_stop)

    # 5. 打印结果
    if path:
        print("\n----------- 查找结果 -----------")
        print(f"最短距离: {distance:.2f}")
        print("路径:")
        path_str = " -> ".join([stop.name for stop in path])
        print(path_str)
        print("---------------------------------")
    else:
        print("\n未找到从起点到终点的有效路径。")

if __name__ == '__main__':
    main()
