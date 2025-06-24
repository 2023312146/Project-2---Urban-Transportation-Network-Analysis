import unittest
from project.module.network import TransportNetwork
from project.algorithms import dijkstra, find_all_paths

class TestAlgorithms(unittest.TestCase):

    def setUp(self):
        self.network = TransportNetwork()
        self.network.add_route(1, 2, 7)
        self.network.add_route(1, 3, 9)
        self.network.add_route(1, 6, 14)
        self.network.add_route(2, 3, 10)
        self.network.add_route(2, 4, 15)
        self.network.add_route(3, 4, 11)
        self.network.add_route(3, 6, 2)
        self.network.add_route(4, 5, 6)
        self.network.add_route(5, 6, 9)

    def test_dijkstra(self):
        path, distance = dijkstra(self.network, 1, 5)
        self.assertEqual(distance, 26)
        self.assertEqual(path, [1, 3, 4, 5])

    def test_dijkstra_no_path(self):
        path, distance = dijkstra(self.network, 1, 7)
        self.assertIsNone(path)
        self.assertEqual(distance, float('inf'))

    def test_find_all_paths(self):
        # A smaller network for simplicity
        net = TransportNetwork()
        net.add_route(1, 2, 1)
        net.add_route(1, 3, 1)
        net.add_route(2, 4, 1)
        net.add_route(3, 4, 1)
        paths = find_all_paths(net, 1, 4)
        self.assertEqual(len(paths), 2)
        # Check if paths are correct, regardless of order
        path_tuples = [tuple(p[0]) for p in paths]
        self.assertIn((1, 2, 4), path_tuples)
        self.assertIn((1, 3, 4), path_tuples)

if __name__ == '__main__':
    unittest.main() 