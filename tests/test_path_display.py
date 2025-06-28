import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt
from project.module.path_display import PathDisplay
from typing import Optional


"""Dummy main window class for testing path display functionality"""
"""用于测试路径显示功能的虚拟主窗口类"""

class DummyMainWindow:
    def __init__(self):
        self.selected_start: Optional[str] = None
        self.selected_end: Optional[str] = None
        self.all_paths = []
        self.best_path = []
        self.show_only_best_path = False
        self.data_manager = MagicMock()
        self.path_analyzer = MagicMock()
        self.path_info = MagicMock()
        self.shortest_path = []
        self.efficiency_path = []
        self.shortest_distance = 0.0
        self.efficiency_distance = 0.0
        self.efficiency_value = 0.0
        self.paths_are_same = False


"""Test class for PathDisplay functionality"""
""" 路径显示功能测试类"""

class TestPathDisplay(unittest.TestCase):
    def setUp(self):
        self.main_window = DummyMainWindow()
        self.display = PathDisplay(self.main_window)

    """
    Test PathDisplay initialization
    测试路径显示初始化
    """
    def test_init(self):
        self.assertIs(self.display.main_window, self.main_window)
        self.assertIs(self.display.data_manager, self.main_window.data_manager)
        self.assertIs(self.display.path_analyzer, self.main_window.path_analyzer)

    """
    Test path info update when no start or end station is selected
    测试未选择起始或终点站点时的路径信息更新
    """
    def test_update_path_info_no_selection(self):
        self.main_window.selected_start = None
        self.main_window.selected_end = None
        self.display.update_path_info()
        self.main_window.path_analyzer.find_all_paths.assert_not_called()
        self.main_window.path_analyzer.find_best_path.assert_not_called()

    """
    Test path info update when no paths are found
    测试找不到路径时的路径信息更新
    """
    def test_update_path_info_no_paths_found(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'}
        }
        
        self.display.update_path_info()
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("No path found", call_args)
        self.assertIn("FROM Station A TO Station B", call_args)

    """
    Test path info update when paths are found
    测试找到路径时的路径信息更新
    """
    def test_update_path_info_with_paths(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        mock_paths = [
            {
                'path': ['1', '3', '2'],
                'distance': 15.5,
                'efficiency': 25.3
            },
            {
                'path': ['1', '4', '2'],
                'distance': 18.2,
                'efficiency': 22.1
            }
        ]
        self.main_window.path_analyzer.find_all_paths.return_value = mock_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '3', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
      
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'},
            '3': {'name': 'Station C'},
            '4': {'name': 'Station D'}
        }
        
        self.display.update_path_info()
        
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("Station A → Station C → Station B", call_args)
        self.assertIn("Station A → Station D → Station B", call_args)
        self.assertIn("15.50km", call_args)
        self.assertIn("25.30km/h", call_args)
        self.assertIn("18.20km", call_args)
        self.assertIn("22.10km/h", call_args)

    """
    Test best path comparison functionality
    测试最佳路径比较功能
    """
    def test_update_path_info_with_best_path_comparison(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        mock_paths = [
            {
                'path': ['1', '3', '2'],
                'distance': 12.5,
                'efficiency': 28.2
            }
        ]
        self.main_window.path_analyzer.find_all_paths.return_value = mock_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '3', '2']
        mock_compare_result = {
            'dijkstra_path': ['1', '3', '2'],
            'dijkstra_distance': 12.5,
            'efficiency_path': ['1', '4', '2'],
            'efficiency_distance': 18.0,
            'efficiency_value': 30.5,
            'is_same': False
        }
        self.main_window.path_analyzer.compare_best_paths.return_value = mock_compare_result
        self.main_window.path_analyzer._calculate_efficiency.return_value = 28.2
        
        """
        Mock station data
        模拟站点数据
        """
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'},
            '3': {'name': 'Station C'},
            '4': {'name': 'Station D'}
        }
        
        self.display.update_path_info()
        
        """
        Verify best path information is displayed
        验证最佳路径信息被显示
        """
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("Shortest Path (Red)", call_args)
        self.assertIn("Most Efficient Path (Green)", call_args)
        self.assertIn("Station A → Station C → Station B", call_args)
        self.assertIn("Station A → Station D → Station B", call_args)
        self.assertIn("12.50km", call_args)
        self.assertIn("18.00km", call_args)
        self.assertIn("28.20km/h", call_args)
        self.assertIn("30.50km/h", call_args)

    """
    Test path info update without comparison result
    测试没有比较结果时的路径信息更新
    """
    def test_update_path_info_without_compare_result(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        
        """
        Mock path data
        模拟路径数据
        """
        mock_paths = [
            {
                'path': ['1', '3', '2'],
                'distance': 15.5,
                'efficiency': 25.3
            }
        ]
        self.main_window.path_analyzer.find_all_paths.return_value = mock_paths
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        """
        Mock station data
        模拟站点数据
        """
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'},
            '3': {'name': 'Station C'}
        }
        
        self.display.update_path_info()
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("Station A → Station C → Station B", call_args)
        self.assertNotIn("Recommended Path", call_args)

    """
    Test station name resolution
    测试站点名称解析
    """
    def test_station_name_resolution(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
        }
        
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        self.display.update_path_info()
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("FROM Station A TO 2", call_args)

    """
    Test station name resolution in paths
    测试路径中站点名称解析
    """
    def test_station_name_resolution_in_paths(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        
        mock_paths = [
            {
                'path': ['1', '3', '2'],
                'distance': 15.5,
                'efficiency': 25.3
            }
        ]
        self.main_window.path_analyzer.find_all_paths.return_value = mock_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '3', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '3': {'name': 'Station C'},
            
        }
        
        self.display.update_path_info()
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("Station A → Station C → 2", call_args)

    """
    Test text format setting
    测试文本格式设置
    """
    def test_text_format_setting(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        self.display.update_path_info()
        
       
        self.main_window.path_info.setTextFormat.assert_called_with(Qt.TextFormat.RichText)

    """
    Test state updates
    测试状态更新
    """
    def test_state_updates(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        self.display.update_path_info()
        self.assertTrue(self.main_window.show_only_best_path)
        self.assertEqual(self.main_window.all_paths, [])
        self.assertEqual(self.main_window.best_path, [])

  
    def test_path_analyzer_calls(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        self.display.update_path_info()
        self.main_window.path_analyzer.find_all_paths.assert_called_with(
            '1', '2', include_efficiency=True
        )
        self.main_window.path_analyzer.find_best_path.assert_called_with('1', '2')

    """
    Test efficiency calculation call
    测试效率计算调用
    """
    def test_efficiency_calculation_call(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        
        mock_paths = [
            {
                'path': ['1', '3', '2'],
                'distance': 15.5,
                'efficiency': 25.3
            }
        ]
        self.main_window.path_analyzer.find_all_paths.return_value = mock_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '3', '2']
        
        mock_compare_result = {
            'dijkstra_path': ['1', '3', '2'],
            'dijkstra_distance': 12.5,
            'efficiency_path': ['1', '4', '2'],
            'efficiency_distance': 18.0,
            'efficiency_value': 30.5,
            'is_same': False
        }
        self.main_window.path_analyzer.compare_best_paths.return_value = mock_compare_result
        self.main_window.path_analyzer._calculate_efficiency.return_value = 28.2
        
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'},
            '3': {'name': 'Station C'},
            '4': {'name': 'Station D'}
        }
        
        self.display.update_path_info()
       

    """
    Test empty path info handling
    测试空路径信息处理
    """
    def test_empty_path_info(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'}
        }
        
        self.display.update_path_info()
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("FROM Station A TO Station B", call_args)
        self.assertIn("No path found", call_args)

    """
    Test multiple paths display
    测试多条路径的显示
    """
    def test_multiple_paths_display(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        
        mock_paths = [
            {
                'path': ['1', '3', '2'],
                'distance': 15.5,
                'efficiency': 25.3
            },
            {
                'path': ['1', '4', '2'],
                'distance': 18.2,
                'efficiency': 22.1
            },
            {
                'path': ['1', '5', '2'],
                'distance': 20.0,
                'efficiency': 19.8
            }
        ]
        self.main_window.path_analyzer.find_all_paths.return_value = mock_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '3', '2']
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'},
            '3': {'name': 'Station C'},
            '4': {'name': 'Station D'},
            '5': {'name': 'Station E'}
        }
        
        self.display.update_path_info()
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("Station A → Station C → Station B", call_args)
        self.assertIn("Station A → Station D → Station B", call_args)
        self.assertIn("Station A → Station E → Station B", call_args)
        self.assertEqual(call_args.count("-----------"), 4)

if __name__ == '__main__':
    unittest.main() 