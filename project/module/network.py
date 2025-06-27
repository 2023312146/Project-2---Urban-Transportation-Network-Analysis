from .stop import Stop
import csv

class TransportNetwork:
    def __init__(self):
        self.adjacency_list = {} 
        self.stops = {} 
    
    def add_stop(self, stop):
        if not isinstance(stop, Stop):
            raise TypeError("Argument must be a Stop object")
        if stop not in self.adjacency_list:
            self.adjacency_list[stop] = []
            self.stops[stop.stop_ID] = stop
    
    def add_route(self, from_stop, to_stop, distance):
        if from_stop not in self.adjacency_list:
            raise ValueError("From stop not found in network")
        if to_stop not in self.adjacency_list:
            raise ValueError("To stop not found in network")
        if distance < 0:
            raise ValueError("Distance must be non-negative")
        
        self.adjacency_list[from_stop].append((to_stop, distance))
    
    def get_stop_by_id(self, stop_id):
        return self.stops.get(stop_id)

    @classmethod
    def load_stops_from_csv(cls, file_path):
        """从CSV文件加载站点"""
        network = cls()
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                stop = Stop.from_dict(row)
                network.add_stop(stop)
        return network
    
    def load_routes_from_csv(self, file_path):
        """从CSV文件加载路线"""
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    start_id = int(row['start_stop_id'])
                    end_id = int(row['end_stop_id'])
                    distance = float(row['distance'])
                    
                    start_stop = self.get_stop_by_id(start_id)
                    end_stop = self.get_stop_by_id(end_id)
                    
                    if start_stop and end_stop:
                        self.add_route(start_stop, end_stop, distance)
                    else:
                        print(f"Warning: Stop ID not found for route {start_id} -> {end_id}")
                except (ValueError, KeyError) as e:
                    print(f"Skipping malformed route row: {row}, error: {e}")