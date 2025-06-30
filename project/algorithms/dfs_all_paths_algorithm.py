from project.data_structures.stop_entity import Stop
from project.data_structures.transport_network_structure import TransportNetwork

def find_all_paths(network: TransportNetwork, start_stop, end_stop, path=None, distance=0):
    """
    使用深度优先搜索递归查找两个站点之间的所有可能路径。
    :param network: TransportNetwork 对象
    :param start_stop: 起始 Stop 对象或stop_ID
    :param end_stop: 终点 Stop 对象或stop_ID
    :param path: 当前路径 (内部递归使用)
    :param distance: 当前距离 (内部递归使用)
    :return: 一个包含元组(路径, 距离)的列表。
    """
    start_id = start_stop.stop_ID if isinstance(start_stop, Stop) else start_stop
    end_id = end_stop.stop_ID if isinstance(end_stop, Stop) else end_stop
    if path is None:
        path = []
    path = path + [start_id]

    if start_id == end_id:
        # 返回Stop对象路径
        return [([network.get_stop_by_id(pid) for pid in path], distance)]

    if start_id not in network.adjacency_list:
        return []

    all_paths = []
    for neighbor_id, weight in network.adjacency_list[start_id]:
        if neighbor_id not in path:
            new_paths = find_all_paths(network, neighbor_id, end_id, path, distance + weight)
            for p in new_paths:
                all_paths.append(p)
    return all_paths 