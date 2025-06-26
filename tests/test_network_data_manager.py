import unittest
from project.module.NetworkDataManager import NetworkDataManager

class TestNetworkDataManager(unittest.TestCase):
    def setUp(self):
        self.data_manager = NetworkDataManager()
        
    def test_initial_data(self):
        # 测试初始数据是否正确加载
        self.assertGreater(len(self.data_manager.stations), 0)
        self.assertGreater(len(self.data_manager.distances), 0)
        self.assertGreater(len(self.data_manager.lines), 0)
        
    def test_add_remove_station(self):
        # 测试添加和删除站点
        initial_count = len(self.data_manager.stations)
        self.data_manager.add_station("Test Station", 100, 100, "Residential")  # 添加station_type参数
        self.assertEqual(len(self.data_manager.stations), initial_count + 1)
        
        new_name = "Test Station"
        self.data_manager.remove_station(new_name)
        self.assertEqual(len(self.data_manager.stations), initial_count)
        
    def test_add_remove_connection(self):
        # 测试添加和删除连接
        station_names = list(self.data_manager.stations.keys())[:2]
        from_name, to_name = station_names[0], station_names[1]
        
        # 确保连接不存在
        if (from_name, to_name) in self.data_manager.distances:
            self.data_manager.remove_connection(from_name, to_name)
        
        initial_connections = len(self.data_manager.distances)
        self.data_manager.add_connection(from_name, to_name, 10.0)
        self.assertEqual(len(self.data_manager.distances), initial_connections + 1)
        
        self.data_manager.remove_connection(from_name, to_name)
        self.assertEqual(len(self.data_manager.distances), initial_connections)
        
    def test_update_station_type(self):
        # 测试更新站点类型
        station_name = list(self.data_manager.stations.keys())[0]
        original_type = self.data_manager.stations[station_name]["type"]
        
        new_type = "Commercial" if original_type != "Commercial" else "Residential"
        self.data_manager.update_station_type(station_name, new_type)
        self.assertEqual(self.data_manager.stations[station_name]["type"], new_type)

if __name__ == '__main__':
    unittest.main()