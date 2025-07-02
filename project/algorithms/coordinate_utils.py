import math
from math import sin, cos, sqrt, atan2, radians

class CoordinateUtils:
    """坐标工具类：提供地理坐标计算和转换功能"""
    
    # 巴黎市区的默认坐标边界
    DEFAULT_MIN_LAT = 48.84216
    DEFAULT_MAX_LAT = 48.891342
    DEFAULT_MIN_LON = 2.237151
    DEFAULT_MAX_LON = 2.3955517
    
    # 默认视图尺寸
    DEFAULT_VIEW_WIDTH = 1200
    DEFAULT_VIEW_HEIGHT = 900
    DEFAULT_PADDING = 80
    
    @staticmethod
    def calculate_haversine_distance(lat1, lon1, lat2, lon2):
        """
        使用Haversine公式计算两个地理坐标点之间的距离
        
        Args:
            lat1: 第一点纬度
            lon1: 第一点经度
            lat2: 第二点纬度
            lon2: 第二点经度
            
        Returns:
            float: 两点间的距离（公里）
        """
        # 地球半径（公里）
        R = 6371.0
        
        # 转换为弧度
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # 经纬度差值
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine公式
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        
        return distance
    
    @staticmethod
    def calculate_distance_between_stops(stop1, stop2):
        """
        计算两个站点之间的距离
        
        Args:
            stop1: 包含lat和lon键的第一个站点字典
            stop2: 包含lat和lon键的第二个站点字典
            
        Returns:
            float: 两个站点之间的距离（公里）
        """
        return CoordinateUtils.calculate_haversine_distance(
            stop1['lat'], stop1['lon'],
            stop2['lat'], stop2['lon']
        )
    
    @staticmethod
    def calculate_distance_between_stops_by_id(data_manager, stop1_id, stop2_id):
        """
        通过站点ID计算两个站点之间的距离
        
        Args:
            data_manager: 数据管理器实例
            stop1_id: 第一个站点ID
            stop2_id: 第二个站点ID
            
        Returns:
            float: 两个站点之间的距离（公里），如果站点不存在则返回0
        """
        if stop1_id in data_manager.stations and stop2_id in data_manager.stations:
            stop1 = data_manager.stations[stop1_id]
            stop2 = data_manager.stations[stop2_id]
            return CoordinateUtils.calculate_distance_between_stops(stop1, stop2)
        return 0
    
    @classmethod
    def convert_gui_to_geo_coords(cls, x, y, min_lat=None, max_lat=None, min_lon=None, max_lon=None, 
                              view_width=None, view_height=None, padding=None):
        """
        将GUI坐标转换为地理坐标
        
        Args:
            x: GUI中的X坐标
            y: GUI中的Y坐标
            min_lat, max_lat, min_lon, max_lon: 坐标边界
            view_width, view_height: 视图尺寸
            padding: 内边距
            
        Returns:
            tuple: (纬度, 经度)
        """
        # 使用默认值或提供的值
        min_lat = min_lat if min_lat is not None else cls.DEFAULT_MIN_LAT
        max_lat = max_lat if max_lat is not None else cls.DEFAULT_MAX_LAT
        min_lon = min_lon if min_lon is not None else cls.DEFAULT_MIN_LON
        max_lon = max_lon if max_lon is not None else cls.DEFAULT_MAX_LON
        view_width = view_width if view_width is not None else cls.DEFAULT_VIEW_WIDTH
        view_height = view_height if view_height is not None else cls.DEFAULT_VIEW_HEIGHT
        padding = padding if padding is not None else cls.DEFAULT_PADDING
        
        norm_lon = (x - padding) / (view_width - 2*padding)
        norm_lat = 1 - (y - padding) / (view_height - 2*padding)
        lat = min_lat + norm_lat * (max_lat - min_lat)
        lon = min_lon + norm_lon * (max_lon - min_lon)
        
        return lat, lon
    
    @classmethod
    def convert_geo_to_gui_coords(cls, lat, lon, min_lat=None, max_lat=None, min_lon=None, max_lon=None, 
                              view_width=None, view_height=None, padding=None):
        """
        将地理坐标转换为GUI坐标
        
        Args:
            lat: 纬度
            lon: 经度
            min_lat, max_lat, min_lon, max_lon: 坐标边界
            view_width, view_height: 视图尺寸
            padding: 内边距
            
        Returns:
            tuple: (x, y) GUI中的坐标
        """
        # 使用默认值或提供的值
        min_lat = min_lat if min_lat is not None else cls.DEFAULT_MIN_LAT
        max_lat = max_lat if max_lat is not None else cls.DEFAULT_MAX_LAT
        min_lon = min_lon if min_lon is not None else cls.DEFAULT_MIN_LON
        max_lon = max_lon if max_lon is not None else cls.DEFAULT_MAX_LON
        view_width = view_width if view_width is not None else cls.DEFAULT_VIEW_WIDTH
        view_height = view_height if view_height is not None else cls.DEFAULT_VIEW_HEIGHT
        padding = padding if padding is not None else cls.DEFAULT_PADDING
        
        norm_lat = (lat - min_lat) / (max_lat - min_lat)
        norm_lon = (lon - min_lon) / (max_lon - min_lon)
        x = padding + norm_lon * (view_width - 2*padding)
        y = padding + (1 - norm_lat) * (view_height - 2*padding)
        
        return x, y 