import unittest
from project.module.stop import Stop, ZoneType
from project.module.network import TransportNetwork
from project.algorithms.dijkstra import dijkstra
from project.algorithms.dfs import find_all_paths

class TestAlgorithms(unittest.TestCase):
    """Test cases for path finding algorithms"""
    """路径查找算法的测试用例"""
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
        """Test  Dijkstra algorithm functionality"""
        """测试Dijkstra算法功能"""
        path, distance = dijkstra(self.network, self.stop1, self.stop3)
        self.assertEqual([s.name for s in path], ["A", "B", "C"])
        self.assertEqual(distance, 3)

    def test_dijkstra_direct(self):
        """Test Dijkstra algorithm with direct path option"""
        """测试Dijkstra算法的直接路径选项"""
        path, distance = dijkstra(self.network, self.stop1, self.stop3)
        self.assertIn([s.name for s in path], [["A", "B", "C"]])
        self.assertEqual(distance, 3)

    def test_dijkstra_no_path(self):
        """Test Dijkstra algorithm when no path exists"""
        """测试Dijkstra算法在无路径存在时的情况"""
        path, distance = dijkstra(self.network, self.stop1, self.stop5)
        self.assertIsNone(path)
        self.assertEqual(distance, float('inf'))

    def test_dijkstra_same_start_end(self):
        """Test Dijkstra algorithm with same start and end points"""
        """测试Dijkstra算法在起点终点相同时的情况"""
        path, distance = dijkstra(self.network, self.stop1, self.stop1)
        self.assertEqual([s.name for s in path], ["A"])
        self.assertEqual(distance, 0)

    def test_dijkstra_start_not_in_network(self):
        """Test Dijkstra algorithm when start point is not in network"""
        """测试Dijkstra算法在起点不在网络中时的情况"""
        fake_stop = Stop(99, "Z", 0, 0, ZoneType.RESIDENTIAL)
        path, distance = dijkstra(self.network, fake_stop, self.stop1)
        self.assertIsNone(path)
        self.assertEqual(distance, float('inf'))

    def test_dijkstra_end_not_in_network(self):
        """Test Dijkstra algorithm when end point is not in network"""
        """测试Dijkstra算法在终点不在网络中时的情况"""
        fake_stop = Stop(99, "Z", 0, 0, ZoneType.RESIDENTIAL)
        path, distance = dijkstra(self.network, self.stop1, fake_stop)
        self.assertIsNone(path)
        self.assertEqual(distance, float('inf'))

    def test_find_all_paths_basic(self):
        """Test basic functionality of find all paths algorithm"""
        """测试查找所有路径算法的基本功能"""
        paths = find_all_paths(self.network, self.stop1, self.stop3)
        path_names = sorted([tuple(s.name for s in p[0]) for p in paths])
        self.assertIn(("A", "B", "C"), path_names)
        self.assertIn(("A", "C"), path_names)
        distances = [p[1] for p in paths]
        self.assertIn(3, distances)
        self.assertIn(4, distances)

    def test_find_all_paths_no_path(self):
        """Test find all paths when no path exists"""
        """测试查找所有路径在无路径存在时的情况"""
        paths = find_all_paths(self.network, self.stop1, self.stop5)
        self.assertEqual(len(paths), 0)

    def test_find_all_paths_same_start_end(self):
        """Test find all paths with same start and end points"""
        """测试查找所有路径在起点终点相同时的情况"""
        paths = find_all_paths(self.network, self.stop1, self.stop1)
        self.assertEqual(len(paths), 1)
        self.assertEqual([s.name for s in paths[0][0]], ["A"])
        self.assertEqual(paths[0][1], 0)

    def test_find_all_paths_start_not_in_network(self):
        """Test find all paths when start point is not in network"""
        """测试查找所有路径在起点不在网络中时的情况"""
        fake_stop = Stop(99, "Z", 0, 0, ZoneType.RESIDENTIAL)
        paths = find_all_paths(self.network, fake_stop, self.stop1)
        self.assertEqual(paths, [])

    def test_find_all_paths_end_not_in_network(self):
        """Test find all paths when end point is not in network"""
        """测试查找所有路径在终点不在网络中时的情况"""
        fake_stop = Stop(99, "Z", 0, 0, ZoneType.RESIDENTIAL)
        paths = find_all_paths(self.network, self.stop1, fake_stop)
        self.assertEqual(paths, [])

if __name__ == '__main__':
    unittest.main()