class TransportNetwork:
    def __init__(self):
        self.stops = set()
        self.stop_details = {}
        self.routes = {}

    def add_stop(self, stop_id, details=None):
        self.stops.add(stop_id)
        if details:
            self.stop_details[stop_id] = details
        if stop_id not in self.routes:
            self.routes[stop_id] = []

    def add_route(self, start_id, end_id, distance):
        if start_id not in self.stops:
            self.add_stop(start_id)
        if end_id not in self.stops:
            self.add_stop(end_id)
        self.routes[start_id].append((end_id, distance)) 