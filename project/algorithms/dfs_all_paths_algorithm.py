from project.data_structures.stop_entity import Stop
from project.data_structures.transport_network_structure import TransportNetwork

def find_all_paths(network: TransportNetwork, start_stop, end_stop, max_distance=80):
    # 提取起点和终点ID
    start_id = start_stop.stop_ID if isinstance(start_stop, Stop) else start_stop
    end_id = end_stop.stop_ID if isinstance(end_stop, Stop) else end_stop
    
    # 初始化结果列表
    all_paths = []
    # 栈结构：每个元素是(当前节点ID, 当前路径, 当前距离)
    stack = [(start_id, [start_id], 0)]
    
    # 当栈不为空时继续搜索
    while stack:
        # 从栈顶弹出一个元素
        current_id, current_path, current_distance = stack.pop()
        # 剪枝：如果超过最大距离，则不再考虑该路径
        if max_distance is not None and current_distance > max_distance:
            continue
        
        # 如果到达终点，将路径添加到结果
        if current_id == end_id:
            # 转换路径中的ID为Stop对象
            stop_path = [network.get_stop_by_id(pid) for pid in current_path]
            all_paths.append((stop_path, current_distance))
            continue
        if current_id not in network.adjacency_list:
            continue
        neighbors = list(network.adjacency_list[current_id])
        for neighbor_id, weight in reversed(neighbors):
            # 计算新的累计距离
            new_distance = current_distance + weight
            
            # 剪枝：如果超过最大距离，则不再考虑该路径
            if max_distance is not None and new_distance > max_distance:
                continue
                
            # 避免环路
            if neighbor_id not in current_path:
                # 创建新路径
                new_path = current_path + [neighbor_id]
                stack.append((neighbor_id, new_path, new_distance))
    
    return all_paths 