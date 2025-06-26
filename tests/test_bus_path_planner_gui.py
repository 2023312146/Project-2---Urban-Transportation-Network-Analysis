import unittest
from PyQt5.QtWidgets import QApplication
from project.module.BusPathPlannerGUI import BusNetworkVisualization
from project.module.NetworkDataManager import NetworkDataManager
from project.module.RouteAnalyzer import PathAnalyzer

class TestBusPathPlannerGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])
        
    def setUp(self):
        self.data_manager = NetworkDataManager()
        self.path_analyzer = PathAnalyzer(self.data_manager)
        self.gui = BusNetworkVisualization(self.data_manager, self.path_analyzer)
        
    def test_initial_state(self):
        # 测试初始状态
        self.assertIsNone(self.gui.selected_start)
        self.assertIsNone(self.gui.selected_end)
        self.assertEqual(len(self.gui.all_paths), 0)
        self.assertEqual(len(self.gui.best_path), 0)
        
    def test_path_selection(self):
        # 测试路径选择逻辑
        station_names = list(self.data_manager.stations.keys())[:2]
        self.gui.selected_start = str(station_names[0])  # Ensure string type
        self.gui.selected_end = str(station_names[1])    # Ensure string type
        
        self.gui.update_path_info()
        self.assertGreater(len(self.gui.all_paths), 0)
        if self.gui.best_path:
            self.assertGreater(len(self.gui.best_path), 0)
            # Verify path contains strings
            self.assertTrue(all(isinstance(station, str) for station in self.gui.best_path))
            
    def test_clear_selection(self):
        # 测试清除选择
        station_names = list(self.data_manager.stations.keys())[:2]
        self.gui.selected_start = station_names[0]
        self.gui.selected_end = station_names[1]
        
        self.gui.clear_selection()
        self.assertIsNone(self.gui.selected_start)
        self.assertIsNone(self.gui.selected_end)
        self.assertEqual(len(self.gui.all_paths), 0)
        self.assertEqual(len(self.gui.best_path), 0)

    def test_add_remove_connection(self):
        # 测试添加和删除连接
        station_names = list(self.data_manager.stations.keys())[:2]
        from_name, to_name = station_names[0], station_names[1]
        
        # 先确保连接不存在
        if (from_name, to_name) in self.data_manager.distances:
            self.data_manager.remove_connection(from_name, to_name)
        
        initial_connections = len(self.data_manager.distances)
        
        # 测试添加连接
        self.data_manager.add_connection(from_name, to_name, 10.0)
        self.assertEqual(len(self.data_manager.distances), initial_connections + 1)
        self.assertIn((from_name, to_name), self.data_manager.distances)
        self.assertIn(to_name, self.data_manager.stations[from_name]["connections"])
        
        # 测试删除连接
        self.data_manager.remove_connection(from_name, to_name)
        self.assertEqual(len(self.data_manager.distances), initial_connections)
        self.assertNotIn((from_name, to_name), self.data_manager.distances)
        self.assertNotIn(to_name, self.data_manager.stations[from_name]["connections"])

if __name__ == '__main__':
    unittest.main()