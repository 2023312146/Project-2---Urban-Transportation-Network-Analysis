import unittest
from unittest.mock import MagicMock
import math
from project.analysis.stop_utilization_analyzer import StopUtilizationAnalyzer
from project.data_structures.stop_entity import Stop, ZoneType

class MockNetwork:
    def __init__(self):
        # 建立三個站點，分屬不同區域
        self.stops = {
            1: Stop(1, 'A', 30.0, 120.0, ZoneType.RESIDENTIAL),
            2: Stop(2, 'B', 30.01, 120.01, ZoneType.COMMERCIAL),
            3: Stop(3, 'C', 30.02, 120.02, ZoneType.INDUSTRIAL),
            4: Stop(4, 'D', 30.10, 120.10, ZoneType.MIXED),
        }
        self.adjacency_list = {
            1: [(2, 1.5), (3, 2.5)],
            2: [(3, 1.0), (4, 5.0)],
            3: [(4, 2.0)],
            4: []
        }
    def get_stop_by_id(self, stop_id):
        return self.stops.get(stop_id)

class MockDataManager:
    def __init__(self):
        self.network = MockNetwork()

class TestStopUtilizationAnalyzer(unittest.TestCase):
    def setUp(self):
        self.data_manager = MockDataManager()
        self.analyzer = StopUtilizationAnalyzer(self.data_manager)

    def test_generate_random_data(self):
        self.analyzer.generate_random_data()
        self.assertEqual(len(self.analyzer.passenger_volume), 4)
        self.assertEqual(len(self.analyzer.arrival_frequency), 4)
        # 數值範圍
        for v in self.analyzer.passenger_volume.values():
            self.assertTrue(200 <= v <= 2000)
        for f in self.analyzer.arrival_frequency.values():
            self.assertTrue(2 <= f <= 12)

    def test_calculate_stop_efficiency_with_manual_data(self):
        # 手動設置數據
        self.analyzer.set_passenger_data({1: 1000, 2: 500, 3: 200, 4: 800})
        self.analyzer.set_arrival_frequency({1: 10, 2: 5, 3: 2, 4: 8})
        result = self.analyzer.calculate_stop_efficiency()
        self.assertEqual(len(result), 4)
        # 應有排序
        scores = [x[1] for x in result]
        self.assertTrue(all(scores[i] >= scores[i+1] for i in range(len(scores)-1)))

    def test_calculate_stop_efficiency_missing_data(self):
        # 缺少部分數據，應用默認值
        self.analyzer.set_passenger_data({1: 1000})
        self.analyzer.set_arrival_frequency({2: 5})
        result = self.analyzer.calculate_stop_efficiency()
        self.assertEqual(len(result), 4)
        # 不會報錯

    def test_identify_underutilized_stops(self):
        self.analyzer.generate_random_data()
        under = self.analyzer.identify_underutilized_stops(threshold=0.5)
        # 返回為列表，內容為字典
        self.assertIsInstance(under, list)
        if under:
            self.assertIn('stop_id', under[0])
            self.assertIn('score', under[0])

    def test_find_stops_for_consolidation(self):
        self.analyzer.generate_random_data()
        self.analyzer.calculate_stop_efficiency()
        pairs = self.analyzer.find_stops_for_consolidation(max_distance=20.0)
        self.assertIsInstance(pairs, list)
        if pairs:
            self.assertIn('keep_stop', pairs[0])
            self.assertIn('remove_stop', pairs[0])
            self.assertLessEqual(pairs[0]['distance'], 20.0)

    def test_suggest_new_stops(self):
        self.analyzer.generate_random_data()
        self.analyzer.calculate_stop_efficiency()
        suggestions = self.analyzer.suggest_new_stops(num_suggestions=2)
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 2)
        if suggestions:
            self.assertIn('latitude', suggestions[0])
            self.assertIn('longitude', suggestions[0])

    def test_optimize_network(self):
        self.analyzer.generate_random_data()
        self.analyzer.calculate_stop_efficiency()
        result = self.analyzer.optimize_network()
        self.assertIn('underutilized_stops', result)
        self.assertIn('consolidation_candidates', result)
        self.assertIn('new_stop_suggestions', result)

    def test_empty_network(self):
        # 無站點
        self.analyzer.data_manager.network.stops = {}
        self.analyzer.data_manager.network.adjacency_list = {}
        self.analyzer.generate_random_data()
        eff = self.analyzer.calculate_stop_efficiency()
        self.assertEqual(eff, [])
        under = self.analyzer.identify_underutilized_stops()
        self.assertEqual(under, [])
        pairs = self.analyzer.find_stops_for_consolidation()
        self.assertEqual(pairs, [])
        sugg = self.analyzer.suggest_new_stops()
        self.assertEqual(sugg, [])

    def test_extreme_values(self):
        # 乘客量極大/極小，頻率極大/極小
        self.analyzer.set_passenger_data({1: 0, 2: 99999, 3: 1, 4: 500})
        self.analyzer.set_arrival_frequency({1: 1, 2: 100, 3: 1, 4: 1})
        result = self.analyzer.calculate_stop_efficiency()
        self.assertEqual(len(result), 4)

    def test_private_calculate_distance(self):
        # 驗證距離計算
        d = self.analyzer._calculate_distance(30, 120, 30, 120)
        self.assertAlmostEqual(d, 0.0, places=2)
        d2 = self.analyzer._calculate_distance(30, 120, 31, 121)
        self.assertGreater(d2, 0)

    def test_private_is_location_safe_for_new_stop(self):
        # 距離足夠遠
        safe = self.analyzer._is_location_safe_for_new_stop(50, 50, 1.0)
        self.assertTrue(safe)
        # 距離很近
        safe2 = self.analyzer._is_location_safe_for_new_stop(30.0, 120.0, 100)
        self.assertFalse(safe2)

if __name__ == '__main__':
    unittest.main() 