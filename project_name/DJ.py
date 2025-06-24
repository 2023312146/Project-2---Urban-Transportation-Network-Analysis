class TransportNetwork:
    def __init__(self):
        self.stops = set()
        self.routes = dict()  # {start: list of (end, distance)}

    def add_stop(self, stop_id):
        self.stops.add(stop_id)
        if stop_id not in self.routes:
            self.routes[stop_id] = []

    def add_route(self, start_id, end_id, distance):
        if start_id not in self.routes:
            self.routes[start_id] = []
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
