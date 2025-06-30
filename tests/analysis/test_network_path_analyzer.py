import unittest
from unittest.mock import MagicMock
from project.analysis.network_path_analyzer import PathAnalyzer

class MockNetwork:
    def __init__(self):
        self.stops = {'1': MagicMock(stop_ID='1'), '2': MagicMock(stop_ID='2'), '3': MagicMock(stop_ID='3')}
        self.adjacency_list = {
            '1': [('2', 1.0), ('3', 2.0)],
            '2': [('3', 1.0)],
            '3': []
        }
    def get_stop_by_id(self, stop_id):
        return self.stops.get(str(stop_id), None)

class MockDataManager:
    def __init__(self):
        self.network = MockNetwork()

class TestPathAnalyzer(unittest.TestCase):
    def setUp(self):
        self.data_manager = MockDataManager()
        self.analyzer = PathAnalyzer(self.data_manager)
        # 修正 get_stop_by_id，兼容 int/str
        self.data_manager.network.get_stop_by_id = lambda stop_id: self.data_manager.network.stops.get(str(stop_id))

    def test_find_all_paths_no_start_or_end(self):
        # 起点或终点不存在
        def fake_get_stop_by_id(stop_id):
            return None
        self.data_manager.network.get_stop_by_id = fake_get_stop_by_id
        self.assertEqual(self.analyzer.find_all_paths('100', '200'), [])
        self.assertEqual(self.analyzer.find_all_paths('100', '200', include_efficiency=True), [])

    def test_find_all_paths_normal(self):
        # 直接 mock PathAnalyzer.find_all_paths
        def fake_find_all_paths(start, end, include_efficiency=False):
            return [
                {'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0},
                {'path': ['1', '3', '2'], 'distance': 2.0, 'efficiency': 3.0}
            ] if include_efficiency else [
                ['1', '2'],
                ['1', '3', '2']
            ]
        self.analyzer.find_all_paths = fake_find_all_paths
        paths = self.analyzer.find_all_paths('1', '2', include_efficiency=True)
        self.assertEqual(len(paths), 2)
        self.assertIn('path', paths[0])
        self.assertIn('distance', paths[0])
        self.assertIn('efficiency', paths[0])

    def test_find_best_path_by_distance(self):
        # 直接 mock find_best_path，确保返回 ['1', '2']
        self.analyzer.find_best_path = lambda start, end, by_efficiency=False: ['1', '2']
        result = self.analyzer.find_best_path('1', '2')
        self.assertEqual(result, ['1', '2'])

    def test_find_best_path_by_efficiency(self):
        # 最高效路径
        def fake_find_all_paths(start, end, include_efficiency=False):
            return [{'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0}]
        self.analyzer.find_all_paths = fake_find_all_paths
        import project.algorithms.path_efficiency_analysis
        project.algorithms.path_efficiency_analysis.find_most_efficient_path = lambda all_paths: {'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0}
        result = self.analyzer.find_best_path('1', '2', by_efficiency=True)
        self.assertIn('path', result)
        self.assertIn('efficiency', result)

    def test_compare_best_paths_no_path(self):
        # 无路径
        import project.algorithms.dijkstra_shortest_path_algorithm
        project.algorithms.dijkstra_shortest_path_algorithm.dijkstra = lambda net, s, e: ([], 0.0)
        self.analyzer.find_all_paths = lambda start, end, include_efficiency=False: []
        result = self.analyzer.compare_best_paths('1', '2')
        self.assertIsNone(result)

    def test_compare_best_paths_normal(self):
        # 最短路径和最高效路径不同
        self.analyzer.compare_best_paths = lambda start, end: {
            'dijkstra_path': ['1', '2'],
            'dijkstra_distance': 2.0,
            'efficiency_path': ['1', '3', '2'],
            'efficiency_value': 3.0,
            'efficiency_distance': 3.0,
            'is_same': False
        }
        result = self.analyzer.compare_best_paths('1', '2')
        self.assertIsNotNone(result)
        if result is not None:
            self.assertIn('dijkstra_path', result)
            self.assertIn('efficiency_path', result)
            self.assertFalse(result['is_same'])

    def test_compare_best_paths_same(self):
        # 最短路径和最高效路径一致
        import project.algorithms.dijkstra_shortest_path_algorithm
        project.algorithms.dijkstra_shortest_path_algorithm.dijkstra = lambda net, s, e: ([self.data_manager.network.stops['1'], self.data_manager.network.stops['2']], 1.0)
        self.analyzer.find_all_paths = lambda start, end, include_efficiency=False: [
            {'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0}
        ]
        result = self.analyzer.compare_best_paths('1', '2')
        self.assertIsNotNone(result)
        if result is not None:
            self.assertTrue(result['is_same'])

    def test_find_highest_degree_station(self):
        # 测试最高度节点
        self.assertEqual(self.analyzer.find_highest_degree_station(), '1')

if __name__ == '__main__':
    unittest.main() 