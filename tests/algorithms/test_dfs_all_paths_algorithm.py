import unittest
from project.algorithms import dfs_all_paths_algorithm
from project.data_structures.transport_network_structure import TransportNetwork

class DummyTransportNetwork(TransportNetwork):
    def __init__(self, adjacency_list, stops):
        self.adjacency_list = adjacency_list
        self._stops = stops
    def get_stop_by_id(self, stop_id):
        return self._stops.get(stop_id, type('Stop', (), {'stop_ID': stop_id})())

class TestDFSAllPathsAlgorithm(unittest.TestCase):
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

    def test_single_path(self):
        paths = dfs_all_paths_algorithm.find_all_paths(self.network, 'A', 'C')
        self.assertEqual(len(paths), 1)
        self.assertEqual([s.stop_ID for s in paths[0][0]], ['A', 'B', 'C'])
        self.assertEqual(paths[0][1], 2)

    def test_no_path(self):
        paths = dfs_all_paths_algorithm.find_all_paths(self.network, 'C', 'A')
        self.assertEqual(paths, [])

    def test_start_equals_end(self):
        paths = dfs_all_paths_algorithm.find_all_paths(self.network, 'A', 'A')
        self.assertEqual(len(paths), 1)
        self.assertEqual([s.stop_ID for s in paths[0][0]], ['A'])
        self.assertEqual(paths[0][1], 0)

    def test_multiple_paths(self):
        # A --1--> B --1--> C
        #  \------2------/
        network = DummyTransportNetwork(
            adjacency_list={
                'A': [('B', 1), ('C', 2)],
                'B': [('C', 1)],
                'C': []
            },
            stops=self.network._stops
        )
        paths = dfs_all_paths_algorithm.find_all_paths(network, 'A', 'C')
        all_paths = sorted([[s.stop_ID for s in p[0]] for p in paths])
        self.assertIn(['A', 'B', 'C'], all_paths)
        self.assertIn(['A', 'C'], all_paths)
        self.assertEqual(len(paths), 2)

    def test_invalid_start(self):
        paths = dfs_all_paths_algorithm.find_all_paths(self.network, 'X', 'C')
        self.assertEqual(paths, [])

if __name__ == '__main__':
    unittest.main() 