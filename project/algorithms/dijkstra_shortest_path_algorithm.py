from project.data_structures.stop_entity import Stop
from project.data_structures.transport_network_structure import TransportNetwork

def dijkstra(network: TransportNetwork, start_stop, end_stop):
    """
    使用Dijkstra算法查找两个站点之间的最短路径。
    :param network: TransportNetwork 对象
    :param start_stop: 起始 Stop 对象或stop_ID
    :param end_stop: 终点 Stop 对象或stop_ID
    :return: 一个元组，包含最短路径（Stop对象列表）和总距离。如果找不到路径，则返回(None, float('inf'))。
    """
    # 支持传入Stop对象或stop_ID
    start_id = start_stop.stop_ID if isinstance(start_stop, Stop) else start_stop
    end_id = end_stop.stop_ID if isinstance(end_stop, Stop) else end_stop
    if start_id not in network.adjacency_list or end_id not in network.adjacency_list:
        return None, float('inf')

    distances = {stop_id: float('inf') for stop_id in network.adjacency_list}
    previous_stops = {stop_id: None for stop_id in network.adjacency_list}
    distances[start_id] = 0
    
    queue = [(0, start_id)]

    while queue:
        min_index = 0
        for i in range(1, len(queue)):
            if queue[i][0] < queue[min_index][0]:
                min_index = i
        current_distance, current_id = queue.pop(min_index)

        if current_distance > distances[current_id]:
            continue

        if current_id == end_id:
            break

        for neighbor_id, weight in network.adjacency_list.get(current_id, []):
            distance = current_distance + weight
            if distance < distances[neighbor_id]:
                distances[neighbor_id] = distance
                previous_stops[neighbor_id] = current_id
                queue.append((distance, neighbor_id))

    # 重建路径
    path = []
    current = end_id
    while current is not None:
        path.append(current)
        current = previous_stops[current]
    path.reverse()

    if path and path[0] == start_id:
        # 返回Stop对象列表
        return [network.get_stop_by_id(stop_id) for stop_id in path], distances[end_id]
    else:
        return None, float('inf') 