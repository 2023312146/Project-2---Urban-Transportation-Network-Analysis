import unittest
from project.module.stop import Stop, ZoneType
from project.module.network import TransportNetwork

"""Test class for Stop functionality"""
"""站点功能测试类"""
class TestStop(unittest.TestCase):
    def setUp(self):
        """Setup test data for stop creation"""
        """设置站点创建测试数据"""
        self.stop_data = {
            'stop_id': '1',
            'name': 'Central Station',
            'latitude': '48.8566',
            'longitude': '2.3522',
            'zone_type': 'Commercial'
        }
    
    """Test basic stop creation with constructor"""
    """测试使用构造函数的基本站点创建"""
    def test_stop_creation(self):
        stop = Stop(1, "Test Stop", 0.0, 0.0, ZoneType.RESIDENTIAL)
        self.assertEqual(stop.stop_ID, 1)
        self.assertEqual(stop.name, "Test Stop")
        self.assertEqual(stop.zone_type, ZoneType.RESIDENTIAL)
    
    """Test stop creation from dictionary data"""
    """测试从字典数据创建站点"""
    def test_from_dict(self):
        stop = Stop.from_dict(self.stop_data)
        self.assertEqual(stop.stop_ID, 1)
        self.assertEqual(stop.name, "Central Station")
        self.assertEqual(stop.latitude, 48.8566)
        self.assertEqual(stop.zone_type, ZoneType.COMMERCIAL)
    
    """Test zone type validation and error handling"""
    """测试区域类型验证和错误处理"""
    def test_zone_type_validation(self):
        with self.assertRaises(TypeError):
            Stop(1, "Invalid", 0.0, 0.0, "InvalidType")
        stop = Stop(1, "Valid", 0.0, 0.0, ZoneType.INDUSTRIAL)
        with self.assertRaises(TypeError):
            stop.zone_type = "InvalidType"
    
    """Test stop equality comparison"""
    """测试站点相等性比较"""
    def test_equality(self):
        """Create stops with same and different IDs for comparison"""
        """创建具有相同和不同ID的站点进行比较"""
        stop1 = Stop(1, "Same", 0.0, 0.0, ZoneType.MIXED)
        stop2 = Stop(1, "Same", 0.0, 0.0, ZoneType.MIXED)
        stop3 = Stop(2, "Different", 0.0, 0.0, ZoneType.MIXED)
        self.assertEqual(stop1, stop2)
        self.assertNotEqual(stop1, stop3)

if __name__ == '__main__':
    unittest.main()