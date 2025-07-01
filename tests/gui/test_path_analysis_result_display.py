import unittest
from unittest.mock import MagicMock
from project.gui.path_analysis_result_display import PathDisplay

class MockMainWindow:
    def __init__(self):
        self.selected_start = '1'  # type: str | None
        self.selected_end = '2'    # type: str | None
        self.data_manager = MagicMock()
        self.data_manager.stations = {
            '1': {'name': 'A'},
            '2': {'name': 'B'},
            '3': {'name': 'C'}
        }
        self.path_analyzer = MagicMock()
        self.path_info = MagicMock()
        self.show_only_best_path = False
        self.all_paths = []
        self.best_path = []
        self.paths_are_same = False

    def reset(self):
        self.selected_start = '1'
        self.selected_end = '2'
        self.all_paths = []
        self.best_path = []
        self.show_only_best_path = False
        self.path_info = MagicMock()
        self.paths_are_same = False

class TestPathAnalysisResultDisplay(unittest.TestCase):
    def setUp(self):
        self.main_window = MockMainWindow()
        self.display = PathDisplay(self.main_window)

    def test_no_selected_start_or_end(self):
        self.main_window.selected_start = None
        self.display.update_path_info()
        self.main_window.path_info.setText.assert_not_called()
        self.main_window.selected_start = '1'
        self.main_window.selected_end = None
        self.display.update_path_info()
        self.main_window.path_info.setText.assert_not_called()

    def test_no_path_found(self):
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        self.display.update_path_info()
        self.assertIn('No path found', self.main_window.path_info.setText.call_args[0][0])
        self.assertTrue(self.main_window.show_only_best_path)

    def test_paths_found_and_compare(self):
        # 多条路径，最短和最高效不同
        all_paths = [
            {'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0},
            {'path': ['1', '3', '2'], 'distance': 2.0, 'efficiency': 3.0}
        ]
        compare_result = {
            'dijkstra_path': ['1', '2'],
            'dijkstra_distance': 1.0,
            'efficiency_path': ['1', '3', '2'],
            'efficiency_value': 3.0,
            'efficiency_distance': 2.0,
            'is_same': False
        }
        self.main_window.path_analyzer.find_all_paths.return_value = all_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = compare_result
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn('All reachable paths', text)
        self.assertIn('Shortest Path', text)
        self.assertIn('Most Efficient Path', text)
        self.assertIn('A → B', text)
        self.assertIn('A → C → B', text)
        self.assertIn('distance: 1.00km', text)
        self.assertIn('efficiency: 3.00km/h', text)
        self.assertFalse(self.main_window.paths_are_same)

    def test_paths_are_same(self):
        # 最短路径和最高效路径一致
        all_paths = [
            {'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0}
        ]
        compare_result = {
            'dijkstra_path': ['1', '2'],
            'dijkstra_distance': 1.0,
            'efficiency_path': ['1', '2'],
            'efficiency_value': 2.0,
            'efficiency_distance': 1.0,
            'is_same': True
        }
        self.main_window.path_analyzer.find_all_paths.return_value = all_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = compare_result
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn('Shortest Path', text)
        self.assertIn('Most Efficient Path', text)
        self.assertTrue(self.main_window.paths_are_same)

    def test_only_shortest_path(self):
        # 只有最短路径
        all_paths = [
            {'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0}
        ]
        compare_result = {
            'dijkstra_path': ['1', '2'],
            'dijkstra_distance': 1.0,
            'efficiency_path': [],
            'efficiency_value': 0.0,
            'efficiency_distance': 0.0,
            'is_same': False
        }
        self.main_window.path_analyzer.find_all_paths.return_value = all_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = compare_result
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn('Shortest Path', text)
        self.assertNotIn('Most Efficient Path', text)

    def test_only_efficiency_path(self):
        # 只有最高效路径
        all_paths = [
            {'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0}
        ]
        compare_result = {
            'dijkstra_path': [],
            'dijkstra_distance': 0.0,
            'efficiency_path': ['1', '2'],
            'efficiency_value': 2.0,
            'efficiency_distance': 1.0,
            'is_same': False
        }
        self.main_window.path_analyzer.find_all_paths.return_value = all_paths
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = compare_result
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertNotIn('Shortest Path', text)
        self.assertIn('Most Efficient Path', text)

    def test_missing_station_name(self):
        # 站点无 name 字段
        self.main_window.data_manager.stations = {'1': {}, '2': {}}
        all_paths = [
            {'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0}
        ]
        compare_result = {
            'dijkstra_path': ['1', '2'],
            'dijkstra_distance': 1.0,
            'efficiency_path': ['1', '2'],
            'efficiency_value': 2.0,
            'efficiency_distance': 1.0,
            'is_same': True
        }
        self.main_window.path_analyzer.find_all_paths.return_value = all_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = compare_result
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn('FROM 1 TO 2', text)

    def test_compare_result_missing_keys(self):
        # compare_result 缺少部分 key
        all_paths = [
            {'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0}
        ]
        compare_result = {
            'dijkstra_path': ['1', '2'],
            # 缺少 dijkstra_distance
            'efficiency_path': ['1', '2'],
            # 缺少 efficiency_value, efficiency_distance, is_same
        }
        self.main_window.path_analyzer.find_all_paths.return_value = all_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = compare_result
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn('Shortest Path', text)
        self.assertIn('Most Efficient Path', text)

    def test_all_paths_none(self):
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        self.display.update_path_info()
        self.assertIn('No path found', self.main_window.path_info.setText.call_args[0][0])

    def test_path_info_distance_efficiency_edge_cases(self):
        all_paths = [
            {'path': ['1', '2'], 'distance': 0.0, 'efficiency': 0.0},
            {'path': ['1', '3', '2'], 'distance': -1.0, 'efficiency': -2.0},
            {'path': ['1', '2'], 'distance': 1e10, 'efficiency': 1e10}
        ]
        compare_result = {
            'dijkstra_path': ['1', '2'],
            'dijkstra_distance': 0.0,
            'efficiency_path': ['1', '3', '2'],
            'efficiency_value': 0.0,
            'efficiency_distance': -1.0,
            'is_same': False
        }
        self.main_window.path_analyzer.find_all_paths.return_value = all_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = compare_result
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn('All reachable paths', text)

    def test_selected_start_end_special(self):
        self.main_window.selected_start = '@@'
        self.main_window.selected_end = '##'
        self.main_window.data_manager.stations = {}
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn('FROM @@ TO ##', text)

    def test_stations_empty(self):
        self.main_window.data_manager.stations = {}
        all_paths = [
            {'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0}
        ]
        compare_result = {
            'dijkstra_path': ['1', '2'],
            'dijkstra_distance': 1.0,
            'efficiency_path': ['1', '2'],
            'efficiency_value': 2.0,
            'efficiency_distance': 1.0,
            'is_same': True
        }
        self.main_window.path_analyzer.find_all_paths.return_value = all_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = compare_result
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn('FROM 1 TO 2', text)

    def test_path_analyzer_raises_exception(self):
        self.main_window.path_analyzer.find_all_paths.side_effect = Exception('fail')
        try:
            self.display.update_path_info()
        except Exception as e:
            self.assertEqual(str(e), 'fail')

    def test_path_info_setText_raises_exception(self):
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        self.main_window.path_info.setText.side_effect = Exception('fail_setText')
        with self.assertRaises(Exception) as cm:
            self.display.update_path_info()
        self.assertEqual(str(cm.exception), 'fail_setText')

    def test_info_text_very_long(self):
        all_paths = []
        for i in range(100):
            all_paths.append({'path': ['1', '2'], 'distance': 1.0, 'efficiency': 2.0})
        compare_result = {
            'dijkstra_path': ['1', '2'],
            'dijkstra_distance': 1.0,
            'efficiency_path': ['1', '2'],
            'efficiency_value': 2.0,
            'efficiency_distance': 1.0,
            'is_same': True
        }
        self.main_window.path_analyzer.find_all_paths.return_value = all_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = compare_result
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertTrue(len(text) > 1000)

    def test_path_with_duplicate_stations(self):
        all_paths = [
            {'path': ['1', '2', '1', '2'], 'distance': 2.0, 'efficiency': 2.0}
        ]
        compare_result = {
            'dijkstra_path': ['1', '2', '1', '2'],
            'dijkstra_distance': 2.0,
            'efficiency_path': ['1', '2', '1', '2'],
            'efficiency_value': 2.0,
            'efficiency_distance': 2.0,
            'is_same': True
        }
        self.main_window.path_analyzer.find_all_paths.return_value = all_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '2', '1', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = compare_result
        self.display.update_path_info()
        text = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn('A → B → A → B', text)

if __name__ == '__main__':
    unittest.main() 