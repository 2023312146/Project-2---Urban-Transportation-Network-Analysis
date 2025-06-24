from project_name.DJ import TransportNetwork

if __name__ == '__main__':
    network = TransportNetwork()
    for stop_id in [1, 2, 3]:
        network.add_stop(stop_id)
    network.add_route(1, 2, 5)
    network.add_route(2, 3, 10)
    network.add_route(1, 3, 20)
    print("所有路径及最短路径标注：")
    network.print_all_paths_with_shortest(1, 3)
