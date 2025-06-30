from project.algorithms.dijkstra import dijkstra
from project.algorithms.dfs import find_all_paths as find_all_paths_algo
from project.algorithms.efficient_path import calculate_efficiency, find_most_efficient_path, compare_paths_by_efficiency_and_distance
from project.data_structures.network import TransportNetwork
from project.data_structures.stop import Stop, ZoneType

class PathAnalyzer:
    # 定义各类型站点的等待时间（分钟）
    WAIT_TIMES = {
        ZoneType.RESIDENTIAL: 2,
        ZoneType.COMMERCIAL: 4,
        ZoneType.INDUSTRIAL: 3,
        ZoneType.MIXED: 3,
    }

    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def _get_stop_by_id(self, stop_id):
        """从TransportNetwork中获取Stop对象"""
        return self.data_manager.network.get_stop_by_id(stop_id)

    def find_all_paths(self, start, end, include_efficiency=False):
        """
        查找所有路径
        :param include_efficiency: 是否包含效率计算
        :return: 路径列表 or 带效率的字典列表
        """
        start_stop = self._get_stop_by_id(start)
        end_stop = self._get_stop_by_id(end)
        
        if not start_stop or not end_stop:
            return [] if not include_efficiency else []

        all_paths = find_all_paths_algo(self.data_manager.network, start_stop, end_stop)
        
        if not include_efficiency:
            return [[stop.stop_ID for stop in path] for path, _ in all_paths]
        else:
            return [{
                'path': [stop.stop_ID for stop in path],
                'distance': distance,
                'efficiency': calculate_efficiency(path, distance, self.WAIT_TIMES)
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
        """
        比较最短路径和效率最优路径
        :return: {
            'dijkstra_path': [IDs],
            'dijkstra_distance': float,
            'efficiency_path': [IDs],
            'efficiency_value': float,
            'efficiency_distance': float,
            'is_same': bool
        }
        """
        start_stop = self._get_stop_by_id(start)
        end_stop = self._get_stop_by_id(end)
        
        if not start_stop or not end_stop:
            return None

        # 获取Dijkstra最短路径
        dijkstra_path_stops, dist = dijkstra(self.data_manager.network, start_stop, end_stop)
        dijkstra_path = [s.stop_ID for s in dijkstra_path_stops] if dijkstra_path_stops else []

        # 获取所有路径并计算效率
        all_paths = []
        for path_stops, distance in find_all_paths_algo(self.data_manager.network, start_stop, end_stop):
            all_paths.append({
                'path': [s.stop_ID for s in path_stops],
                'distance': distance,
                'efficiency': calculate_efficiency(path_stops, distance, self.WAIT_TIMES)
            })

        if not all_paths:
            return None

        # 找出效率最高的路径
        eff_path = max(all_paths, key=lambda x: x['efficiency'])

        return {
            'dijkstra_path': dijkstra_path,
            'dijkstra_distance': dist,
            'efficiency_path': eff_path['path'],
            'efficiency_value': eff_path['efficiency'],
            'efficiency_distance': eff_path['distance'],
            'is_same': dijkstra_path == eff_path['path']
        }

    def find_highest_degree_station(self):
        """查找入度和出度之和最多的站点"""
        max_degree = 0
        hub_station = None
        
        # 统计所有站点的出度
        out_degrees = {}
        for stop in self.data_manager.network.adjacency_list:
            out_degrees[stop.stop_ID] = len(self.data_manager.network.adjacency_list[stop])
        
        # 统计所有站点的入度
        in_degrees = {stop.stop_ID: 0 for stop in self.data_manager.network.stops.values()}
        for stop in self.data_manager.network.adjacency_list:
            for neighbor, _ in self.data_manager.network.adjacency_list[stop]:
                in_degrees[neighbor.stop_ID] += 1
        
        # 计算总度数
        for stop in self.data_manager.network.stops.values():
            degree = out_degrees.get(stop.stop_ID, 0) + in_degrees.get(stop.stop_ID, 0)
            if degree > max_degree:
                max_degree = degree
                hub_station = stop.stop_ID
        
        return hub_station