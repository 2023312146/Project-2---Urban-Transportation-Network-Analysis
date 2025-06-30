from project.data_structures.stop import Stop
from project.data_structures.network import TransportNetwork

def find_all_paths(network: TransportNetwork, start_stop: Stop, end_stop: Stop, path=None, distance=0):
    """
    使用深度优先搜索递归查找两个站点之间的所有可能路径。

    :param network: TransportNetwork 对象
    :param start_stop: 起始 Stop 对象
    :param end_stop: 终点 Stop 对象
    :param path: 当前路径 (内部递归使用)
    :param distance: 当前距离 (内部递归使用)
    :return: 一个包含元组(路径, 距离)的列表。
    """
    if path is None:
        path = []
    path = path + [start_stop]

    if start_stop == end_stop:
        return [(path, distance)]

    if start_stop not in network.adjacency_list:
        return []

    all_paths = []
    for neighbor, weight in network.adjacency_list[start_stop]:
        if neighbor not in path:
            new_paths = find_all_paths(network, neighbor, end_stop, path, distance + weight)
            for p in new_paths:
                all_paths.append(p)
    return all_paths 