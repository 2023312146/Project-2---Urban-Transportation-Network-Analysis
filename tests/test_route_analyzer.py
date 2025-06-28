import unittest
from project.module.RouteAnalyzer import PathAnalyzer
from project.module.NetworkDataManager import NetworkDataManager
from project.module.stop import ZoneType

"""Test class for route analyzer functionality"""
"""路径分析器功能测试类"""
class TestRouteAnalyzer(unittest.TestCase):
    def setUp(self):
        self.data_manager = NetworkDataManager()
        """Setup test data"""
        """设置测试数据"""
        self.data_manager.stations = {
            "1": {"id": "1", "name": "Station 1", "type": "Residential", "connections": ["2", "3"]},
            "2": {"id": "2", "name": "Station 2", "type": "Commercial", "connections": ["1", "4"]},
            "3": {"id": "3", "name": "Station 3", "type": "Industrial", "connections": ["1", "4"]},
            "4": {"id": "4", "name": "Station 4", "type": "Mixed", "connections": ["2", "3"]}
        }
        self.data_manager.distances = {
            ("1", "2"): 5.0,  # Residential -> Commercial
            ("2", "1"): 5.0,
            ("1", "3"): 3.0,  # Residential -> Industrial
            ("3", "1"): 3.0,
            ("2", "4"): 4.0,  # Commercial -> Mixed
            ("4", "2"): 4.0,
            ("3", "4"): 2.0,  # Industrial -> Mixed
            ("4", "3"): 2.0
        }
        self.analyzer = PathAnalyzer(self.data_manager)
    
    """Test transport network creation"""
    """测试交通网络构建"""
    def test_create_transport_network(self):
        network, stops = self.analyzer._create_transport_network()
        self.assertIsNotNone(network)
        self.assertEqual(len(stops), 4)
        
        for station_id, stop in stops.items():
            station_data = self.data_manager.stations[station_id]
            self.assertEqual(stop.name, station_data['name'])
            self.assertEqual(stop.stop_ID, station_data['id'])
            
            if station_data['type'] == 'Residential':
                self.assertEqual(stop.zone_type, ZoneType.RESIDENTIAL)
            elif station_data['type'] == 'Commercial':
                self.assertEqual(stop.zone_type, ZoneType.COMMERCIAL)
            elif station_data['type'] == 'Industrial':
                self.assertEqual(stop.zone_type, ZoneType.INDUSTRIAL)
            elif station_data['type'] == 'Mixed':
                self.assertEqual(stop.zone_type, ZoneType.MIXED)
    
    """Test wait time mapping for different station types"""
    """测试不同站点类型的等待时间"""
    def test_wait_time_mapping(self):
        self.assertEqual(self.analyzer.WAIT_TIMES[ZoneType.RESIDENTIAL], 2)
        self.assertEqual(self.analyzer.WAIT_TIMES[ZoneType.COMMERCIAL], 4)
        self.assertEqual(self.analyzer.WAIT_TIMES[ZoneType.INDUSTRIAL], 3)
        self.assertEqual(self.analyzer.WAIT_TIMES[ZoneType.MIXED], 3)
        for wait_time in self.analyzer.WAIT_TIMES.values():
            self.assertGreater(wait_time, 0)
    
    """Test detailed efficiency calculation logic"""
    """测试效率计算的详细逻辑"""
    def test_calculate_efficiency_detailed(self):
        network, stops = self.analyzer._create_transport_network()
        path1 = [stops['1'], stops['2'], stops['4']]  # Residential -> Commercial -> Mixed
        path2 = [stops['1'], stops['3'], stops['4']]  # Residential -> Industrial -> Mixed
        
        eff1 = self.analyzer._calculate_efficiency(path1, 9.0)
        eff2 = self.analyzer._calculate_efficiency(path2, 5.0)
        self.assertGreater(eff1, 0)
        self.assertGreater(eff2, 0)
        self.assertNotEqual(eff1, eff2)
        self.assertAlmostEqual(eff1, 18.33, places=1)
        self.assertAlmostEqual(eff2, 16.67, places=1)
    
    """Test edge cases for efficiency calculation"""
    """测试效率计算的边界情况"""
    def test_efficiency_calculation_edge_cases(self):
        network, stops = self.analyzer._create_transport_network()
        eff = self.analyzer._calculate_efficiency([], 0.0)
        self.assertEqual(eff, 0.0)
        eff = self.analyzer._calculate_efficiency([stops['1']], 0.0)
        self.assertEqual(eff, 0.0)
        eff = self.analyzer._calculate_efficiency([stops['1'], stops['2']], 0.0)
        self.assertEqual(eff, 0.0)
        eff = self.analyzer._calculate_efficiency([stops['1'], stops['2']], -1.0)
        self.assertEqual(eff, 0.0)
        eff = self.analyzer._calculate_efficiency([stops['1'], stops['2']], 0.001)
        self.assertGreater(eff, 0)
    
    """Test basic path finding functionality"""
    """测试基本路径查找功能"""
    def test_find_all_paths_basic(self):
        paths = self.analyzer.find_all_paths("1", "4")
        self.assertEqual(len(paths), 2)  # 1-2-4 and 1-3-4
        # 1-2-4 和 1-3-4
        self.assertIn(["1", "2", "4"], paths)
        self.assertIn(["1", "3", "4"], paths)
    
    """Test path finding with efficiency calculation"""
    """测试带效率计算的路径查找"""
    def test_find_all_paths_with_efficiency(self):
        paths = self.analyzer.find_all_paths("1", "4", include_efficiency=True)
        self.assertEqual(len(paths), 2)
        for path in paths:
            self.assertIn("path", path)
            self.assertIn("distance", path)
            self.assertIn("efficiency", path)
            self.assertGreater(path["efficiency"], 0)
            self.assertIsInstance(path["path"], list)
            self.assertIsInstance(path["distance"], float)
            self.assertIsInstance(path["efficiency"], float)
        path1 = next(p for p in paths if p["path"] == ["1", "2", "4"])
        path2 = next(p for p in paths if p["path"] == ["1", "3", "4"])
        self.assertGreater(path1["efficiency"], path2["efficiency"])
    
    """Test edge cases for path finding"""
    """测试路径查找的边界情况"""
    def test_path_finding_edge_cases(self):
        
        paths = self.analyzer.find_all_paths("1", "1")
        self.assertEqual(paths, [["1"]])
        paths = self.analyzer.find_all_paths("1", "2")
        self.assertIn(["1", "2"], paths)
        self.assertGreater(len(paths), 0)
        paths = self.analyzer.find_all_paths("1", "99")
        self.assertEqual(paths, [])
        paths = self.analyzer.find_all_paths("99", "100")
        self.assertEqual(paths, [])
        paths = self.analyzer.find_all_paths("1", "99", include_efficiency=True)
        self.assertEqual(paths, [])
    
    """Test finding best path by distance"""
    """测试按距离查找最优路径"""
    def test_find_best_path_by_distance(self):
        path = self.analyzer.find_best_path("1", "4")
        self.assertIsInstance(path, list)
        self.assertEqual(path, ["1", "3", "4"])  
        
    
    """Test finding best path by efficiency"""
    """测试按效率查找最优路径"""
    def test_find_best_path_by_efficiency(self):
        best_path = self.analyzer.find_best_path("1", "4", by_efficiency=True)
        self.assertIsInstance(best_path, dict)
        self.assertEqual(best_path["path"], ["1", "2", "4"])
        self.assertAlmostEqual(best_path["distance"], 9.0)  
        self.assertGreater(best_path["efficiency"], 18) 
    
    """Test edge cases for best path finding"""
    """测试最优路径查找的边界情况"""
    def test_find_best_path_edge_cases(self):
        path = self.analyzer.find_best_path("99", "100")
        self.assertEqual(path, [])
        path = self.analyzer.find_best_path("99", "100", by_efficiency=True)
        self.assertEqual(path, {})
        path = self.analyzer.find_best_path("1", "1")
        self.assertEqual(path, ["1"])
        path = self.analyzer.find_best_path("1", "1", by_efficiency=True)
        self.assertIsInstance(path, dict)
        self.assertEqual(path["path"], ["1"])
    
    """Test comparing shortest path and efficiency optimal path"""
    """测试比较最短路径和效率最优路径"""
    def test_compare_best_paths(self):
        result = self.analyzer.compare_best_paths("1", "4")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["dijkstra_path"], ["1", "3", "4"])
        self.assertEqual(result["efficiency_path"], ["1", "2", "4"])
        self.assertFalse(result["is_same"])
        self.assertAlmostEqual(result["dijkstra_distance"], 5.0)
        self.assertAlmostEqual(result["efficiency_distance"], 9.0)
        self.assertGreater(result["efficiency_value"], 18)
    
    """Test detailed logic for path comparison"""
    """测试路径比较的详细逻辑"""
    def test_compare_best_paths_detailed(self):
        result = self.analyzer.compare_best_paths("1", "4")
        required_fields = ['dijkstra_path', 'dijkstra_distance', 'efficiency_path', 
                          'efficiency_value', 'efficiency_distance', 'is_same']
        for field in required_fields:
            self.assertIn(field, result)
        self.assertIsInstance(result['is_same'], bool)
        self.assertIsInstance(result['dijkstra_distance'], float)
        self.assertIsInstance(result['efficiency_distance'], float)
        self.assertIsInstance(result['efficiency_value'], float)
        self.assertGreater(len(result['dijkstra_path']), 0)
        self.assertGreater(len(result['efficiency_path']), 0)
        self.assertGreater(result['dijkstra_distance'], 0)
        self.assertGreater(result['efficiency_distance'], 0)
        self.assertGreater(result['efficiency_value'], 0)
    
    """Test edge cases for path comparison"""
    """测试路径比较的边界情况"""
    def test_compare_best_paths_edge_cases(self):
        
        result = self.analyzer.compare_best_paths("99", "100")
        self.assertIsNone(result)
        result = self.analyzer.compare_best_paths("1", "1")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["dijkstra_path"], ["1"])
        self.assertEqual(result["efficiency_path"], ["1"])
        self.assertTrue(result["is_same"])
        self.assertEqual(result["dijkstra_distance"], 0.0)
        self.assertEqual(result["efficiency_distance"], 0.0)
    
    """Test finding highest degree station"""
    """测试查找最高连接度站点"""
    def test_find_highest_degree_station(self):
        hub = self.analyzer.find_highest_degree_station()
        self.assertIn(hub, ["1", "4"])  # Stations 1 and 4 both have 2 connections
        # 站点1和4都有2个连接
    
    """Test detailed logic for highest degree station finding"""
    """测试最高度站点查找的详细逻辑"""
    def test_find_highest_degree_station_detailed(self):
        hub = self.analyzer.find_highest_degree_station()
        out_degrees = {station_id: len(station["connections"]) 
                      for station_id, station in self.data_manager.stations.items()}
        in_degrees = {station_id: 0 for station_id in self.data_manager.stations}
        
        for station_id, station in self.data_manager.stations.items():
            for to_id in station["connections"]:
                if to_id in in_degrees:
                    in_degrees[to_id] += 1
        
        max_degree = 0
        expected_hub = None
        for station_id in self.data_manager.stations:
            degree = out_degrees.get(station_id, 0) + in_degrees.get(station_id, 0)
            if degree > max_degree:
                max_degree = degree
                expected_hub = station_id
        
        self.assertEqual(hub, expected_hub)
        
        """Verify degree calculation correctness"""
        """验证度数计算正确性"""
        self.assertEqual(out_degrees["1"], 2)  
        self.assertEqual(out_degrees["2"], 2)  
        self.assertEqual(out_degrees["3"], 2)  
        self.assertEqual(out_degrees["4"], 2)  
        self.assertEqual(in_degrees["1"], 2) 
        self.assertEqual(in_degrees["2"], 2)  
        self.assertEqual(in_degrees["3"], 2)  
        self.assertEqual(in_degrees["4"], 2) 
       
    
    """Test network data consistency"""
    """测试网络数据的一致性"""
    def test_network_data_consistency(self):
        for (from_id, to_id) in self.data_manager.distances.keys():
            self.assertIn(from_id, self.data_manager.stations)
            self.assertIn(to_id, self.data_manager.stations)
            self.assertIn(to_id, self.data_manager.stations[from_id]["connections"])
        for station_id, station in self.data_manager.stations.items():
            for to_id in station["connections"]:
                self.assertIn((station_id, to_id), self.data_manager.distances)
    
    """Test invalid station handling"""
    """测试无效站点处理"""
    def test_invalid_stations(self):
        self.assertEqual(self.analyzer.find_all_paths("99", "100"), [])
        self.assertEqual(self.analyzer.find_best_path("99", "100"), [])
        self.assertEqual(self.analyzer.find_best_path("99", "100", by_efficiency=True), {})
        self.assertIsNone(self.analyzer.compare_best_paths("99", "100"))
        self.assertEqual(self.analyzer.find_all_paths("1", "1"), [["1"]])
    
    """Test efficiency calculation accuracy"""
    """测试效率计算准确性"""
    def test_efficiency_calculation(self):
        paths = self.analyzer.find_all_paths("1", "4", include_efficiency=True)
        path = next(p for p in paths if p["path"] == ["1", "3", "4"])
        self.assertAlmostEqual(path["efficiency"], 16.63, places=1)
    
    """Test empty network handling"""
    """测试空网络处理"""
    def test_empty_network(self):
        empty_manager = NetworkDataManager()
        empty_manager.stations = {}
        empty_manager.distances = {}
        empty_manager.lines = {}
        empty_manager.station_name_to_id = {}
        empty_analyzer = PathAnalyzer(empty_manager)
        self.assertEqual(empty_analyzer.find_all_paths("1", "2"), [])
        self.assertEqual(empty_analyzer.find_best_path("1", "2"), [])
        self.assertEqual(empty_analyzer.find_best_path("1", "2", by_efficiency=True), {})
        self.assertIsNone(empty_analyzer.compare_best_paths("1", "2"))
        self.assertIsNone(empty_analyzer.find_highest_degree_station())
    
    """Test single station network"""
    """测试单站点网络"""
    def test_single_station_network(self):
        single_manager = NetworkDataManager()
        single_manager.stations = {
            "1": {"id": "1", "name": "Station 1", "type": "Residential", "connections": []}
        }
        single_manager.distances = {}
        single_analyzer = PathAnalyzer(single_manager)
        self.assertEqual(single_analyzer.find_all_paths("1", "1"), [["1"]])
        self.assertEqual(single_analyzer.find_best_path("1", "1"), ["1"])
        self.assertEqual(single_analyzer.find_all_paths("1", "2"), [])
        self.assertEqual(single_analyzer.find_best_path("1", "2"), [])
        self.assertIsNone(single_analyzer.find_highest_degree_station())

if __name__ == '__main__':
    unittest.main()