import heapq
from project.module.stop import Stop
from project.module.network import TransportNetwork

def dijkstra(network: TransportNetwork, start_stop: Stop, end_stop: Stop):
    """
    使用Dijkstra算法查找两个站点之间的最短路径。
    使用列表代替heapq实现优先队列

    :param network: TransportNetwork 对象
    :param start_stop: 起始 Stop 对象
    :param end_stop: 终点 Stop 对象
    :return: 一个元组，包含最短路径（Stop对象列表）和总距离。如果找不到路径，则返回(None, float('inf'))。
    """
    if start_stop not in network.adjacency_list or end_stop not in network.adjacency_list:
        return None, float('inf')

    distances = {stop: float('inf') for stop in network.adjacency_list}
    previous_stops = {stop: None for stop in network.adjacency_list}
    distances[start_stop] = 0
    
    # 使用普通列表代替优先队列
    queue = [(0, start_stop)]

    while queue:
        # 手动查找队列中距离最小的元素
        min_index = 0
        for i in range(1, len(queue)):
            if queue[i][0] < queue[min_index][0]:
                min_index = i
        current_distance, current_stop = queue.pop(min_index)

        if current_distance > distances[current_stop]:
            continue

        if current_stop == end_stop:
            break

        for neighbor, weight in network.adjacency_list.get(current_stop, []):
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_stops[neighbor] = current_stop
                queue.append((distance, neighbor))

    # 重建路径 (保持不变)
    path = []
    current = end_stop
    while current is not None:
        path.append(current)
        current = previous_stops[current]
    path.reverse()

    if path and path[0] == start_stop:
        return path, distances[end_stop]
    else:
        return None, float('inf')


def find_all_paths(network: TransportNetwork, start_stop: Stop, end_stop: Stop, path=None, distance=0):
    """
    递归查找两个站点之间的所有可能路径。

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