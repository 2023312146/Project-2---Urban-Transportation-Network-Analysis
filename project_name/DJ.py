import csv

class TransportNetwork:
    def __init__(self):
        self.stops = set()
        self.stop_details = {}  # 存储站点详细信息
        self.routes = {}  # {start: list of (end, distance)}
    
    def load_stops_from_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                stop_id = int(row['stop_id'])
                self.add_stop(stop_id)
                # 存储站点详细信息
                self.stop_details[stop_id] = {
                    'name': row['name'],
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'zone_type': row['zone_type']
                }
    
    def load_routes_from_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, fieldnames=['start_stop_id', 'end_stop_id', 'distance'])
            next(reader)  # 跳过标题行
            for row in reader:
                start = int(row['start_stop_id'])
                end = int(row['end_stop_id'])
                distance = float(row['distance'])
                self.add_route(start, end, distance)
    
    def add_stop(self, stop_id):
        self.stops.add(stop_id)
        if stop_id not in self.routes:
            self.routes[stop_id] = []
    
    def add_route(self, start_id, end_id, distance):
        if start_id not in self.routes:
            self.add_stop(start_id)
        self.routes[start_id].append((end_id, distance))

    def dijkstra(self, start_id, end_id):
        import heapq
        distances = {stop: float('inf') for stop in self.stops}
        previous = {stop: None for stop in self.stops}
        distances[start_id] = 0
        queue = [(0, start_id)]
        while queue:
            current_distance, current_stop = heapq.heappop(queue)
            if current_distance > distances[current_stop]:
                continue
            for neighbor, weight in self.routes.get(current_stop, []):
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
        return path, distances[end_id]

    def find_all_paths(self, start_id, end_id, path=None, distance=0):
        if path is None:
            path = []
        path = path + [start_id]
        if start_id == end_id:
            return [(path, distance)]
        if start_id not in self.routes:
            return []
        paths = []
        for neighbor, weight in self.routes[start_id]:
            if neighbor not in path:
                newpaths = self.find_all_paths(neighbor, end_id, path, distance + weight)
                for p in newpaths:
                    paths.append(p)
        return paths

    def print_all_paths_with_shortest(self, start_id, end_id):
        all_paths = self.find_all_paths(start_id, end_id)
        if not all_paths:
            print(f"No path from {start_id} to {end_id}")
            return
        min_distance = min(dist for _, dist in all_paths)
        for path, dist in all_paths:
            mark = " <--- shortest" if dist == min_distance else ""
            print(f"Path: {path}, Distance: {dist}{mark}")
