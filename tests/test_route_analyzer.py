import unittest
from project.module.RouteAnalyzer import PathAnalyzer
from project.module.NetworkDataManager import NetworkDataManager

class TestRouteAnalyzer(unittest.TestCase):
    def setUp(self):
        self.data_manager = NetworkDataManager()
        # 添加测试数据
        self.data_manager.stations = {
            "1": {"id": "1", "name": "Station 1", "type": "Residential", "connections": ["2", "3"]},
            "2": {"id": "2", "name": "Station 2", "type": "Commercial", "connections": ["1", "4"]},
            "3": {"id": "3", "name": "Station 3", "type": "Industrial", "connections": ["1", "4"]},
            "4": {"id": "4", "name": "Station 4", "type": "Mixed", "connections": ["2", "3"]}
        }
        self.data_manager.distances = {
            ("1", "2"): 5.0,
            ("2", "1"): 5.0,
            ("1", "3"): 3.0,
            ("3", "1"): 3.0,
            ("2", "4"): 4.0,
            ("4", "2"): 4.0,
            ("3", "4"): 2.0,
            ("4", "3"): 2.0
        }
        self.path_analyzer = PathAnalyzer(self.data_manager)
        
    def test_find_all_paths(self):
        # 测试查找所有路径
        paths = self.path_analyzer.find_all_paths("1", "4")
        self.assertEqual(len(paths), 2)  # 应该有两条路径
        
        # 验证路径格式
        for path in paths:
            self.assertIsInstance(path, list)
            self.assertGreater(len(path), 1)
            self.assertEqual(path[0], "1")
            self.assertEqual(path[-1], "4")
            
    def test_find_best_path(self):
        # 测试查找最优路径
        path = self.path_analyzer.find_best_path("1", "4")
        self.assertEqual(len(path), 3)  # 最优路径应该是1->3->4
        self.assertEqual(path, ["1", "3", "4"])
        
    def test_find_highest_degree_station(self):
        # 测试查找最高连接度的站点
        station_id = self.path_analyzer.find_highest_degree_station()
        self.assertIsNotNone(station_id)
        self.assertIn(station_id, ["1", "4"])  # 站点1和4都有2个连接
        
    def test_invalid_stations(self):
        # 测试无效站点ID
        self.assertEqual(len(self.path_analyzer.find_all_paths("100", "200")), 0)
        self.assertEqual(len(self.path_analyzer.find_best_path("100", "200")), 0)

if __name__ == '__main__':
    unittest.main()