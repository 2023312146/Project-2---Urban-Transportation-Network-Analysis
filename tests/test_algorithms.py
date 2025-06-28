import unittest
from project.module.stop import Stop, ZoneType
from project.module.network import TransportNetwork
from project.algorithms.dijkstra import dijkstra
from project.algorithms.dfs import find_all_paths

class TestAlgorithms(unittest.TestCase):
    def setUp(self):

        self.stop1 = Stop(1, "A", 0, 0, ZoneType.RESIDENTIAL)
        self.stop2 = Stop(2, "B", 1, 1, ZoneType.COMMERCIAL)
        self.stop3 = Stop(3, "C", 2, 2, ZoneType.INDUSTRIAL)
        self.stop4 = Stop(4, "D", 3, 3, ZoneType.MIXED)
        self.stop5 = Stop(5, "E", 4, 4, ZoneType.URBAN)  
        self.network = TransportNetwork()
        for stop in [self.stop1, self.stop2, self.stop3, self.stop4, self.stop5]:
            self.network.add_stop(stop)
        self.network.add_route(self.stop1, self.stop2, 1)
        self.network.add_route(self.stop2, self.stop3, 2)
        self.network.add_route(self.stop1, self.stop3, 4)
        self.network.add_route(self.stop3, self.stop4, 1)

    def test_dijkstra_basic(self):
        # 路径A->B->C
        path, distance = dijkstra(self.network, self.stop1, self.stop3)
        self.assertEqual([s.name for s in path], ["A", "B", "C"])
        self.assertEqual(distance, 3)

    def test_dijkstra_direct(self):
        # 路径A->C（直接）
        path, distance = dijkstra(self.network, self.stop1, self.stop3)
        self.assertIn([s.name for s in path], [["A", "B", "C"]])  # 最短路径
        self.assertEqual(distance, 3)

    def test_dijkstra_no_path(self):
        # 到孤立点
        path, distance = dijkstra(self.network, self.stop1, self.stop5)
        self.assertIsNone(path)
        self.assertEqual(distance, float('inf'))

    def test_dijkstra_same_start_end(self):
        # 起点终点相同
        path, distance = dijkstra(self.network, self.stop1, self.stop1)
        self.assertEqual([s.name for s in path], ["A"])
        self.assertEqual(distance, 0)

    def test_dijkstra_start_not_in_network(self):
        # 起点不在网络
        fake_stop = Stop(99, "Z", 0, 0, ZoneType.RESIDENTIAL)
        path, distance = dijkstra(self.network, fake_stop, self.stop1)
        self.assertIsNone(path)
        self.assertEqual(distance, float('inf'))

    def test_dijkstra_end_not_in_network(self):
        # 终点不在网络
        fake_stop = Stop(99, "Z", 0, 0, ZoneType.RESIDENTIAL)
        path, distance = dijkstra(self.network, self.stop1, fake_stop)
        self.assertIsNone(path)
        self.assertEqual(distance, float('inf'))

    def test_find_all_paths_basic(self):
        # A->B->C 和 A->C
        paths = find_all_paths(self.network, self.stop1, self.stop3)
        path_names = sorted([tuple(s.name for s in p[0]) for p in paths])
        self.assertIn(("A", "B", "C"), path_names)
        self.assertIn(("A", "C"), path_names)
        distances = [p[1] for p in paths]
        self.assertIn(3, distances)
        self.assertIn(4, distances)

    def test_find_all_paths_no_path(self):
        # 到孤立点
        paths = find_all_paths(self.network, self.stop1, self.stop5)
        self.assertEqual(len(paths), 0)

    def test_find_all_paths_same_start_end(self):
        # 起点终点相同
        paths = find_all_paths(self.network, self.stop1, self.stop1)
        self.assertEqual(len(paths), 1)
        self.assertEqual([s.name for s in paths[0][0]], ["A"])
        self.assertEqual(paths[0][1], 0)

    def test_find_all_paths_start_not_in_network(self):
        # 起点不在网络
        fake_stop = Stop(99, "Z", 0, 0, ZoneType.RESIDENTIAL)
        paths = find_all_paths(self.network, fake_stop, self.stop1)
        self.assertEqual(paths, [])

    def test_find_all_paths_end_not_in_network(self):
        # 终点不在网络
        fake_stop = Stop(99, "Z", 0, 0, ZoneType.RESIDENTIAL)
        paths = find_all_paths(self.network, self.stop1, fake_stop)
        self.assertEqual(paths, [])

if __name__ == '__main__':
    unittest.main()