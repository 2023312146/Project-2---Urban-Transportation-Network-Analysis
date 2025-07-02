import sys
from PyQt5.QtWidgets import QApplication
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

import unittest
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from project.gui.stop_and_route_dialogs_gui import DataDialogs
from unittest.mock import MagicMock, patch, call
from PyQt5.QtCore import Qt

class MockMainWindow:
    def __init__(self):
        self.data_manager = MagicMock()
        self.path_analyzer = MagicMock()
        self.interaction_handler = MagicMock()
        self.view = MagicMock()
        self.scene = MagicMock()
        self.handle_station_click = MagicMock()
        self.draw_network = MagicMock()

class TestDataDialogs(unittest.TestCase):
    def setUp(self):
        self.main_window = MockMainWindow()
        self.dialogs = DataDialogs(self.main_window)

    def test_init(self):
        """測試 DataDialogs 初始化"""
        self.assertEqual(self.dialogs.main_window, self.main_window)
        self.assertEqual(self.dialogs.data_manager, self.main_window.data_manager)
        self.assertEqual(self.dialogs.path_analyzer, self.main_window.path_analyzer)
        self.assertIsNone(self.dialogs.selected_from_station)
        self.assertIsNone(self.dialogs.connection_mode)

    def test_add_station_dialog(self):
        """測試添加站點對話框"""
        with patch('PyQt5.QtCore.Qt.CrossCursor') as mock_cursor:
            self.dialogs.add_station_dialog()
            
            # 驗證添加模式被啟用
            self.main_window.interaction_handler.add_station_mode = True
            self.main_window.view.setCursor.assert_called_with(mock_cursor)

    def test_remove_station_dialog_with_stations(self):
        """測試刪除站點對話框 - 有站點存在"""
        self.main_window.data_manager.stations = {'1': {'name': 'A'}}
        
        with patch('PyQt5.QtCore.Qt.ForbiddenCursor') as mock_cursor:
            self.dialogs.remove_station_dialog()
            
            # 驗證刪除模式被啟用
            self.main_window.interaction_handler.remove_station_mode = True
            self.main_window.view.setCursor.assert_called_with(mock_cursor)

    def test_remove_station_dialog_no_stations(self):
        """測試刪除站點對話框 - 沒有站點"""
        self.main_window.data_manager.stations = {}
        
        self.dialogs.remove_station_dialog()
        
        # 驗證沒有啟用刪除模式
        self.main_window.interaction_handler.remove_station_mode = False
        self.main_window.view.setCursor.assert_not_called()

    def test_update_station_type_dialog_with_stations(self):
        """測試更新站點類型對話框 - 有站點存在"""
        self.main_window.data_manager.stations = {
            '1': {'name': 'Station A', 'type': 'Residential'},
            '2': {'name': 'Station B', 'type': 'Commercial'}
        }
        
        with patch('PyQt5.QtWidgets.QInputDialog.getItem') as mock_get_item:
            # 模擬用戶選擇站點和類型
            mock_get_item.side_effect = [('Station A', True), ('Commercial', True)]
            
            self.dialogs.update_station_type_dialog()
            
            # 驗證 QInputDialog.getItem 被呼叫兩次
            self.assertEqual(mock_get_item.call_count, 2)
            # 驗證 update_station_type 被呼叫
            self.main_window.data_manager.update_station_type.assert_called_with('Station A', 'Commercial')
            # 驗證重繪網絡
            self.main_window.draw_network.assert_called()

    def test_update_station_type_dialog_no_stations(self):
        """測試更新站點類型對話框 - 沒有站點"""
        self.main_window.data_manager.stations = {}
        
        self.dialogs.update_station_type_dialog()
        
        # 驗證沒有呼叫任何方法
        self.main_window.data_manager.update_station_type.assert_not_called()
        self.main_window.draw_network.assert_not_called()

    def test_update_station_type_dialog_cancel_first(self):
        """測試更新站點類型對話框 - 第一次取消"""
        self.main_window.data_manager.stations = {'1': {'name': 'Station A'}}
        
        with patch('PyQt5.QtWidgets.QInputDialog.getItem') as mock_get_item:
            mock_get_item.return_value = ('Station A', False)  # 取消選擇站點
            
            self.dialogs.update_station_type_dialog()
            
            # 驗證只呼叫一次 getItem
            mock_get_item.assert_called_once()
            # 驗證沒有更新站點類型
            self.main_window.data_manager.update_station_type.assert_not_called()

    def test_update_station_type_dialog_cancel_second(self):
        """測試更新站點類型對話框 - 第二次取消"""
        self.main_window.data_manager.stations = {'1': {'name': 'Station A', 'type': 'Residential'}}
        
        with patch('PyQt5.QtWidgets.QInputDialog.getItem') as mock_get_item:
            mock_get_item.side_effect = [('Station A', True), ('Commercial', False)]  # 取消選擇類型
            
            self.dialogs.update_station_type_dialog()
            
            # 驗證呼叫兩次 getItem
            self.assertEqual(mock_get_item.call_count, 2)
            # 驗證沒有更新站點類型
            self.main_window.data_manager.update_station_type.assert_not_called()

    def test_add_connection_dialog_sufficient_stations(self):
        """測試添加連接對話框 - 站點數量足夠"""
        self.main_window.data_manager.stations = {'1': {}, '2': {}}
        
        with patch.object(self.dialogs, 'start_connection_click_mode') as mock_start_mode, \
             patch('PyQt5.QtCore.Qt.PointingHandCursor') as mock_cursor:
            
            self.dialogs.add_connection_dialog()
            
            # 驗證啟動連接點擊模式
            mock_start_mode.assert_called_with('add')
            # 驗證設置手型光標
            self.main_window.view.setCursor.assert_called_with(mock_cursor)

    def test_add_connection_dialog_insufficient_stations(self):
        """測試添加連接對話框 - 站點數量不足"""
        self.main_window.data_manager.stations = {'1': {}}  # 只有一個站點
        
        with patch.object(self.dialogs, 'start_connection_click_mode') as mock_start_mode:
            self.dialogs.add_connection_dialog()
            
            # 驗證沒有啟動連接點擊模式
            mock_start_mode.assert_not_called()
            # 驗證沒有設置光標
            self.main_window.view.setCursor.assert_not_called()

    def test_remove_connection_dialog_with_connections(self):
        """測試刪除連接對話框 - 有連接存在"""
        self.main_window.data_manager.distances = {('1', '2'): 1.5}
        
        with patch.object(self.dialogs, 'start_connection_click_mode') as mock_start_mode, \
             patch('PyQt5.QtCore.Qt.ForbiddenCursor') as mock_cursor:
            
            self.dialogs.remove_connection_dialog()
            
            # 驗證啟動連接點擊模式
            mock_start_mode.assert_called_with('remove')
            # 驗證設置禁止光標
            self.main_window.view.setCursor.assert_called_with(mock_cursor)

    def test_remove_connection_dialog_no_connections(self):
        """測試刪除連接對話框 - 沒有連接"""
        self.main_window.data_manager.distances = {}
        
        with patch.object(self.dialogs, 'start_connection_click_mode') as mock_start_mode:
            self.dialogs.remove_connection_dialog()
            
            # 驗證沒有啟動連接點擊模式
            mock_start_mode.assert_not_called()
            # 驗證沒有設置光標
            self.main_window.view.setCursor.assert_not_called()

    def test_start_connection_click_mode(self):
        """測試啟動連接點擊模式"""
        # 保存原始的點擊處理器
        original_handler = self.main_window.handle_station_click
        
        self.dialogs.start_connection_click_mode('add')
        
        # 驗證狀態被正確設置
        self.assertIsNone(self.dialogs.selected_from_station)
        self.assertEqual(self.dialogs.connection_mode, 'add')
        # 驗證原始點擊處理函數被保存
        self.assertEqual(self.dialogs.original_click_handler, original_handler)
        # 驗證點擊處理函數被重寫（不是同一個物件）
        self.assertNotEqual(self.main_window.handle_station_click, original_handler)
        # 驗證新的點擊處理器是一個函數
        self.assertTrue(callable(self.main_window.handle_station_click))

    def test_connection_click_handler_first_click(self):
        """測試連接點擊處理器 - 第一次點擊"""
        self.dialogs.start_connection_click_mode('add')
        
        # 模擬場景項目
        mock_item = MagicMock()
        mock_item.data.return_value = 'station_1'
        self.main_window.scene.items.return_value = [mock_item]
        
        # 執行點擊處理器
        click_handler = self.main_window.handle_station_click
        click_handler(MagicMock())  # 傳入位置
        
        # 驗證第一個站點被選中
        self.assertEqual(self.dialogs.selected_from_station, 'station_1')

    def test_connection_click_handler_same_station(self):
        """測試連接點擊處理器 - 點擊相同站點"""
        self.dialogs.start_connection_click_mode('add')
        # 直接設置屬性，忽略型別檢查
        setattr(self.dialogs, 'selected_from_station', 'station_1')
        
        # 模擬場景項目
        mock_item = MagicMock()
        mock_item.data.return_value = 'station_1'  # 相同站點
        self.main_window.scene.items.return_value = [mock_item]
        
        # 執行點擊處理器
        click_handler = self.main_window.handle_station_click
        click_handler(MagicMock())
        
        # 驗證沒有添加連接
        self.main_window.data_manager.add_connection.assert_not_called()

    def test_connection_click_handler_add_connection(self):
        """測試連接點擊處理器 - 添加連接"""
        self.dialogs.start_connection_click_mode('add')
        # 直接設置屬性，忽略型別檢查
        setattr(self.dialogs, 'selected_from_station', 'station_1')
        
        # 設置站點資料，包含 lat/lon 屬性
        self.main_window.data_manager.stations = {
            'station_1': {'name': 'Station A', 'lat': 1.0, 'lon': 2.0},
            'station_2': {'name': 'Station B', 'lat': 3.0, 'lon': 4.0}
        }
        self.main_window.data_manager.distances = {}  # 沒有現有連接
        
        # 模擬場景項目
        mock_item = MagicMock()
        mock_item.data.return_value = 'station_2'
        self.main_window.scene.items.return_value = [mock_item]
        
        with patch('project.gui.stop_and_route_dialogs_gui.calculate_distance_between_stops_by_id') as mock_calc:
            mock_calc.return_value = 2.5
            
            # 執行點擊處理器
            click_handler = self.main_window.handle_station_click
            click_handler(MagicMock())
            
            # 驗證添加連接
            self.main_window.data_manager.add_connection.assert_called_with('Station A', 'Station B', 2.5)
            # 驗證恢復原始點擊處理器
            self.assertEqual(self.main_window.handle_station_click, self.dialogs.original_click_handler)
            # 驗證清除狀態
            self.assertIsNone(self.dialogs.selected_from_station)
            self.assertIsNone(self.dialogs.connection_mode)
            # 驗證重繪網絡
            self.main_window.draw_network.assert_called()

    def test_connection_click_handler_remove_connection(self):
        """測試連接點擊處理器 - 刪除連接"""
        self.dialogs.start_connection_click_mode('remove')
        # 直接設置屬性，忽略型別檢查
        setattr(self.dialogs, 'selected_from_station', 'station_1')
        
        # 設置站點資料和現有連接
        self.main_window.data_manager.stations = {
            'station_1': {'name': 'Station A', 'lat': 1.0, 'lon': 2.0},
            'station_2': {'name': 'Station B', 'lat': 3.0, 'lon': 4.0}
        }
        self.main_window.data_manager.distances = {('station_1', 'station_2'): 2.5}
        
        # 模擬場景項目
        mock_item = MagicMock()
        mock_item.data.return_value = 'station_2'
        self.main_window.scene.items.return_value = [mock_item]
        
        # 執行點擊處理器
        click_handler = self.main_window.handle_station_click
        click_handler(MagicMock())
        
        # 驗證刪除連接
        self.main_window.data_manager.remove_connection.assert_called_with('Station A', 'Station B')
        # 驗證恢復原始點擊處理器
        self.assertEqual(self.main_window.handle_station_click, self.dialogs.original_click_handler)

    def test_connection_click_handler_no_item_data(self):
        """測試連接點擊處理器 - 項目沒有資料"""
        self.dialogs.start_connection_click_mode('add')
        
        # 模擬場景項目沒有資料
        mock_item = MagicMock()
        mock_item.data.return_value = None
        self.main_window.scene.items.return_value = [mock_item]
        
        # 執行點擊處理器
        click_handler = self.main_window.handle_station_click
        click_handler(MagicMock())
        
        # 驗證沒有選中站點
        self.assertIsNone(self.dialogs.selected_from_station)

    def test_connection_click_handler_no_items(self):
        """測試連接點擊處理器 - 沒有項目"""
        self.dialogs.start_connection_click_mode('add')
        
        # 模擬沒有場景項目
        self.main_window.scene.items.return_value = []
        
        # 執行點擊處理器
        click_handler = self.main_window.handle_station_click
        click_handler(MagicMock())
        
        # 驗證沒有選中站點
        self.assertIsNone(self.dialogs.selected_from_station)

    def test_find_highest_degree_station_dialog_with_station(self):
        """測試查找最高度數站點對話框 - 有站點"""
        # 設置站點資料
        self.main_window.data_manager.stations = {
            'station_1': {'name': 'Station A', 'connections': ['station_2', 'station_3']},
            'station_2': {'name': 'Station B', 'connections': ['station_1']},
            'station_3': {'name': 'Station C', 'connections': ['station_1']}
        }
        
        # 模擬 path_analyzer 返回最高度數站點
        self.main_window.path_analyzer.find_highest_degree_station.return_value = 'station_1'
        
        with patch('project.gui.stop_and_route_dialogs_gui.QMessageBox') as MockMessageBox:
            mock_msg = MagicMock()
            MockMessageBox.return_value = mock_msg
            
            self.dialogs.find_highest_degree_station_dialog()
            
            # 驗證查找最高度數站點
            self.main_window.path_analyzer.find_highest_degree_station.assert_called()
            # 驗證創建消息框
            MockMessageBox.assert_called()
            # 驗證設置樣式
            mock_msg.setStyleSheet.assert_called()
            # 驗證設置標題和內容
            mock_msg.setWindowTitle.assert_called_with("Highest Degree Station")
            mock_msg.setText.assert_called()
            # 驗證設置按鈕
            mock_msg.setStandardButtons.assert_called()
            # 驗證執行對話框
            mock_msg.exec_.assert_called()

    def test_find_highest_degree_station_dialog_no_station(self):
        """測試查找最高度數站點對話框 - 沒有站點"""
        # 模擬 path_analyzer 返回 None
        self.main_window.path_analyzer.find_highest_degree_station.return_value = None
        
        with patch('project.gui.stop_and_route_dialogs_gui.QMessageBox') as MockMessageBox:
            mock_msg = MagicMock()
            MockMessageBox.return_value = mock_msg
            
            self.dialogs.find_highest_degree_station_dialog()
            
            # 驗證查找最高度數站點
            self.main_window.path_analyzer.find_highest_degree_station.assert_called()
            # 驗證設置標題和內容
            mock_msg.setWindowTitle.assert_called_with("Highest Degree Station")
            mock_msg.setText.assert_called_with("No stations available")

    def test_get_messagebox_style(self):
        """測試獲取消息框樣式"""
        style = self.dialogs.get_messagebox_style()
        
        # 驗證樣式包含必要的 CSS 規則
        self.assertIn('QMessageBox', style)
        self.assertIn('QLabel', style)
        self.assertIn('QPushButton', style)
        self.assertIn('font-size', style)
        self.assertIn('min-width', style)

    def test_connection_click_handler_existing_connection_add(self):
        """測試連接點擊處理器 - 添加已存在的連接"""
        self.dialogs.start_connection_click_mode('add')
        # 直接設置屬性，忽略型別檢查
        setattr(self.dialogs, 'selected_from_station', 'station_1')
        
        # 設置現有連接
        self.main_window.data_manager.distances = {('station_1', 'station_2'): 2.5}
        
        # 模擬場景項目
        mock_item = MagicMock()
        mock_item.data.return_value = 'station_2'
        self.main_window.scene.items.return_value = [mock_item]
        
        # 執行點擊處理器
        click_handler = self.main_window.handle_station_click
        click_handler(MagicMock())
        
        # 驗證沒有添加連接
        self.main_window.data_manager.add_connection.assert_not_called()

    def test_connection_click_handler_nonexistent_connection_remove(self):
        """測試連接點擊處理器 - 刪除不存在的連接"""
        self.dialogs.start_connection_click_mode('remove')
        # 直接設置屬性，忽略型別檢查
        setattr(self.dialogs, 'selected_from_station', 'station_1')
        
        # 設置沒有現有連接
        self.main_window.data_manager.distances = {}
        
        # 模擬場景項目
        mock_item = MagicMock()
        mock_item.data.return_value = 'station_2'
        self.main_window.scene.items.return_value = [mock_item]
        
        # 執行點擊處理器
        click_handler = self.main_window.handle_station_click
        click_handler(MagicMock())
        
        # 驗證沒有刪除連接
        self.main_window.data_manager.remove_connection.assert_not_called()

if __name__ == '__main__':
    unittest.main() 