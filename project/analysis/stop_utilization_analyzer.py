import heapq
from collections import defaultdict
import math
import numpy as np

class StopUtilizationAnalyzer:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.network = data_manager.network
        self.passenger_volume = {}
        self.arrival_frequency = {}
        self.utilization_scores = {}
        self.potential_new_stops = []
    
    def set_passenger_data(self, passenger_data):
        self.passenger_volume = passenger_data
        
    def set_arrival_frequency(self, frequency_data):
        self.arrival_frequency = frequency_data
    
    def generate_random_data(self):
        """
        生成随机的乘客量和到达频率数据用于测试
        使用固定的种子以确保结果一致性
        """
        import random
        
        # 使用固定的种子值，确保每次生成的随机数据相同
        random.seed(42)  # 使用固定种子值42
        
        for stop_id in self.network.stops:
            # 生成随机乘客量，200-2000人/天
            self.passenger_volume[stop_id] = random.randint(200, 2000)
            # 生成随机到达频率，2-12班/小时
            self.arrival_frequency[stop_id] = random.randint(2, 12)
            
        # 重置随机数生成器，避免影响程序其他部分
        random.seed()
    
    def calculate_stop_efficiency(self):
        zone_weights = {
            "Residential": 1.2, 
            "Commercial": 1.5, 
            "Industrial": 0.9, 
            "Mixed": 1.0,       
        }
        efficiency_scores = []
        for stop_id, stop in self.network.stops.items():
            passenger_count = self.passenger_volume.get(stop_id, 500)
            frequency = self.arrival_frequency.get(stop_id, 4)

            connectivity = len(self.network.adjacency_list.get(stop_id, []))
            
            zone_weight = zone_weights.get(stop.zone_type.value, 1.0)
            # 计算效率分数: 乘客量 / (频率 * 区域权重)
            efficiency = (passenger_count / max(1, frequency)) * zone_weight
            self.utilization_scores[stop_id] = efficiency
            efficiency_scores.append((stop_id, efficiency, connectivity))
        return sorted(efficiency_scores, key=lambda x: x[1], reverse=True)
    
    def identify_underutilized_stops(self, threshold=0.3):
        efficiencies = self.calculate_stop_efficiency()
        scores = [score for _, score, _ in efficiencies]
        if not scores:
            return []
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score
        threshold_value = min_score + threshold * score_range
        underutilized = []
        for stop_id, score, connectivity in efficiencies:
            if score < threshold_value:
                stop = self.network.get_stop_by_id(stop_id)
                underutilized.append({
                    'stop_id': stop_id, 
                    'name': stop.name,
                    'score': score,
                    'connectivity': connectivity,
                    'passenger_volume': self.passenger_volume.get(stop_id, 0),
                    'arrival_frequency': self.arrival_frequency.get(stop_id, 0)
                })
        
        return underutilized
    
    def find_stops_for_consolidation(self, max_distance=2.0):
        consolidation_pairs = []
        stop_ids = list(self.network.stops.keys())
        for i in range(len(stop_ids)):
            for j in range(i + 1, len(stop_ids)):
                stop_id1 = stop_ids[i]
                stop_id2 = stop_ids[j]
                
                stop1 = self.network.get_stop_by_id(stop_id1)
                stop2 = self.network.get_stop_by_id(stop_id2)
                distance = self._calculate_distance(
                    stop1.latitude, stop1.longitude,
                    stop2.latitude, stop2.longitude
                )
                if distance <= max_distance:
                    score1 = self.utilization_scores.get(stop_id1, 0)
                    score2 = self.utilization_scores.get(stop_id2, 0)
                    if score1 >= score2:
                        keep_id, remove_id = stop_id1, stop_id2
                        keep_name, remove_name = stop1.name, stop2.name
                    else:
                        keep_id, remove_id = stop_id2, stop_id1
                        keep_name, remove_name = stop2.name, stop1.name
                    
                    consolidation_pairs.append({
                        'distance': distance,
                        'keep_stop': {'id': keep_id, 'name': keep_name},
                        'remove_stop': {'id': remove_id, 'name': remove_name}
                    })
        return sorted(consolidation_pairs, key=lambda x: x['distance'])
    
    def suggest_new_stops(self, num_suggestions=3):
        """
        推荐新站点位置
        Args:
            num_suggestions: 推荐站点的数量
        Returns:
            推荐站点列表
        """
        # 现有站点的安全距离（公里）- 不允许在该范围内添加新站点
        MIN_DISTANCE_TO_EXISTING_STOPS = 1.0  # 1公里安全距离
        # 找出高利用率区域
        high_utilized = []
        scores = list(self.utilization_scores.values())
        if not scores:
            return []
        threshold = np.percentile(scores, 60)  # 降低为前40%的站点都被认为是高利用率
        for stop_id, score in self.utilization_scores.items():
            if score > threshold:
                stop = self.network.get_stop_by_id(stop_id)
                high_utilized.append((stop, score))
        # 使用图的社区检测找出潜在的新站点位置
        suggestions = []
        if high_utilized:
            # 排序按利用率从高到低
            high_utilized.sort(key=lambda x: x[1], reverse=True)
            # 针对每个高利用率站点，找出与其相邻但没有直接连接的站点对
            for stop, score in high_utilized[:num_suggestions*2]:  # 增加考虑的高利用率站点数量
                stop_id = stop.stop_ID
                # 获取一级连接
                first_level = set(n_id for n_id, _ in self.network.adjacency_list.get(stop_id, []))
                # 获取二级连接（一级连接的连接）
                second_level = set()
                for n_id in first_level:
                    second_level.update(n2_id for n2_id, _ in self.network.adjacency_list.get(n_id, []))
                # 移除已经是一级连接的站点
                second_level -= first_level
                second_level.discard(stop_id)
                for s_id in second_level:
                    s_stop = self.network.get_stop_by_id(s_id)
                    # 计算两个站点之间的中点
                    mid_lat = (stop.latitude + s_stop.latitude) / 2
                    mid_lon = (stop.longitude + s_stop.longitude) / 2
                    # 计算两站点之间的距离
                    distance = self._calculate_distance(
                        stop.latitude, stop.longitude,
                        s_stop.latitude, s_stop.longitude
                    )
                    # 如果距离足够大，可能需要一个中间站点
                    if distance > 3.0:  # 降低距离阈值
                        # 检查新站点位置是否远离所有现有站点
                        if self._is_location_safe_for_new_stop(mid_lat, mid_lon, MIN_DISTANCE_TO_EXISTING_STOPS):
                            suggestions.append({
                                'latitude': mid_lat,
                                'longitude': mid_lon,
                                'distance': distance,
                                'connects': [stop.name, s_stop.name],
                                'score': score * self.utilization_scores.get(s_id, 0) / distance
                            })
        # 按分数排序
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        # 如果没有足够的建议，降低要求再次尝试
        if len(suggestions) < num_suggestions:
            # 再次尝试，这次将距离阈值降至2公里
            additional_suggestions = []
            for stop, score in high_utilized:
                stop_id = stop.stop_ID
                first_level = set(n_id for n_id, _ in self.network.adjacency_list.get(stop_id, []))
                for s_id in self.network.stops.keys():
                    if s_id == stop_id or s_id in first_level:
                        continue
                    s_stop = self.network.get_stop_by_id(s_id)
                    # 计算两个站点之间的中点
                    mid_lat = (stop.latitude + s_stop.latitude) / 2
                    mid_lon = (stop.longitude + s_stop.longitude) / 2
                    # 计算两站点之间的距离
                    distance = self._calculate_distance(
                        stop.latitude, stop.longitude,
                        s_stop.latitude, s_stop.longitude
                    )
                    # 进一步降低距离阈值
                    if 1.5 < distance < 4.0:  # 距离在1.5-4公里之间
                        # 检查新站点位置是否远离所有现有站点
                        if self._is_location_safe_for_new_stop(mid_lat, mid_lon, MIN_DISTANCE_TO_EXISTING_STOPS):
                            additional_suggestions.append({
                                'latitude': mid_lat,
                                'longitude': mid_lon,
                                'distance': distance,
                                'connects': [stop.name, s_stop.name],
                                'score': score * 0.8  # 给这些建议一个稍低的分数
                            })
            # 合并建议
            suggestions.extend(additional_suggestions)
            suggestions.sort(key=lambda x: x['score'], reverse=True)
        self.potential_new_stops = suggestions[:num_suggestions]
        return self.potential_new_stops
    
    def optimize_network(self):
        """
        优化网络 - 综合分析
        
        Returns:
            优化建议的字典
        """
        # 1. 识别低利用率站点
        underutilized = self.identify_underutilized_stops()
        
        # 2. 查找可合并站点
        consolidation = self.find_stops_for_consolidation()
        
        # 3. 推荐新站点 - 增加建议数量到5个
        new_stops = self.suggest_new_stops(num_suggestions=5)
        
        # 返回优化建议
        return {
            'underutilized_stops': underutilized,
            'consolidation_candidates': consolidation,
            'new_stop_suggestions': new_stops
        }
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        使用Haversine公式计算两点间的地理距离（公里）
        """
        # 地球半径（公里）
        R = 6371.0
        
        # 转换为弧度
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # 经纬度差值
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine公式
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance 
    
    def _is_location_safe_for_new_stop(self, lat, lon, min_distance):
        """
        检查新站点位置是否与所有现有站点保持足够距离
        
        Args:
            lat: 新站点纬度
            lon: 新站点经度
            min_distance: 与现有站点的最小安全距离(公里)
            
        Returns:
            如果位置安全返回True，否则返回False
        """
        # 检查与每个现有站点的距离
        for stop_id, stop in self.network.stops.items():
            distance = self._calculate_distance(lat, lon, stop.latitude, stop.longitude)
            if distance < min_distance:
                # 太靠近现有站点
                return False
                
        # 通过所有检查，位置安全
        return True 