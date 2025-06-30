import unittest
from project.algorithms import distance_calculation

class DummyDataManager:
    def __init__(self, stations):
        self.stations = stations

class TestDistanceCalculation(unittest.TestCase):
    def test_haversine_distance_basic(self):
        # 北京到上海
        dist = distance_calculation.calculate_haversine_distance(39.9042, 116.4074, 31.2304, 121.4737)
        self.assertAlmostEqual(dist, 1068, delta=5)

    def test_haversine_distance_same_point(self):
        dist = distance_calculation.calculate_haversine_distance(0, 0, 0, 0)
        self.assertEqual(dist, 0)

    def test_distance_between_stops(self):
        stop1 = {'lat': 39.9, 'lon': 116.4}
        stop2 = {'lat': 31.2, 'lon': 121.4}
        dist = distance_calculation.calculate_distance_between_stops(stop1, stop2)
        self.assertGreater(dist, 0)

    def test_distance_between_stops_missing_key(self):
        stop1 = {'lat': 39.9}
        stop2 = {'lat': 31.2, 'lon': 121.4}
        with self.assertRaises(KeyError):
            distance_calculation.calculate_distance_between_stops(stop1, stop2)

    def test_distance_between_stops_by_id_normal(self):
        stations = {
            'A': {'lat': 39.9, 'lon': 116.4},
            'B': {'lat': 31.2, 'lon': 121.4}
        }
        dm = DummyDataManager(stations)
        dist = distance_calculation.calculate_distance_between_stops_by_id(dm, 'A', 'B')
        self.assertGreater(dist, 0)

    def test_distance_between_stops_by_id_missing(self):
        stations = {'A': {'lat': 39.9, 'lon': 116.4}}
        dm = DummyDataManager(stations)
        dist = distance_calculation.calculate_distance_between_stops_by_id(dm, 'A', 'B')
        self.assertEqual(dist, 0)

if __name__ == '__main__':
    unittest.main() 