from project.data_structures.stop_entity import Stop
import csv

class TransportNetwork:
    def __init__(self):
        # 邻接表：key为stop_ID，value为[(neighbor_stop_ID, distance), ...]
        self.adjacency_list = {} 
        # id到Stop对象的映射
        self.stops = {} 
        # 反向邻接表：key为stop_ID，value为[(from_stop_ID, distance), ...]
        self.reverse_adjacency = {}
    
    def add_stop(self, stop):
        if not isinstance(stop, Stop):
            raise TypeError("Argument must be a Stop object")
        if stop.stop_ID in self.adjacency_list:
            raise ValueError(f"Stop with ID {stop.stop_ID} already exists")
        self.adjacency_list[stop.stop_ID] = []
        self.reverse_adjacency[stop.stop_ID] = []
        self.stops[stop.stop_ID] = stop
    
    def add_route(self, from_stop, to_stop, distance):
        from_id = from_stop.stop_ID if isinstance(from_stop, Stop) else from_stop
        to_id = to_stop.stop_ID if isinstance(to_stop, Stop) else to_stop
        if from_id not in self.adjacency_list:
            raise ValueError("From stop not found in network")
        if to_id not in self.adjacency_list:
            raise ValueError("To stop not found in network")
        if distance < 0:
            raise ValueError("Distance must be non-negative")
        for neighbor_id, _ in self.adjacency_list[from_id]:
            if neighbor_id == to_id:
                raise ValueError(f"Route from {from_id} to {to_id} already exists")
        self.adjacency_list[from_id].append((to_id, distance))
        self.reverse_adjacency[to_id].append((from_id, distance))
    
    def remove_stop(self, stop):
        stop_id = stop.stop_ID if isinstance(stop, Stop) else stop
        if stop_id not in self.adjacency_list:
            return  # 站点不存在，无需操作
        # 1. 移除所有指向该站点的边
        for from_id, _ in list(self.reverse_adjacency[stop_id]):
            self.adjacency_list[from_id] = [
                (neighbor_id, dist) for neighbor_id, dist in self.adjacency_list[from_id]
                if neighbor_id != stop_id
            ]
        # 2. 移除该站点的所有出边
        for to_id, _ in list(self.adjacency_list[stop_id]):
            self.reverse_adjacency[to_id] = [
                (neighbor_id, dist) for neighbor_id, dist in self.reverse_adjacency[to_id]
                if neighbor_id != stop_id
            ]
        # 3. 从数据结构中移除站点
        del self.adjacency_list[stop_id]
        del self.reverse_adjacency[stop_id]
        if stop_id in self.stops:
            del self.stops[stop_id]
    
    def remove_route(self, from_stop, to_stop):
        from_id = from_stop.stop_ID if isinstance(from_stop, Stop) else from_stop
        to_id = to_stop.stop_ID if isinstance(to_stop, Stop) else to_stop
        if from_id not in self.adjacency_list:
            raise ValueError("From stop not found in network")
        # 从正向邻接表中移除
        self.adjacency_list[from_id] = [
            (neighbor_id, dist) for neighbor_id, dist in self.adjacency_list[from_id]
            if neighbor_id != to_id
        ]
        # 从反向邻接表中移除
        if to_id in self.reverse_adjacency:
            self.reverse_adjacency[to_id] = [
                (neighbor_id, dist) for neighbor_id, dist in self.reverse_adjacency[to_id]
                if neighbor_id != from_id
            ]
    
    def get_stop_by_id(self, stop_id):
        return self.stops.get(stop_id)

    @classmethod
    def load_stops_from_csv(cls, file_path):
        network = cls()
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                stop = Stop.from_dict(row)
                try:
                    network.add_stop(stop)
                except ValueError as e:
                    print(f"Warning: {e}")
        return network
    
    def load_routes_from_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    start_id = int(row['start_stop_id'])
                    end_id = int(row['end_stop_id'])
                    distance = float(row['distance'])
                    if start_id in self.stops and end_id in self.stops:
                        try:
                            self.add_route(start_id, end_id, distance)
                        except ValueError as e:
                            print(f"Warning: {e}")
                    else:
                        print(f"Warning: Stop ID not found for route {start_id} -> {end_id}")
                except (ValueError, KeyError) as e:
                    print(f"Skipping malformed route row: {row}, error: {e}")