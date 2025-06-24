import heapq

def dijkstra(network, start_id, end_id):
    if start_id not in network.stops or end_id not in network.stops:
        return None, float('inf')
        
    distances = {stop: float('inf') for stop in network.stops}
    previous = {stop: None for stop in network.stops}
    distances[start_id] = 0
    queue = [(0, start_id)]
    
    while queue:
        current_distance, current_stop = heapq.heappop(queue)
        
        if current_distance > distances[current_stop]:
            continue
            
        for neighbor, weight in network.routes.get(current_stop, []):
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_stop
                heapq.heappush(queue, (distance, neighbor))
                
    path = []
    current = end_id
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    
    if path and path[0] == start_id:
        return path, distances[end_id]
    else:
        return None, float('inf')

def find_all_paths(network, start_id, end_id, path=None, distance=0):
    if path is None:
        path = []
    path = path + [start_id]
    
    if start_id == end_id:
        return [(path, distance)]
        
    if start_id not in network.routes:
        return []
        
    paths = []
    for neighbor, weight in network.routes[start_id]:
        if neighbor not in path:
            newpaths = find_all_paths(network, neighbor, end_id, path, distance + weight)
            for p in newpaths:
                paths.append(p)
    return paths 