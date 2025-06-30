import unittest
from project.algorithms import path_efficiency_analysis

class DummyStop:
    def __init__(self, stop_ID, zone_type='default'):
        self.stop_ID = stop_ID
        self.zone_type = zone_type

class TestPathEfficiencyAnalysis(unittest.TestCase):
    def test_efficiency_normal(self):
        stops = [DummyStop('A', 'A'), DummyStop('B', 'B'), DummyStop('C', 'A')]
        wait_times = {'A': 2, 'B': 3}
        eff = path_efficiency_analysis.calculate_efficiency(stops, 10, wait_times, speed=20)
        self.assertGreater(eff, 0)

    def test_efficiency_single_stop(self):
        stops = [DummyStop('A')]
        wait_times = {'A': 2}
        eff = path_efficiency_analysis.calculate_efficiency(stops, 10, wait_times)
        self.assertEqual(eff, 0.0)

    def test_efficiency_empty(self):
        stops = []
        wait_times = {}
        eff = path_efficiency_analysis.calculate_efficiency(stops, 10, wait_times)
        self.assertEqual(eff, 0.0)

    def test_efficiency_zero_distance(self):
        stops = [DummyStop('A'), DummyStop('B')]
        wait_times = {'A': 2, 'B': 3}
        eff = path_efficiency_analysis.calculate_efficiency(stops, 0, wait_times)
        self.assertEqual(eff, 0.0)

    def test_efficiency_missing_wait_time(self):
        stops = [DummyStop('A'), DummyStop('B')]
        wait_times = {}  # 使用預設值
        eff = path_efficiency_analysis.calculate_efficiency(stops, 10, wait_times)
        self.assertGreater(eff, 0)

    def test_find_most_efficient_path(self):
        all_paths = [
            {'path': ['A', 'B'], 'distance': 10, 'efficiency': 1.0},
            {'path': ['A', 'C'], 'distance': 8, 'efficiency': 2.0}
        ]
        result = path_efficiency_analysis.find_most_efficient_path(all_paths)
        self.assertEqual(result['path'], ['A', 'C'])

    def test_find_most_efficient_path_empty(self):
        result = path_efficiency_analysis.find_most_efficient_path([])
        self.assertEqual(result, {})

    def test_compare_paths_by_efficiency_and_distance(self):
        dijkstra_path_stops = [DummyStop('A'), DummyStop('B')]
        dijkstra_distance = 10
        all_paths = [
            {'path': ['A', 'B'], 'distance': 10, 'efficiency': 1.0},
            {'path': ['A', 'C'], 'distance': 8, 'efficiency': 2.0}
        ]
        result = path_efficiency_analysis.compare_paths_by_efficiency_and_distance(
            dijkstra_path_stops, dijkstra_distance, all_paths)
        self.assertEqual(result['dijkstra_path'], ['A', 'B'])
        self.assertEqual(result['dijkstra_distance'], 10)
        self.assertEqual(result['efficiency_path'], ['A', 'C'])
        self.assertEqual(result['efficiency_value'], 2.0)
        self.assertEqual(result['efficiency_distance'], 8)
        self.assertFalse(result['is_same'])

    def test_compare_paths_empty(self):
        result = path_efficiency_analysis.compare_paths_by_efficiency_and_distance([], 0, [])
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main() 