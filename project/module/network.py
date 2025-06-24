from module.stop import Stop

class TransportNetwork:
    def __init__(self):
        self.adjacency_list = {}  # 邻接表：{Stop对象: [(Stop对象, 距离), ...]}
    
    def add_stop(self, stop):
        if not isinstance(stop, Stop):
            raise TypeError("Argument must be a Stop object")
        if stop not in self.adjacency_list:
            self.adjacency_list[stop] = []
    
    def add_route(self, from_stop, to_stop, distance):
        if from_stop not in self.adjacency_list:
            raise ValueError("From stop not found in network")
        if to_stop not in self.adjacency_list:
            raise ValueError("To stop not found in network")
        if distance < 0:
            raise ValueError("Distance must be non-negative")
        
        self.adjacency_list[from_stop].append((to_stop, distance))