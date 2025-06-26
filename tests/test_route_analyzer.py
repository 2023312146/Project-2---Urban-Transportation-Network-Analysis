import unittest
from project.module.RouteAnalyzer import PathAnalyzer
from project.module.NetworkDataManager import NetworkDataManager

class TestRouteAnalyzer(unittest.TestCase):
    def setUp(self):
        self.data_manager = NetworkDataManager()
        self.path_analyzer = PathAnalyzer(self.data_manager)
        
    def test_find_all_paths(self):
        # 测试查找所有路径
        paths = self.path_analyzer.find_all_paths(1, 4)
        self.assertGreater(len(paths), 0)
        
        # 验证路径格式
        for path in paths:
            self.assertIsInstance(path, list)
            self.assertGreater(len(path), 1)
            
    def test_find_best_path(self):
        # 测试查找最优路径
        path = self.path_analyzer.find_best_path(1, 4)
        self.assertGreater(len(path), 0)
        
    def test_find_highest_degree_station(self):
        # 测试查找最高连接度的站点
        station_id = self.path_analyzer.find_highest_degree_station()
        self.assertIsNotNone(station_id)
        self.assertIn(station_id, self.data_manager.stations)
        
    def test_invalid_stations(self):
        # 测试无效站点ID
        self.assertEqual(len(self.path_analyzer.find_all_paths(100, 200)), 0)
        self.assertEqual(len(self.path_analyzer.find_best_path(100, 200)), 0)

if __name__ == '__main__':
    unittest.main()