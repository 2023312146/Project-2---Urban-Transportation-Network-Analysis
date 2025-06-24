import unittest
from ..module.network import TransportNetwork  # 修改导入路径
from ..module.stop import Stop, ZoneType  # 修改导入路径

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