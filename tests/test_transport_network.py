import unittest
from .data_structures import Stop, ZoneType
from .network import TransportNetwork

class TestStop(unittest.TestCase):
    def test_stop_creation(self):
        stop = Stop("S1", "Central Station", 48.8584, 2.2945, ZoneType.COMMERCIAL)
        self.assertEqual(stop.stop_ID, "S1")
        self.assertEqual(stop.name, "Central Station")
        self.assertEqual(stop.zone_type, ZoneType.COMMERCIAL)

    def test_invalid_zone_type(self):
        with self.assertRaises(TypeError):
            Stop("S2", "Residential Stop", 48.86, 2.30, "Residential")

    def test_zone_type_setter(self):
        stop = Stop("S3", "Industrial Zone", 48.80, 2.35, ZoneType.INDUSTRIAL)
        self.assertEqual(stop.zone_type, ZoneType.INDUSTRIAL)
        stop.zone_type = ZoneType.MIXED
        self.assertEqual(stop.zone_type, ZoneType.MIXED)
        with self.assertRaises(TypeError):
            stop.zone_type = "some_string"

    def test_repr(self):
        stop = Stop("S4", "Mixed Zone", 48.90, 2.40, ZoneType.MIXED)
        expected_repr = "Stop(ID=S4, Name='Mixed Zone', Zone='Mixed')"
        self.assertEqual(repr(stop), expected_repr)

    def test_comparison(self):
        stop1 = Stop("S1", "Stop 1", 0, 0, ZoneType.RESIDENTIAL)
        stop2 = Stop("S2", "Stop 2", 0, 0, ZoneType.RESIDENTIAL)
        stop1_clone = Stop("S1", "Stop 1", 0, 0, ZoneType.RESIDENTIAL)
        self.assertTrue(stop1 < stop2)
        self.assertFalse(stop2 < stop1)
        self.assertEqual(stop1, stop1_clone)
        self.assertNotEqual(stop1, stop2)

class TestTransportNetwork(unittest.TestCase):
    def setUp(self):
        self.network = TransportNetwork()
        self.stop1 = Stop("S1", "Stop 1", 1, 1, ZoneType.RESIDENTIAL)
        self.stop2 = Stop("S2", "Stop 2", 2, 2, ZoneType.COMMERCIAL)
        self.stop3 = Stop("S3", "Stop 3", 3, 3, ZoneType.INDUSTRIAL)

    def test_add_stop(self):
        self.network.add_stop(self.stop1)
        self.assertIn(self.stop1, self.network.stops)
        self.assertIn(self.stop1, self.network.routes)

    def test_add_invalid_stop(self):
        with self.assertRaises(TypeError):
            self.network.add_stop("not a stop")

    def test_add_route(self):
        self.network.add_stop(self.stop1)
        self.network.add_stop(self.stop2)
        self.network.add_route(self.stop1, self.stop2, 10)
        self.assertIn((self.stop2, 10), self.network.routes[self.stop1])

    def test_add_route_with_new_stops(self):
        self.network.add_route(self.stop1, self.stop2, 15)
        self.assertIn(self.stop1, self.network.stops)
        self.assertIn(self.stop2, self.network.stops)
        self.assertIn((self.stop2, 15), self.network.routes[self.stop1])

    def test_add_route_invalid_distance(self):
        with self.assertRaises(ValueError):
            self.network.add_route(self.stop1, self.stop2, -5)

if __name__ == '__main__':
    unittest.main() 