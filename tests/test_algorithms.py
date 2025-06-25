import unittest
from project.module.stop import Stop
from project.module.network import TransportNetwork
from project.algorithms import dijkstra, find_all_paths

class TestAlgorithms(unittest.TestCase):
    def setUp(self):
        # 创建测试用的站点和网络
        self.stop1 = Stop("A", 0, 0)
        self.stop2 = Stop("B", 1, 1)
        self.stop3 = Stop("C", 2, 2)
        self.stop4 = Stop("D", 3, 3)
        
        # 构建交通网络
        self.network = TransportNetwork()
        self.network.add_stop(self.stop1)
        self.network.add_stop(self.stop2)
        self.network.add_stop(self.stop3)
        self.network.add_stop(self.stop4)
        
        # 添加连接
        self.network.add_connection(self.stop1, self.stop2, 1)
        self.network.add_connection(self.stop2, self.stop3, 2)
        self.network.add_connection(self.stop1, self.stop3, 4)
        self.network.add_connection(self.stop3, self.stop4, 1)

    def test_dijkstra_basic(self):
        # 测试基本路径查找
        path, distance = dijkstra(self.network, self.stop1, self.stop3)
        self.assertEqual(len(path), 3)
        self.assertEqual(distance, 3)
        self.assertEqual(path[0].name, "A")
        self.assertEqual(path[-1].name, "C")

    def test_dijkstra_no_path(self):
        # 测试无路径情况
        isolated_stop = Stop("E", 4, 4)
        path, distance = dijkstra(self.network, self.stop1, isolated_stop)
        self.assertIsNone(path)
        self.assertEqual(distance, float('inf'))

    def test_dijkstra_same_start_end(self):
        # 测试起点终点相同
        path, distance = dijkstra(self.network, self.stop1, self.stop1)
        self.assertEqual(len(path), 1)
        self.assertEqual(distance, 0)

    def test_find_all_paths_basic(self):
        # 测试查找所有路径
        paths = find_all_paths(self.network, self.stop1, self.stop3)
        self.assertEqual(len(paths), 2)  # A->B->C 和 A->C
        # 验证路径距离
        distances = [p[1] for p in paths]
        self.assertIn(3, distances)  # A->B->C
        self.assertIn(4, distances)  # A->C

    def test_find_all_paths_no_path(self):
        # 测试无路径情况
        isolated_stop = Stop("E", 4, 4)
        paths = find_all_paths(self.network, self.stop1, isolated_stop)
        self.assertEqual(len(paths), 0)

if __name__ == '__main__':
    unittest.main()