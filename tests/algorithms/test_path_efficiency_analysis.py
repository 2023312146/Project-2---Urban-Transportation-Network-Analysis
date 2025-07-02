import unittest
from project.algorithms import path_efficiency_analysis
from unittest.mock import MagicMock

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

    def test_efficiency_total_time_zero(self):
        stops = [DummyStop('A'), DummyStop('B')]
        wait_times = {'A': 0, 'B': 0}
        # speed=0 會導致 travel_time 無窮大，這裡直接設置 speed=0
        eff = path_efficiency_analysis.calculate_efficiency(stops, 10, wait_times, speed=0)
        self.assertEqual(eff, 0.0)
        # total_distance=0 也會導致 total_time=0
        eff2 = path_efficiency_analysis.calculate_efficiency(stops, 0, wait_times, speed=23)
        self.assertEqual(eff2, 0.0)

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

    def test_efficiency_with_traffic_manager(self):
        stops = [DummyStop('A', MagicMock(value='A')), DummyStop('B', MagicMock(value='B')), DummyStop('C', MagicMock(value='A'))]
        wait_times = {'A': 2, 'B': 3}
        traffic_manager = MagicMock()
        # 模擬 get_wait_time
        traffic_manager.get_wait_time.side_effect = lambda z: 5 if z == 'a' else 7
        # 模擬 get_speed
        traffic_manager.get_speed.side_effect = lambda z: 10 if z == 'a' else 20
        traffic_manager.base_speed = 23
        eff = path_efficiency_analysis.calculate_efficiency(stops, 10, wait_times, speed=20, traffic_manager=traffic_manager)
        self.assertGreater(eff, 0)
        self.assertEqual(traffic_manager.get_wait_time.call_count, 2)
        self.assertEqual(traffic_manager.get_speed.call_count, 2)

    def test_efficiency_with_traffic_manager_single_section(self):
        stops = [DummyStop('A', MagicMock(value='A')), DummyStop('B', MagicMock(value='B'))]
        wait_times = {'A': 2, 'B': 3}
        traffic_manager = MagicMock()
        traffic_manager.get_wait_time.return_value = 5
        traffic_manager.get_speed.return_value = 10
        traffic_manager.base_speed = 23
        eff = path_efficiency_analysis.calculate_efficiency(stops, 10, wait_times, speed=20, traffic_manager=traffic_manager)
        self.assertGreater(eff, 0)
        self.assertEqual(traffic_manager.get_wait_time.call_count, 1)
        self.assertEqual(traffic_manager.get_speed.call_count, 1)

    def test_efficiency_with_traffic_manager_no_sections(self):
        stops = [DummyStop('A', MagicMock(value='A'))]
        wait_times = {'A': 2}
        traffic_manager = MagicMock()
        traffic_manager.get_wait_time.return_value = 5
        traffic_manager.get_speed.return_value = 10
        traffic_manager.base_speed = 42
        eff = path_efficiency_analysis.calculate_efficiency(stops, 10, wait_times, speed=20, traffic_manager=traffic_manager)
        self.assertEqual(eff, 0.0)
        # base_speed 應該被用到
        self.assertEqual(traffic_manager.base_speed, 42)

if __name__ == '__main__':
    unittest.main() 