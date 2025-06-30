import unittest
from project.algorithms import dijkstra_shortest_path_algorithm
from project.data_structures.transport_network_structure import TransportNetwork

class DummyTransportNetwork(TransportNetwork):
    def __init__(self, adjacency_list, stops):
        self.adjacency_list = adjacency_list
        self._stops = stops
    def get_stop_by_id(self, stop_id):
        if stop_id in self._stops:
            return self._stops[stop_id]
        # 始终返回带 stop_ID 属性的对象，避免 None
        return type('Stop', (), {'stop_ID': stop_id})()

class TestDijkstraShortestPathAlgorithm(unittest.TestCase):
    def setUp(self):
        # A --1--> B --1--> C
        self.network = DummyTransportNetwork(
            adjacency_list={
                'A': [('B', 1)],
                'B': [('C', 1)],
                'C': []
            },
            stops={
                'A': type('Stop', (), {'stop_ID': 'A'})(),
                'B': type('Stop', (), {'stop_ID': 'B'})(),
                'C': type('Stop', (), {'stop_ID': 'C'})()
            }
        )

    def test_shortest_path(self):
        path, dist = dijkstra_shortest_path_algorithm.dijkstra(self.network, 'A', 'C')
        self.assertIsNotNone(path)
        self.assertEqual([s.stop_ID for s in path], ['A', 'B', 'C'])
        self.assertEqual(dist, 2)

    def test_no_path(self):
        path, dist = dijkstra_shortest_path_algorithm.dijkstra(self.network, 'C', 'A')
        self.assertIsNone(path)
        self.assertEqual(dist, float('inf'))

    def test_start_equals_end(self):
        path, dist = dijkstra_shortest_path_algorithm.dijkstra(self.network, 'A', 'A')
        self.assertIsNotNone(path)
        self.assertEqual([s.stop_ID for s in path], ['A'])
        self.assertEqual(dist, 0)

    def test_invalid_start(self):
        path, dist = dijkstra_shortest_path_algorithm.dijkstra(self.network, 'X', 'C')
        self.assertIsNone(path)
        self.assertEqual(dist, float('inf'))

    def test_invalid_end(self):
        path, dist = dijkstra_shortest_path_algorithm.dijkstra(self.network, 'A', 'X')
        self.assertIsNone(path)
        self.assertEqual(dist, float('inf'))

    def test_multiple_paths(self):
        # A --1--> B --1--> C
        #  \------2------/
        network = DummyTransportNetwork(
            adjacency_list={
                'A': [('B', 1), ('C', 2)],
                'B': [('C', 1)],
                'C': []
            },
            stops={
                'A': type('Stop', (), {'stop_ID': 'A'})(),
                'B': type('Stop', (), {'stop_ID': 'B'})(),
                'C': type('Stop', (), {'stop_ID': 'C'})()
            }
        )
        path, dist = dijkstra_shortest_path_algorithm.dijkstra(network, 'A', 'C')
        self.assertIsNotNone(path)
        # 允许 ['A', 'C'] 或 ['A', 'B', 'C'] 都通过
        self.assertIn([s.stop_ID for s in path], [['A', 'B', 'C'], ['A', 'C']])
        self.assertEqual(dist, 2)

if __name__ == '__main__':
    unittest.main() 