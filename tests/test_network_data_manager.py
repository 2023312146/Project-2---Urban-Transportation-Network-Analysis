import unittest
from project.core.NetworkDataManager import NetworkDataManager

class TestNetworkDataManager(unittest.TestCase):
    """Test cases for network data manager functionality"""
    """网络数据管理器功能的测试用例"""
    def setUp(self):
        self.data_manager = NetworkDataManager()
        
    def test_initial_data(self):
        """Test that initial data is properly loaded"""
        """测试初始数据是否正确加载"""
        self.assertGreater(len(self.data_manager.stations), 0)
        self.assertGreater(len(self.data_manager.distances), 0)
        
    def test_fixed_data_structure(self):
        """Test fixed data structure integrity"""
        """测试固定数据的结构完整性"""
        for station_id, station in self.data_manager.stations.items():
            required_keys = ["id", "name", "lat", "lon", "x", "y", "type", "wait_time", "connections"]
            for key in required_keys:
                self.assertIn(key, station)
            self.assertIsInstance(station["id"], str)
            self.assertIsInstance(station["name"], str)
            self.assertIsInstance(station["lat"], (int, float))
            self.assertIsInstance(station["lon"], (int, float))
            self.assertIsInstance(station["x"], (int, float))
            self.assertIsInstance(station["y"], (int, float))
            self.assertIsInstance(station["type"], str)
            self.assertIsInstance(station["wait_time"], int)
            self.assertIsInstance(station["connections"], list)
            
            """Test coordinate ranges"""
            """测试坐标范围"""
            self.assertGreaterEqual(station["x"], 0)
            self.assertGreaterEqual(station["y"], 0)
            self.assertLessEqual(station["x"], 1200)
            self.assertLessEqual(station["y"], 900)
    
    def test_station_name_to_id_mapping(self):
        """Test station name to ID mapping"""
        """测试站点名称到ID的映射"""
        for station_id, station in self.data_manager.stations.items():
            self.assertIn(station["name"], self.data_manager.station_name_to_id)
            self.assertEqual(self.data_manager.station_name_to_id[station["name"]], station_id)
    
    def test_station_type_wait_time_mapping(self):
        """Test wait time mapping for different station types"""
        """测试不同站点类型的等待时间映射"""
        expected_wait_times = {
            "Residential": 2,
            "Commercial": 4,
            "Industrial": 3,
            "Mixed": 3
        }
        
        for station in self.data_manager.stations.values():
            station_type = station["type"]
            wait_time = station["wait_time"]
            self.assertEqual(wait_time, expected_wait_times[station_type])
    
    def test_connection_consistency(self):
        """Test connection relationship consistency"""
        """测试连接关系的一致性"""
        for (from_id, to_id), distance in self.data_manager.distances.items():
            self.assertGreater(distance, 0)
            self.assertIn(from_id, self.data_manager.stations)
            self.assertIn(to_id, self.data_manager.stations)
            self.assertIn(to_id, self.data_manager.stations[from_id]["connections"])
    
    def test_add_station(self):
        """Test adding a new station"""
        """测试添加新站点"""
        initial_count = len(self.data_manager.stations)
        self.data_manager.add_station("Test Station", 100, 100, "Residential")
        self.assertEqual(len(self.data_manager.stations), initial_count + 1)
        
        """Verify new station data"""
        """验证新站点数据"""
        station_id = self.data_manager.station_name_to_id["Test Station"]
        station = self.data_manager.stations[station_id]
        self.assertEqual(station["name"], "Test Station")
        self.assertAlmostEqual(station["x"], 100, places=1)
        self.assertAlmostEqual(station["y"], 100, places=1)
        self.assertEqual(station["type"], "Residential")
        self.assertEqual(station["wait_time"], 2)
        self.assertEqual(station["connections"], [])
    
    def test_add_station_with_custom_wait_time(self):
        """Test adding station with custom wait time"""
        """测试添加站点时自定义等待时间"""
        self.data_manager.add_station("Custom Wait Station", 200, 200, "Commercial")
        station_id = self.data_manager.station_name_to_id["Custom Wait Station"]
        station = self.data_manager.stations[station_id]
        self.assertEqual(station["wait_time"], 4)
    
    def test_add_station_duplicate_name(self):
        """Test adding station with duplicate name"""
        """测试添加重复站点名称"""
        self.data_manager.add_station("Test Station", 100, 100, "Residential")
        with self.assertRaises(ValueError):
            self.data_manager.add_station("Test Station", 200, 200, "Commercial")
    
    def test_remove_station(self):
        """Test removing a station"""
        """测试删除站点"""
        self.data_manager.add_station("Test Station", 100, 100, "Residential")
        initial_count = len(self.data_manager.stations)
        
        self.data_manager.remove_station("Test Station")
        self.assertEqual(len(self.data_manager.stations), initial_count - 1)
        self.assertNotIn("Test Station", self.data_manager.station_name_to_id)
    
    def test_remove_station_cascade_effects(self):
        """Test cascade deletion effects when removing station"""
        """测试删除站点时的级联删除效果"""
        """Get two existing stations"""
        """获取两个现有站点"""
        station_names = list(self.data_manager.station_name_to_id.keys())[:2]
        from_name, to_name = station_names[0], station_names[1]
        
        """Check if connection exists, add if not"""
        """检查连接是否已存在，如果不存在则添加"""
        from_id = self.data_manager.station_name_to_id[from_name]
        to_id = self.data_manager.station_name_to_id[to_name]
        
        if (from_id, to_id) not in self.data_manager.distances:
            self.data_manager.add_connection(from_name, to_name, 10.0)
 
        initial_distances = len(self.data_manager.distances)
        
        """Calculate connections related to station to be deleted"""
        """计算与要删除站点相关的连接数量"""
        connections_to_remove = 0
        for (f, t) in self.data_manager.distances:
            if f == from_id or t == from_id:
                connections_to_remove += 1
        
        """Delete the starting station"""
        """删除起始站点"""
        self.data_manager.remove_station(from_name)
        
        """Verify connections are deleted"""
        """验证连接被删除"""
        expected_distances = initial_distances - connections_to_remove
        self.assertEqual(len(self.data_manager.distances), expected_distances)
        """Verify station is deleted"""
        """验证站点被删除"""
        self.assertNotIn(from_name, self.data_manager.station_name_to_id)
        """Verify all connections related to the station are deleted"""
        """验证所有与该站点相关的连接都被删除"""
        for (f, t) in self.data_manager.distances:
            self.assertNotEqual(f, from_id)
            self.assertNotEqual(t, from_id)
    
    def test_remove_nonexistent_station(self):
        """Test removing non-existent station"""
        """测试删除不存在的站点"""
        initial_count = len(self.data_manager.stations)
        self.data_manager.remove_station("Nonexistent Station")
        self.assertEqual(len(self.data_manager.stations), initial_count)
    
    def test_update_station_type(self):
        """Test updating station type"""
        """测试更新站点类型"""
        station_id = list(self.data_manager.stations.keys())[0]
        station_name = self.data_manager.stations[station_id]["name"]
        original_type = self.data_manager.stations[station_id]["type"]

        new_type = "Commercial" if original_type != "Commercial" else "Residential"
        self.data_manager.update_station_type(station_name, new_type)
        self.assertEqual(self.data_manager.stations[station_id]["type"], new_type)
    
    def test_update_nonexistent_station_type(self):
        """Test updating type of non-existent station"""
        """测试更新不存在站点的类型"""
        self.data_manager.update_station_type("Nonexistent Station", "Commercial")
    
    def test_add_connection(self):
        """Test adding a connection"""
        """测试添加连接"""
        station_names = list(self.data_manager.station_name_to_id.keys())[:2]
        from_name, to_name = station_names[0], station_names[1]

        from_id = self.data_manager.station_name_to_id[from_name]
        to_id = self.data_manager.station_name_to_id[to_name]
        if (from_id, to_id) in self.data_manager.distances:
            self.data_manager.remove_connection(from_name, to_name)

        initial_connections = len(self.data_manager.distances)
        self.data_manager.add_connection(from_name, to_name, 10.0)
        self.assertEqual(len(self.data_manager.distances), initial_connections + 1)
        
        """Verify connection data"""
        """验证连接数据"""
        self.assertIn((from_id, to_id), self.data_manager.distances)
        self.assertEqual(self.data_manager.distances[(from_id, to_id)], 10.0)
        self.assertIn(to_id, self.data_manager.stations[from_id]["connections"])
    
    def test_add_connection_nonexistent_stations(self):
        """Test adding connection between non-existent stations"""
        """测试添加不存在的站点连接"""
        with self.assertRaises(ValueError):
            self.data_manager.add_connection("Nonexistent1", "Nonexistent2", 10.0)
    
    def test_add_connection_already_exists(self):
        """Test adding connection that already exists"""
        """测试添加已存在的连接"""
        station_names = list(self.data_manager.station_name_to_id.keys())[:2]
        from_name, to_name = station_names[0], station_names[1]
        
        from_id = self.data_manager.station_name_to_id[from_name]
        to_id = self.data_manager.station_name_to_id[to_name]
        if (from_id, to_id) in self.data_manager.distances:
            self.data_manager.remove_connection(from_name, to_name)
        
        self.data_manager.add_connection(from_name, to_name, 10.0)
        with self.assertRaises(ValueError):
            self.data_manager.add_connection(from_name, to_name, 15.0)
    
    def test_remove_connection(self):
        """Test removing a connection"""
        """测试删除连接"""
        station_names = list(self.data_manager.station_name_to_id.keys())[:2]
        from_name, to_name = station_names[0], station_names[1]

 
        from_id = self.data_manager.station_name_to_id[from_name]
        to_id = self.data_manager.station_name_to_id[to_name]
        if (from_id, to_id) not in self.data_manager.distances:
            self.data_manager.add_connection(from_name, to_name, 10.0)

        initial_connections = len(self.data_manager.distances)
        self.data_manager.remove_connection(from_name, to_name)
        self.assertEqual(len(self.data_manager.distances), initial_connections - 1)
        
 
        self.assertNotIn((from_id, to_id), self.data_manager.distances)
        self.assertNotIn(to_id, self.data_manager.stations[from_id]["connections"])
    
    def test_remove_nonexistent_connection(self):
        """Test removing non-existent connection"""
        """测试删除不存在的连接"""
        initial_connections = len(self.data_manager.distances)
        self.data_manager.remove_connection("Nonexistent1", "Nonexistent2")
        self.assertEqual(len(self.data_manager.distances), initial_connections)
    
    def test_coordinate_conversion(self):
        """Test coordinate conversion reasonableness"""
        """测试坐标转换的合理性"""
        for station in self.data_manager.stations.values():
 
            self.assertGreaterEqual(station["lat"], 48.8)
            self.assertLessEqual(station["lat"], 49.0)
            self.assertGreaterEqual(station["lon"], 2.2)
            self.assertLessEqual(station["lon"], 2.4)
            self.assertGreaterEqual(station["x"], 80)
            self.assertLessEqual(station["x"], 1120)
            self.assertGreaterEqual(station["y"], 80)
            self.assertLessEqual(station["y"], 820)
    
    def test_preset_connections(self):
        """Test preset connections quantity and reasonableness"""
        """测试预设连接的数量和合理性"""
        self.assertGreaterEqual(len(self.data_manager.distances), 10)
        for distance in self.data_manager.distances.values():
            self.assertGreater(distance, 0)
            self.assertLess(distance, 20)
    
    def test_data_integrity_after_operations(self):
        """Test data integrity after operations"""
        """测试操作后数据完整性"""
        self.data_manager.add_station("Test Station", 100, 100, "Residential")
        self.data_manager.add_connection("Test Station", list(self.data_manager.station_name_to_id.keys())[0], 5.0)
  
        for station_id, station in self.data_manager.stations.items():
      
            for connected_id in station["connections"]:
                self.assertIn(connected_id, self.data_manager.stations)

            for (from_id, to_id), distance in self.data_manager.distances.items():
                if from_id == station_id:
                    self.assertIn(to_id, station["connections"])

if __name__ == '__main__':
    unittest.main()