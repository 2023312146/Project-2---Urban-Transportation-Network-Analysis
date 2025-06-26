from project.algorithms.algorithms import dijkstra, find_all_paths as find_all_paths_algo
from project.module.network import TransportNetwork
from project.module.stop import Stop, ZoneType

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
    
    def _create_transport_network(self):
        """构建交通网络"""
        network = TransportNetwork()
        zone_type_map = {
            "Residential": ZoneType.RESIDENTIAL,
            "Commercial": ZoneType.COMMERCIAL,
            "Industrial": ZoneType.INDUSTRIAL,
            "Mixed": ZoneType.MIXED,
        }
        stops = {}
        
        # 创建所有站点
        for station_id, station_data in self.data_manager.stations.items():
            zone_type = zone_type_map.get(station_data['type'], ZoneType.MIXED)
            stop = Stop(
                stop_ID=station_data['id'],
                name=station_data['name'],
                latitude=station_data.get('lat', 0),
                longitude=station_data.get('lon', 0),
                zone_type=zone_type
            )
            stops[station_id] = stop
        
        # 添加站点到网络
        for stop in stops.values():
            network.add_stop(stop)
        
        # 添加路线
        for (from_id, to_id), distance in self.data_manager.distances.items():
            from_stop = stops.get(from_id)
            to_stop = stops.get(to_id)
            if from_stop and to_stop:
                network.add_route(from_stop, to_stop, distance)
        
        return network, stops

    def _calculate_efficiency(self, path_stops, total_distance):
        """
        计算路径效率
        :param path_stops: Stop对象列表
        :param total_distance: 路径总距离(km)
        :return: 效率值(km/h)
        """
        if len(path_stops) < 2:
            return 0.0

        # 计算等待时间（包括起点，不包括终点）
        wait_time = sum(
            self.WAIT_TIMES[stop.zone_type] 
            for stop in path_stops[:-1]  # 包含起点，不包含终点
        )

        # 行程时间 = 距离 / 速度(23km/h)
        travel_time = total_distance / 23.0
        
        # 总时间 = 行程时间 + 等待时间(转换为小时)
        total_time = travel_time + (wait_time / 60.0)
        
        # 效率 = 总距离 / 总时间
        return total_distance / total_time if total_time > 0 else 0.0

    def find_all_paths(self, start, end, include_efficiency=False):
        """
        查找所有路径
        :param include_efficiency: 是否包含效率计算
        :return: 路径列表 or 带效率的字典列表
        """
        network, stops_map = self._create_transport_network()
        start_stop = stops_map.get(start)
        end_stop = stops_map.get(end)
        
        if not start_stop or not end_stop:
            return [] if not include_efficiency else []

        all_paths = find_all_paths_algo(network, start_stop, end_stop)
        
        if not include_efficiency:
            return [[stop.stop_ID for stop in path] for path, _ in all_paths]
        else:
            return [{
                'path': [stop.stop_ID for stop in path],
                'distance': distance,
                'efficiency': self._calculate_efficiency(path, distance)
            } for path, distance in all_paths]

    def find_best_path(self, start, end, by_efficiency=False):
        """
        查找最优路径
        :param by_efficiency: True按效率优化，False按距离优化
        :return: 路径ID列表 or 带效率的字典
        """
        network, stops_map = self._create_transport_network()
        start_stop = stops_map.get(start)
        end_stop = stops_map.get(end)
        
        if not start_stop or not end_stop:
            return [] if not by_efficiency else {}

        if not by_efficiency:
            path_stops, _ = dijkstra(network, start_stop, end_stop)
            return [s.stop_ID for s in path_stops] if path_stops else []
        else:
            all_paths = self.find_all_paths(start, end, include_efficiency=True)
            return max(all_paths, key=lambda x: x['efficiency']) if all_paths else {}

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
        network, stops_map = self._create_transport_network()
        start_stop = stops_map.get(start)
        end_stop = stops_map.get(end)
        
        if not start_stop or not end_stop:
            return None

        # 获取Dijkstra最短路径
        dijkstra_path_stops, dist = dijkstra(network, start_stop, end_stop)
        dijkstra_path = [s.stop_ID for s in dijkstra_path_stops] if dijkstra_path_stops else []

        # 获取所有路径并计算效率
        all_paths = []
        for path_stops, distance in find_all_paths_algo(network, start_stop, end_stop):
            all_paths.append({
                'path': [s.stop_ID for s in path_stops],
                'distance': distance,
                'efficiency': self._calculate_efficiency(path_stops, distance)
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
        """查找连接数最多的站点"""
        max_degree = 0
        hub_station = None
        for station_id, station in self.data_manager.stations.items():
            degree = len(station["connections"])
            if degree > max_degree:
                max_degree = degree
                hub_station = station_id
        return hub_station