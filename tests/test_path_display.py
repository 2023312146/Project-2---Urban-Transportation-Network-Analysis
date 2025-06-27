import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt
from project.module.path_display import PathDisplay

class DummyMainWindow:
    def __init__(self):
        self.selected_start = None
        self.selected_end = None
        self.all_paths = []
        self.best_path = []
        self.show_only_best_path = False
        self.data_manager = MagicMock()
        self.path_analyzer = MagicMock()
        self.path_info = MagicMock()

class TestPathDisplay(unittest.TestCase):
    def setUp(self):
        self.main_window = DummyMainWindow()
        self.display = PathDisplay(self.main_window)

    def test_init(self):
        self.assertIs(self.display.main_window, self.main_window)
        self.assertIs(self.display.data_manager, self.main_window.data_manager)
        self.assertIs(self.display.path_analyzer, self.main_window.path_analyzer)

    def test_update_path_info_no_selection(self):
        # 测试没有选择起始或终点站点的情况
        self.main_window.selected_start = None
        self.main_window.selected_end = None
        self.display.update_path_info()
        # 验证方法正常返回，不执行路径查找
        self.main_window.path_analyzer.find_all_paths.assert_not_called()
        self.main_window.path_analyzer.find_best_path.assert_not_called()

    def test_update_path_info_no_paths_found(self):
        # 测试找不到路径的情况
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        
        # 模拟站点数据
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'}
        }
        
        self.display.update_path_info()
        
        # 验证显示"No path found"
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("No path found", call_args)
        self.assertIn("FROM Station A TO Station B", call_args)

    def test_update_path_info_with_paths(self):
        # 测试找到路径的情况
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        
        # 模拟路径数据
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
        
        # 模拟compare_best_paths返回None，避免格式化问题
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        # 模拟站点数据
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'},
            '3': {'name': 'Station C'},
            '4': {'name': 'Station D'}
        }
        
        self.display.update_path_info()
        
        # 验证路径信息被正确设置
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("Station A → Station C → Station B", call_args)
        self.assertIn("Station A → Station D → Station B", call_args)
        self.assertIn("15.50km", call_args)
        self.assertIn("25.30km/h", call_args)
        self.assertIn("18.20km", call_args)
        self.assertIn("22.10km/h", call_args)

    def test_update_path_info_with_best_path_comparison(self):
        # 测试最佳路径比较功能
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        
        # 模拟路径数据
        mock_paths = [
            {
                'path': ['1', '3', '2'],
                'distance': 12.5,
                'efficiency': 28.2
            }
        ]
        self.main_window.path_analyzer.find_all_paths.return_value = mock_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '3', '2']
        
        # 模拟比较结果
        mock_compare_result = {
            'dijkstra_path': ['1', '3', '2'],
            'dijkstra_distance': 12.5,
            'efficiency_path': ['1', '4', '2'],
            'efficiency_distance': 18.0,
            'efficiency_value': 30.5
        }
        self.main_window.path_analyzer.compare_best_paths.return_value = mock_compare_result
        self.main_window.path_analyzer._calculate_efficiency.return_value = 28.2
        
        # 模拟站点数据
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'},
            '3': {'name': 'Station C'},
            '4': {'name': 'Station D'}
        }
        
        self.display.update_path_info()
        
        # 验证最佳路径信息被显示
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("Recommended Path (Minimum Distance)", call_args)
        self.assertIn("Recommended Path (Maximum Efficiency)", call_args)
        self.assertIn("Station A → Station C → Station B", call_args)
        self.assertIn("Station A → Station D → Station B", call_args)
        self.assertIn("12.50km", call_args)
        self.assertIn("18.00km", call_args)
        self.assertIn("28.20km/h", call_args)
        self.assertIn("30.50km/h", call_args)

    def test_update_path_info_without_compare_result(self):
        # 测试没有比较结果的情况
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        
        # 模拟路径数据
        mock_paths = [
            {
                'path': ['1', '3', '2'],
                'distance': 15.5,
                'efficiency': 25.3
            }
        ]
        self.main_window.path_analyzer.find_all_paths.return_value = mock_paths
        # 设置best_path为空，这样就不会显示推荐路径部分
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        # 模拟站点数据
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'},
            '3': {'name': 'Station C'}
        }
        
        self.display.update_path_info()
        
        # 验证只显示基本路径信息，不显示推荐路径
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("Station A → Station C → Station B", call_args)
        self.assertNotIn("Recommended Path", call_args)

    def test_station_name_resolution(self):
        # 测试站点名称解析
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        
        # 模拟部分站点数据缺失的情况
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            # '2' 站点数据缺失
        }
        
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        
        self.display.update_path_info()
        
        # 验证使用站点ID作为后备名称
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("FROM Station A TO 2", call_args)

    def test_station_name_resolution_in_paths(self):
        # 测试路径中站点名称解析
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        
        # 模拟路径数据，包含缺失的站点
        mock_paths = [
            {
                'path': ['1', '3', '2'],
                'distance': 15.5,
                'efficiency': 25.3
            }
        ]
        self.main_window.path_analyzer.find_all_paths.return_value = mock_paths
        self.main_window.path_analyzer.find_best_path.return_value = ['1', '3', '2']
        # 设置compare_best_paths返回None，避免格式化问题
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        # 模拟部分站点数据
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '3': {'name': 'Station C'},
            # '2' 站点数据缺失
        }
        
        self.display.update_path_info()
        
        # 验证混合使用站点名称和ID
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("Station A → Station C → 2", call_args)

    def test_text_format_setting(self):
        # 测试文本格式设置
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        
        self.display.update_path_info()
        
        # 验证设置了富文本格式
        self.main_window.path_info.setTextFormat.assert_called_with(Qt.RichText)

    def test_state_updates(self):
        # 测试状态更新
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.path_analyzer.find_all_paths.return_value = []
        # 设置best_path为空，避免进入推荐路径显示代码块
        self.main_window.path_analyzer.find_best_path.return_value = []
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        self.display.update_path_info()
        
        # 验证状态被正确更新
        self.assertTrue(self.main_window.show_only_best_path)
        self.assertEqual(self.main_window.all_paths, [])
        self.assertEqual(self.main_window.best_path, [])

    def test_path_analyzer_calls(self):
        # 测试路径分析器的调用
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.path_analyzer.find_all_paths.return_value = []
        self.main_window.path_analyzer.find_best_path.return_value = []
        
        self.display.update_path_info()
        
        # 验证路径分析器方法被正确调用
        self.main_window.path_analyzer.find_all_paths.assert_called_with(
            '1', '2', include_efficiency=True
        )
        self.main_window.path_analyzer.find_best_path.assert_called_with('1', '2')

    def test_efficiency_calculation_call(self):
        # 测试效率计算调用
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
            'efficiency_value': 30.5
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
        
        # 验证效率计算方法被调用
        self.main_window.path_analyzer._calculate_efficiency.assert_called()

    def test_empty_path_info(self):
        # 测试空路径信息的处理
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
        
        # 验证基本信息被显示
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("FROM Station A TO Station B", call_args)
        self.assertIn("No path found", call_args)

    def test_multiple_paths_display(self):
        # 测试多条路径的显示
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        
        # 模拟多条路径
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
        # 设置compare_best_paths返回None，避免格式化问题
        self.main_window.path_analyzer.compare_best_paths.return_value = None
        
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A'},
            '2': {'name': 'Station B'},
            '3': {'name': 'Station C'},
            '4': {'name': 'Station D'},
            '5': {'name': 'Station E'}
        }
        
        self.display.update_path_info()
        
        # 验证所有路径都被显示
        self.main_window.path_info.setText.assert_called()
        call_args = self.main_window.path_info.setText.call_args[0][0]
        self.assertIn("Station A → Station C → Station B", call_args)
        self.assertIn("Station A → Station D → Station B", call_args)
        self.assertIn("Station A → Station E → Station B", call_args)
        self.assertEqual(call_args.count("-----------"), 4)  # 3条路径 + 1个分隔符

if __name__ == '__main__':
    unittest.main() 