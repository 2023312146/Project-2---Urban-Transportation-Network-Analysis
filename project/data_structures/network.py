from project.data_structures.stop import Stop
import csv

class TransportNetwork:
    def __init__(self):
        self.adjacency_list = {} 
        self.stops = {} 
        # 新增：反向邻接表，用于快速找到指向某个站点的所有边
        self.reverse_adjacency = {}
    
    def add_stop(self, stop):
        if not isinstance(stop, Stop):
            raise TypeError("Argument must be a Stop object")
        if stop not in self.adjacency_list:
            self.adjacency_list[stop] = []
            self.reverse_adjacency[stop] = []
            self.stops[stop.stop_ID] = stop
    
    def add_route(self, from_stop, to_stop, distance):
        if from_stop not in self.adjacency_list:
            raise ValueError("From stop not found in network")
        if to_stop not in self.adjacency_list:
            raise ValueError("To stop not found in network")
        if distance < 0:
            raise ValueError("Distance must be non-negative")
        
        # 检查连接是否已存在
        for neighbor, _ in self.adjacency_list[from_stop]:
            if neighbor == to_stop:
                raise ValueError("Route already exists")
        
        # 添加到正向邻接表
        self.adjacency_list[from_stop].append((to_stop, distance))
        # 添加到反向邻接表
        self.reverse_adjacency[to_stop].append((from_stop, distance))
    
    def remove_stop(self, stop):
        """
        从网络中移除站点及其所有相关连接
        优化版本：利用反向邻接表快速定位需要移除的连接
        复杂度：O(deg(stop)) 其中 deg(stop) 是被删除站点的度数
        """
        if not isinstance(stop, Stop):
            raise TypeError("Argument must be a Stop object")
        
        if stop not in self.adjacency_list:
            return  # 站点不存在，无需操作
        
        # 1. 移除所有指向该站点的边（利用反向邻接表，O(deg(stop))）
        for from_stop, _ in self.reverse_adjacency[stop]:
            # 从from_stop的邻接表中移除指向stop的边
            self.adjacency_list[from_stop] = [
                (neighbor, dist) for neighbor, dist in self.adjacency_list[from_stop]
                if neighbor != stop
            ]
        
        # 2. 移除该站点的所有出边（O(deg(stop))）
        for to_stop, _ in self.adjacency_list[stop]:
            # 从to_stop的反向邻接表中移除来自stop的边
            self.reverse_adjacency[to_stop] = [
                (neighbor, dist) for neighbor, dist in self.reverse_adjacency[to_stop]
                if neighbor != stop
            ]
        
        # 3. 从数据结构中移除站点（O(1)）
        del self.adjacency_list[stop]
        del self.reverse_adjacency[stop]
        if stop.stop_ID in self.stops:
            del self.stops[stop.stop_ID]
    
    def remove_route(self, from_stop, to_stop):
        """
        移除两个站点之间的连接
        优化版本：同时更新正向和反向邻接表
        """
        if not isinstance(from_stop, Stop) or not isinstance(to_stop, Stop):
            raise TypeError("Arguments must be Stop objects")
        
        if from_stop not in self.adjacency_list:
            raise ValueError("From stop not found in network")
        
        # 从正向邻接表中移除
        self.adjacency_list[from_stop] = [
            (neighbor, dist) for neighbor, dist in self.adjacency_list[from_stop]
            if neighbor != to_stop
        ]
        
        # 从反向邻接表中移除
        if to_stop in self.reverse_adjacency:
            self.reverse_adjacency[to_stop] = [
                (neighbor, dist) for neighbor, dist in self.reverse_adjacency[to_stop]
                if neighbor != from_stop
            ]
    
    def get_stop_by_id(self, stop_id):
        return self.stops.get(stop_id)

    @classmethod
    def load_stops_from_csv(cls, file_path):
        """Load the stops from a CSV file"""
        network = cls()
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                stop = Stop.from_dict(row)
                network.add_stop(stop)
        return network
    
    def load_routes_from_csv(self, file_path):
        """Load the routes from a CSV file"""
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