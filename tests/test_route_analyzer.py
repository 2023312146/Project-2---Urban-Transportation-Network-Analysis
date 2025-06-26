import unittest
from project.module.RouteAnalyzer import PathAnalyzer
from project.module.NetworkDataManager import NetworkDataManager

class TestRouteAnalyzer(unittest.TestCase):
    def setUp(self):
        self.data_manager = NetworkDataManager()
        # 设置测试数据
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
    
    def test_find_all_paths_basic(self):
        """测试基本路径查找功能"""
        paths = self.analyzer.find_all_paths("1", "4")
        self.assertEqual(len(paths), 2)  # 1-2-4 和 1-3-4
        self.assertIn(["1", "2", "4"], paths)
        self.assertIn(["1", "3", "4"], paths)
    
    def test_find_all_paths_with_efficiency(self):
        """测试带效率计算的路径查找"""
        paths = self.analyzer.find_all_paths("1", "4", include_efficiency=True)
        self.assertEqual(len(paths), 2)
        
        # 验证效率计算正确性
        for path in paths:
            self.assertIn("path", path)
            self.assertIn("distance", path)
            self.assertIn("efficiency", path)
            self.assertGreater(path["efficiency"], 0)
            self.assertIsInstance(path["path"], list)
            self.assertIsInstance(path["distance"], float)
            self.assertIsInstance(path["efficiency"], float)
            
        # 路径1-2-4应该有更高效率（实际算法结果）
        path1 = next(p for p in paths if p["path"] == ["1", "2", "4"])
        path2 = next(p for p in paths if p["path"] == ["1", "3", "4"])
        self.assertGreater(path1["efficiency"], path2["efficiency"])
    
    def test_find_best_path_by_distance(self):
        """测试按距离查找最优路径"""
        path = self.analyzer.find_best_path("1", "4")
        self.assertIsInstance(path, list)
        self.assertEqual(path, ["1", "3", "4"])  # 最短距离路径
    
    def test_find_best_path_by_efficiency(self):
        """测试按效率查找最优路径"""
        best_path = self.analyzer.find_best_path("1", "4", by_efficiency=True)
        self.assertIsInstance(best_path, dict)
        self.assertEqual(best_path["path"], ["1", "2", "4"])
        self.assertAlmostEqual(best_path["distance"], 9.0)  # 5+4=9km
        self.assertGreater(best_path["efficiency"], 18)  # 实际效率更高
    
    def test_compare_best_paths(self):
        """测试比较最短路径和效率最优路径"""
        result = self.analyzer.compare_best_paths("1", "4")
        
        # 验证返回结构
        self.assertIsInstance(result, dict)
        self.assertEqual(result["dijkstra_path"], ["1", "3", "4"])
        self.assertEqual(result["efficiency_path"], ["1", "2", "4"])
        self.assertFalse(result["is_same"])
        
        # 验证距离和效率值
        self.assertAlmostEqual(result["dijkstra_distance"], 5.0)
        self.assertAlmostEqual(result["efficiency_distance"], 9.0)
        self.assertGreater(result["efficiency_value"], 18)
    
    def test_find_highest_degree_station(self):
        """测试查找最高连接度站点"""
        hub = self.analyzer.find_highest_degree_station()
        self.assertIn(hub, ["1", "4"])  # 站点1和4都有2个连接
    
    def test_invalid_stations(self):
        """测试无效站点处理"""
        # 测试不存在的站点
        self.assertEqual(self.analyzer.find_all_paths("99", "100"), [])
        self.assertEqual(self.analyzer.find_best_path("99", "100"), [])
        self.assertEqual(self.analyzer.find_best_path("99", "100", by_efficiency=True), {})
        self.assertIsNone(self.analyzer.compare_best_paths("99", "100"))
        
        # 测试相同起点和终点
        self.assertEqual(self.analyzer.find_all_paths("1", "1"), [["1"]])
    
    def test_efficiency_calculation(self):
        """测试效率计算准确性"""
        # 路径1-3-4的效率
        paths = self.analyzer.find_all_paths("1", "4", include_efficiency=True)
        path = next(p for p in paths if p["path"] == ["1", "3", "4"])
        self.assertAlmostEqual(path["efficiency"], 16.63, places=1)
    
    def test_empty_network(self):
        """测试空网络处理"""
        empty_manager = NetworkDataManager()
        empty_analyzer = PathAnalyzer(empty_manager)
        
        self.assertEqual(empty_analyzer.find_all_paths("1", "2"), [["1", "2"]])
        self.assertEqual(empty_analyzer.find_best_path("1", "2"), ["1", "2"])
        self.assertIn("path", empty_analyzer.find_best_path("1", "2", by_efficiency=True))
        result = empty_analyzer.compare_best_paths("1", "2")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["dijkstra_path"], ["1", "2"])
        self.assertEqual(result["efficiency_path"], ["1", "2"])
        self.assertTrue(result["is_same"])

if __name__ == '__main__':
    unittest.main()