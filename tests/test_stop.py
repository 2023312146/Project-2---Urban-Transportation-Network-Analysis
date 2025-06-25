import unittest
from project.module.stop import Stop, ZoneType
from project.module.network import TransportNetwork

class TestStop(unittest.TestCase):
    def setUp(self):
        self.stop_data = {
            'stop_id': '1',
            'name': 'Central Station',
            'latitude': '48.8566',
            'longitude': '2.3522',
            'zone_type': 'Commercial'
        }
    
    def test_stop_creation(self):
        stop = Stop(1, "Test Stop", 0.0, 0.0, ZoneType.RESIDENTIAL)
        self.assertEqual(stop.stop_ID, 1)
        self.assertEqual(stop.name, "Test Stop")
        self.assertEqual(stop.zone_type, ZoneType.RESIDENTIAL)
    
    def test_from_dict(self):
        stop = Stop.from_dict(self.stop_data)
        self.assertEqual(stop.stop_ID, 1)
        self.assertEqual(stop.name, "Central Station")
        self.assertEqual(stop.latitude, 48.8566)
        self.assertEqual(stop.zone_type, ZoneType.COMMERCIAL)
    
    def test_zone_type_validation(self):
        with self.assertRaises(TypeError):
            Stop(1, "Invalid", 0.0, 0.0, "InvalidType")
        
        stop = Stop(1, "Valid", 0.0, 0.0, ZoneType.INDUSTRIAL)
        with self.assertRaises(TypeError):
            stop.zone_type = "InvalidType"
    
    def test_equality(self):
        stop1 = Stop(1, "Same", 0.0, 0.0, ZoneType.MIXED)
        stop2 = Stop(1, "Same", 0.0, 0.0, ZoneType.MIXED)
        stop3 = Stop(2, "Different", 0.0, 0.0, ZoneType.MIXED)
        
        self.assertEqual(stop1, stop2)
        self.assertNotEqual(stop1, stop3)

if __name__ == '__main__':
    unittest.main()