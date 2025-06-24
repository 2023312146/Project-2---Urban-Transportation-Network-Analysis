import unittest
from project.module.stop import Stop, ZoneType  

class TestStop(unittest.TestCase):
    def test_stop_creation(self):
        stop = Stop("S1", "Central Station", 48.8584, 2.3470, ZoneType.COMMERCIAL)
        self.assertEqual(stop.stop_ID, "S1")
        self.assertEqual(stop.name, "Central Station")
        self.assertEqual(stop.latitude, 48.8584)
        self.assertEqual(stop.longitude, 2.3470)
        self.assertEqual(stop.zone_type, ZoneType.COMMERCIAL)

    def test_zone_type_validation(self):
        with self.assertRaises(TypeError):
            Stop("S2", "Residential Area", 48.86, 2.35, "Residential")
        
        stop = Stop("S3", "Industrial Zone", 48.87, 2.36, ZoneType.INDUSTRIAL)
        with self.assertRaises(TypeError):
            stop.zone_type = "Mixed"

    def test_repr(self):
        stop = Stop("S4", "Mixed Zone", 48.88, 2.37, ZoneType.MIXED)
        self.assertEqual(repr(stop), "Stop(ID=S4, Name='Mixed Zone', Zone='Mixed')")

    def test_eq(self):
        stop1 = Stop("S5", "Stop A", 48.89, 2.38, ZoneType.RESIDENTIAL)
        stop2 = Stop("S5", "Stop B", 48.90, 2.39, ZoneType.RESIDENTIAL)
        stop3 = Stop("S6", "Stop C", 48.91, 2.40, ZoneType.COMMERCIAL)
        self.assertNotEqual(stop1, stop3)

    def test_lt(self):
        stop1 = Stop("S7", "Stop D", 48.92, 2.41, ZoneType.INDUSTRIAL)
        stop2 = Stop("S8", "Stop E", 48.93, 2.42, ZoneType.MIXED)
        self.assertLess(stop1, stop2)
        self.assertGreater(stop2, stop1)

    def test_hash(self):
        stop1 = Stop("S9", "Stop F", 1, 1, ZoneType.RESIDENTIAL)
        stop2 = Stop("S9", "Stop G", 2, 2, ZoneType.COMMERCIAL)
        stop3 = Stop("S10", "Stop H", 3, 3, ZoneType.INDUSTRIAL)
        s = {stop1, stop2, stop3}
        self.assertEqual(len(s), 3)

if __name__ == '__main__':
    unittest.main()