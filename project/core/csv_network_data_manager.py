import csv
import os
from project.data_structures.stop_entity import ZoneType, Stop
from project.data_structures.transport_network_structure import TransportNetwork

class NetworkDataManager:
    def __init__(self, stops_csv_path=None, routes_csv_path=None):
        self.network = TransportNetwork()
        self.station_name_to_id = {}
        
        # 设置默认CSV文件路径
        if stops_csv_path is None:
            stops_csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'urban_transport_network_stops.csv')
        if routes_csv_path is None:
            routes_csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'urban_transport_network_routes.csv')
        
        # 从CSV文件加载数据
        self.load_data_from_csv(stops_csv_path, routes_csv_path)
    
    def load_data_from_csv(self, stops_csv_path, routes_csv_path):
        """
        从CSV文件加载站点和路线数据
        
        Args:
            stops_csv_path (str): 站点CSV文件路径
            routes_csv_path (str): 路线CSV文件路径
        """
        # 加载站点数据
        self._load_stops_from_csv(stops_csv_path)
        
        # 加载路线数据
        self._load_routes_from_csv(routes_csv_path)
    
    def _load_stops_from_csv(self, stops_csv_path):
        """
        从CSV文件加载站点数据
        
        Args:
            stops_csv_path (str): 站点CSV文件路径
        """
        try:
            with open(stops_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # 解析区域类型
                    zone_type = self._parse_zone_type(row['zone_type'])
                    
                    # 创建Stop对象
                    stop = Stop(
                        stop_ID=row['stop_id'],
                        name=row['name'],
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude']),
                        zone_type=zone_type
                    )
                    
                    # 添加到网络
                    self.network.add_stop(stop)
                    self.station_name_to_id[stop.name] = stop.stop_ID
                    
        except FileNotFoundError:
            raise FileNotFoundError(f"站点CSV文件未找到: {stops_csv_path}")
        except Exception as e:
            raise Exception(f"加载站点数据时出错: {str(e)}")
    
    def _load_routes_from_csv(self, routes_csv_path):
        """
        从CSV文件加载路线数据
        
        Args:
            routes_csv_path (str): 路线CSV文件路径
        """
        try:
            with open(routes_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    start_stop_id = row['start_stop_id']
                    end_stop_id = row['end_stop_id']
                    distance = float(row['distance'])
                    
                    # 获取站点对象
                    start_stop = self.network.get_stop_by_id(start_stop_id)
                    end_stop = self.network.get_stop_by_id(end_stop_id)
                    
                    if start_stop and end_stop:
                        self.network.add_route(start_stop, end_stop, distance)
                    else:
                        print(f"警告: 无法找到站点 {start_stop_id} 或 {end_stop_id}")
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"路线CSV文件未找到: {routes_csv_path}")
        except Exception as e:
            raise Exception(f"加载路线数据时出错: {str(e)}")
    
    def _parse_zone_type(self, zone_type_str):
        """
        解析区域类型字符串为ZoneType枚举
        
        Args:
            zone_type_str (str): 区域类型字符串
            
        Returns:
            ZoneType: 对应的区域类型枚举值
        """
        # 关键修改：将键改为全大写，与CSV文件中的zone_type值匹配
        zone_type_map = {
            "RESIDENTIAL": ZoneType.RESIDENTIAL,
            "COMMERCIAL": ZoneType.COMMERCIAL,
            "INDUSTRIAL": ZoneType.INDUSTRIAL,
            "MIXED": ZoneType.MIXED,
        }
        return zone_type_map.get(zone_type_str, ZoneType.MIXED)

    # 委托方法 - 所有操作都委托给TransportNetwork
    def add_station(self, name, x, y, station_type, wait_time=None):
        """添加站点 - 委托给TransportNetwork"""
        # 坐标转换
        lat, lon = self._convert_gui_to_geo_coords(x, y)
        zone_type = self._convert_string_to_zone_type(station_type)
        new_id = str(max([int(id) for id in self.network.stops.keys()] + [0]) + 1)
        stop = Stop(
            stop_ID=new_id,
            name=name,
            latitude=lat,
            longitude=lon,
            zone_type=zone_type
        )
        try:
            self.network.add_stop(stop)
            self.station_name_to_id[name] = new_id
        except ValueError as e:
            raise e

    def remove_station(self, name):
        """删除站点 - 委托给TransportNetwork"""
        if name in self.station_name_to_id:
            station_id = self.station_name_to_id[name]
            stop = self.network.get_stop_by_id(station_id)
            if stop:
                # 委托给TransportNetwork
                self.network.remove_stop(stop)
                del self.station_name_to_id[name]

    def update_station_type(self, name, new_type):
        """更新站点类型 - 直接操作Stop对象"""
        if name in self.station_name_to_id:
            station_id = self.station_name_to_id[name]
            stop = self.network.get_stop_by_id(station_id)
            if stop:
                zone_type = self._convert_string_to_zone_type(new_type)
                stop.zone_type = zone_type

    def add_connection(self, from_name, to_name, distance):
        """添加连接 - 委托给TransportNetwork"""
        if from_name not in self.station_name_to_id or to_name not in self.station_name_to_id:
            raise ValueError("One or both stations do not exist")
        from_id = self.station_name_to_id[from_name]
        to_id = self.station_name_to_id[to_name]
        if from_id not in self.network.stops or to_id not in self.network.stops:
            raise ValueError("One or both stations not found in network")
        try:
            self.network.add_route(from_id, to_id, distance)
        except ValueError as e:
            raise e

    def remove_connection(self, from_name, to_name):
        """删除连接 - 委托给TransportNetwork"""
        if from_name in self.station_name_to_id and to_name in self.station_name_to_id:
            from_id = self.station_name_to_id[from_name]
            to_id = self.station_name_to_id[to_name]
            
            if from_id in self.network.stops and to_id in self.network.stops:
                # 委托给TransportNetwork
                self.network.remove_route(from_id, to_id)

    # 辅助方法 - 坐标和类型转换
    def _convert_gui_to_geo_coords(self, x, y):
        """将GUI坐标转换为地理坐标"""
        min_lat = 48.84216
        max_lat = 48.891342
        min_lon = 2.237151
        max_lon = 2.3955517
        view_width = 1200
        view_height = 900
        padding = 80
        
        norm_lon = (x - padding) / (view_width - 2*padding)
        norm_lat = 1 - (y - padding) / (view_height - 2*padding)
        lat = min_lat + norm_lat * (max_lat - min_lat)
        lon = min_lon + norm_lon * (max_lon - min_lon)
        
        return lat, lon

    def _convert_geo_to_gui_coords(self, lat, lon):
        """将地理坐标转换为GUI坐标"""
        min_lat = 48.84216
        max_lat = 48.891342
        min_lon = 2.237151
        max_lon = 2.3955517
        view_width = 1200
        view_height = 900
        padding = 80
        
        norm_lat = (lat - min_lat) / (max_lat - min_lat)
        norm_lon = (lon - min_lon) / (max_lon - min_lon)
        x = padding + norm_lon * (view_width - 2*padding)
        y = padding + (1 - norm_lat) * (view_height - 2*padding)
        
        return x, y

    def _convert_string_to_zone_type(self, zone_string):
        """将字符串转换为ZoneType枚举"""
        zone_type_map = {
            "Residential": ZoneType.RESIDENTIAL,
            "Commercial": ZoneType.COMMERCIAL,
            "Industrial": ZoneType.INDUSTRIAL,
            "Mixed": ZoneType.MIXED,
        }
        return zone_type_map.get(zone_string, ZoneType.MIXED)

    def _get_wait_time(self, zone_type):
        """根据区域类型获取等待时间"""
        zone_type_wait_map = {
            ZoneType.RESIDENTIAL: 2,
            ZoneType.COMMERCIAL: 4,
            ZoneType.INDUSTRIAL: 3,
            ZoneType.MIXED: 3,
        }
        return zone_type_wait_map.get(zone_type, 3)

    # 向后兼容的属性 - 从TransportNetwork获取数据
    @property
    def stations(self):
        """获取所有站点数据 - 从TransportNetwork转换"""
        stations = {}
        for stop in self.network.stops.values():
            x, y = self._convert_geo_to_gui_coords(stop.latitude, stop.longitude)
            # 获取连接
            connections = []
            if stop.stop_ID in self.network.adjacency_list:
                connections = [neighbor_id for neighbor_id, _ in self.network.adjacency_list[stop.stop_ID]]
            stations[stop.stop_ID] = {
                "id": stop.stop_ID,
                "name": stop.name,
                "lat": stop.latitude,
                "lon": stop.longitude,
                "x": x,
                "y": y,
                "type": stop.zone_type.value,
                "wait_time": self._get_wait_time(stop.zone_type),
                "connections": connections
            }
        return stations

    @property
    def distances(self):
        """获取所有距离数据 - 从TransportNetwork转换"""
        distances = {}
        for stop_id in self.network.adjacency_list:
            for neighbor_id, distance in self.network.adjacency_list[stop_id]:
                distances[(stop_id, neighbor_id)] = distance
        return distances

    @property
    def lines(self):
        """保持向后兼容 - 返回空字典，因为不再使用lines概念"""
        return {}

    # 直接访问TransportNetwork的方法
    def get_stop_by_id(self, stop_id):
        """直接委托给TransportNetwork"""
        return self.network.get_stop_by_id(stop_id)

    def get_all_stops(self):
        """获取所有Stop对象"""
        return list(self.network.stops.values())

    def get_adjacency_list(self):
        """获取邻接表"""
        return self.network.adjacency_list.copy()

    def save_data_to_csv(self, stops_csv_path=None, routes_csv_path=None):
        """
        将内存中的站点和路线数据写入CSV文件
        """
        # 设置默认保存路径（与加载路径一致）
        if stops_csv_path is None:
            stops_csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'urban_transport_network_stops.csv')
        if routes_csv_path is None:
            routes_csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'urban_transport_network_routes.csv')

        try:
            # 检查数据目录是否存在，不存在则创建
            data_dir = os.path.dirname(stops_csv_path)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)

            # 保存站点数据到CSV
            with open(stops_csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['stop_id', 'name', 'latitude', 'longitude', 'zone_type'])
                writer.writeheader()
                for stop in self.get_all_stops():
                    writer.writerow({
                        'stop_id': stop.stop_ID,
                        'name': stop.name,
                        'latitude': stop.latitude,
                        'longitude': stop.longitude,
                        'zone_type': stop.zone_type.name  # 保存枚举名称（如"RESIDENTIAL"）
                    })

            # 保存路线数据到CSV
            with open(routes_csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['start_stop_id', 'end_stop_id', 'distance'])
                writer.writeheader()
                for (start_id, end_id), distance in self.distances.items():
                    writer.writerow({
                        'start_stop_id': start_id,
                        'end_stop_id': end_id,
                        'distance': f"{distance:.2f}"  # 保留两位小数
                    })

        except Exception as e:
            raise Exception(f"保存失败: {str(e)}")