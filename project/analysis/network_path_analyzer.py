from project.algorithms.dijkstra_shortest_path_algorithm import dijkstra
from project.algorithms.dfs_all_paths_algorithm import find_all_paths as find_all_paths_algo
from project.algorithms.path_efficiency_analysis import calculate_efficiency, find_most_efficient_path, compare_paths_by_efficiency_and_distance
from project.data_structures.transport_network_structure import TransportNetwork
from project.data_structures.stop_entity import Stop, ZoneType
from project.algorithms.traffic_condition_manager import TrafficConditionManager

class PathAnalyzer:
    # 定义各类型站点的等待时间（分钟）
    WAIT_TIMES = {
        ZoneType.RESIDENTIAL: 2,
        ZoneType.COMMERCIAL: 4,
        ZoneType.INDUSTRIAL: 3,
        ZoneType.MIXED: 3,
    }

    def __init__(self, data_manager, traffic_manager=None):
        self.data_manager = data_manager
        self.traffic_manager = traffic_manager or TrafficConditionManager()
    
    def set_traffic_manager(self, traffic_manager):
        """设置交通状况管理器"""
        self.traffic_manager = traffic_manager
    
    def _get_stop_by_id(self, stop_id):
        return self.data_manager.network.get_stop_by_id(stop_id)

    def find_all_paths(self, start, end, include_efficiency=False):
        start_id = start if isinstance(start, int) else (start.stop_ID if hasattr(start, 'stop_ID') else start)
        end_id = end if isinstance(end, int) else (end.stop_ID if hasattr(end, 'stop_ID') else end)
        start_stop = self._get_stop_by_id(start_id)
        end_stop = self._get_stop_by_id(end_id)
        if not start_stop or not end_stop:
            return [] if not include_efficiency else []
        all_paths = find_all_paths_algo(self.data_manager.network, start_id, end_id)
        if not include_efficiency:
            return [[stop.stop_ID for stop in path] for path, _ in all_paths]
        else:
            return [{
                'path': [stop.stop_ID for stop in path],
                'distance': distance,
                'efficiency': calculate_efficiency(path, distance, self.WAIT_TIMES, 
                                                traffic_manager=self.traffic_manager)
            } for path, distance in all_paths]

    def find_best_path(self, start, end, by_efficiency=False):
        """
        查找最优路径
        :param by_efficiency: True按效率优化，False按距离优化
        :return: 路径ID列表 or 带效率的字典
        """
        start_stop = self._get_stop_by_id(start)
        end_stop = self._get_stop_by_id(end)
        
        if not start_stop or not end_stop:
            return [] if not by_efficiency else {}

        if not by_efficiency:
            path_stops, _ = dijkstra(self.data_manager.network, start_stop, end_stop)
            return [s.stop_ID for s in path_stops] if path_stops else []
        else:
            all_paths = self.find_all_paths(start, end, include_efficiency=True)
            return find_most_efficient_path(all_paths) if all_paths else {}

    def compare_best_paths(self, start, end):
        start_id = start if isinstance(start, int) else (start.stop_ID if hasattr(start, 'stop_ID') else start)
        end_id = end if isinstance(end, int) else (end.stop_ID if hasattr(end, 'stop_ID') else end)
        dijkstra_path, dist = dijkstra(self.data_manager.network, start_id, end_id)
        all_paths = self.find_all_paths(start_id, end_id, include_efficiency=True)
        if not all_paths:
            return None
        eff_path = max(all_paths, key=lambda x: x['efficiency'])
        return {
            'dijkstra_path': [stop.stop_ID for stop in dijkstra_path] if dijkstra_path else [],
            'dijkstra_distance': dist,
            'efficiency_path': eff_path['path'],
            'efficiency_value': eff_path['efficiency'],
            'efficiency_distance': eff_path['distance'],
            'is_same': [stop.stop_ID for stop in dijkstra_path] if dijkstra_path else [] == eff_path['path']
        }

    def find_highest_degree_station(self):
        max_degree = 0
        hub_station = None
        out_degrees = {}
        for stop_id in self.data_manager.network.adjacency_list:
            out_degrees[stop_id] = len(self.data_manager.network.adjacency_list[stop_id])
        in_degrees = {stop_id: 0 for stop_id in self.data_manager.network.stops}
        for stop_id in self.data_manager.network.adjacency_list:
            for neighbor_id, _ in self.data_manager.network.adjacency_list[stop_id]:
                in_degrees[neighbor_id] += 1
        for stop_id in self.data_manager.network.stops:
            degree = out_degrees.get(stop_id, 0) + in_degrees.get(stop_id, 0)
            if degree > max_degree:
                max_degree = degree
                hub_station = stop_id
        return hub_station