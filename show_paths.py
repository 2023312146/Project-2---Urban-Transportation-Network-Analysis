from project_name.DJ import TransportNetwork

if __name__ == '__main__':
    network = TransportNetwork()
    
    # 从CSV加载数据
    network.load_stops_from_csv("D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\urban_transport_network_stops.csv")    # 对应EXCEL2数据
    network.load_routes_from_csv("D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\urban_transport_network_routes.csv")  # 对应EXCEL1数据
    
    print("所有路径及最短路径标注：")
    network.print_all_paths_with_shortest(1, 3)