# tests/test_DJ.py

import unittest
from project_name.DJ import TransportNetwork

class TestTransportNetwork(unittest.TestCase):
    def setUp(self):
        self.network = TransportNetwork()
        for stop_id in [1, 2, 3]:
            self.network.add_stop(stop_id)
        self.network.add_route(1, 2, 5)
        self.network.add_route(2, 3, 10)
        self.network.add_route(1, 3, 20)

    def test_add_stop(self):
        self.network.add_stop(4)
        self.assertIn(4, self.network.stops)

    def test_add_route(self):
        self.network.add_route(3, 1, 15)
        self.assertIn((1, 15), self.network.routes[3])

    def test_dijkstra(self):
        path, distance = self.network.dijkstra(1, 3)
        self.assertEqual(path, [1, 2, 3])
        self.assertEqual(distance, 15)
        path2, distance2 = self.network.dijkstra(1, 2)
        self.assertEqual(path2, [1, 2])
        self.assertEqual(distance2, 5)

if __name__ == '__main__':
    unittest.main()
