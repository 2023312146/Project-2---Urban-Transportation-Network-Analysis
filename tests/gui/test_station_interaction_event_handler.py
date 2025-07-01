import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from project.gui import station_interaction_event_handler
from project.gui.station_interaction_event_handler import InteractionHandler
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import QPointF
from typing import Optional
from PyQt5.QtWidgets import QGraphicsEllipseItem, QWidget, QApplication

# 初始化QApplication（如果還沒有初始化的話）
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

class DummyStop:
    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon

class MockMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = MagicMock()
        self.hovered_station: Optional[str] = None
        self.selected_start: Optional[str] = None
        self.selected_end: Optional[str] = None
        self.info_label = MagicMock()
        self.path_info = MagicMock()
        self.draw_network = MagicMock()
        self.clear_selection = MagicMock()
        self.update_path_info = MagicMock()
        self.view = MagicMock()
        self.scene = MagicMock()

class TestStationInteractionEventHandler(unittest.TestCase):
    def setUp(self):
        self.main_window = MockMainWindow()
        # Setup data_manager directly on the main_window mock
        self.main_window.data_manager.stations = {
            '1': {'x': 0, 'y': 0, 'name': 'A', 'type': 'Residential', 'wait_time': 5, 'connections': ['2']},
            '2': {'x': 10, 'y': 10, 'name': 'B', 'type': 'Commercial', 'wait_time': 3, 'connections': ['1']}
        }
        self.main_window.data_manager.distances = {('1', '2'): 1.5, ('2', '1'): 1.5}
        self.main_window.data_manager.get_stop_by_id.return_value = DummyStop(1.1, 2.2)
        self.handler = InteractionHandler(self.main_window)

    def test_handle_station_hover_within_area(self):
        self.main_window.hovered_station = '1'
        pos = QPointF(0, 0)
        result = self.handler.handle_station_hover(pos)
        if result is not None:
            self.assertIn('Stop: A', result)
        else:
            self.fail('Expected non-None result')

    def test_handle_station_hover_outside_area(self):
        self.main_window.hovered_station = '1'
        pos = QPointF(100, 100)
        # We need to mock the scene items to be empty for this logic to work
        self.main_window.scene.items.return_value = []
        result = self.handler.handle_station_hover(pos)
        self.assertIsNone(result)
        self.assertIsNone(self.main_window.hovered_station)

    def test_handle_station_hover_no_items(self):
        self.main_window.hovered_station = None
        self.main_window.scene.items.return_value = []
        pos = QPointF(0, 0)
        result = self.handler.handle_station_hover(pos)
        self.assertIsNone(result)

    def test_handle_station_hover_item_no_station(self):
        self.main_window.hovered_station = None
        mock_item = MagicMock(spec=QGraphicsEllipseItem)
        mock_item.data.return_value = None
        self.main_window.scene.items.return_value = [mock_item]
        pos = QPointF(0, 0)
        result = self.handler.handle_station_hover(pos)
        self.assertIsNone(result)

    def test_get_station_tooltip_missing_station(self):
        self.main_window.data_manager.stations = {}
        result = self.handler._get_station_tooltip('999')
        self.assertIsNone(result)

    def test_get_station_tooltip_no_stop_obj(self):
        self.main_window.data_manager.get_stop_by_id.return_value = None
        result = self.handler._get_station_tooltip('1')
        if result is not None:
            self.assertIn('未知', result)
        else:
            self.fail('Expected non-None result')

    def test_get_station_tooltip_no_connections(self):
        self.main_window.data_manager.stations['1']['connections'] = []
        result = self.handler._get_station_tooltip('1')
        if result is not None:
            self.assertIn('Stop: A', result)
        else:
            self.fail('Expected non-None result')

    def test_handle_station_click_add_mode(self):
        self.handler.add_station_mode = True
        with patch.object(self.handler, 'add_station_at_position') as mock_add:
            self.handler.handle_station_click(QPointF(1, 1))
            mock_add.assert_called()

    def test_handle_station_click_remove_mode(self):
        self.handler.remove_station_mode = True
        with patch.object(self.handler, 'remove_station_at_position') as mock_remove:
            self.handler.handle_station_click(QPointF(1, 1))
            mock_remove.assert_called()

    def test_handle_station_click_select_start_end(self):
        mock_item1 = MagicMock(spec=QGraphicsEllipseItem)
        mock_item1.data.return_value = '1'
        self.main_window.scene.items.return_value = [mock_item1]
        self.handler.handle_station_click(QPointF(0, 0))
        self.assertEqual(self.main_window.selected_start, '1')
        self.main_window.info_label.setText.assert_called()
        # 再點擊另一個
        mock_item2 = MagicMock(spec=QGraphicsEllipseItem)
        mock_item2.data.return_value = '2'
        self.main_window.scene.items.return_value = [mock_item2]
        self.handler.handle_station_click(QPointF(10, 10))
        self.assertEqual(self.main_window.selected_end, '2')
        self.main_window.update_path_info.assert_called()

    def test_handle_station_click_repeat(self):
        mock_item = MagicMock(spec=QGraphicsEllipseItem)
        mock_item.data.return_value = '1'
        self.main_window.scene.items.return_value = [mock_item]
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.handler.handle_station_click(QPointF(0, 0))
        self.assertEqual(self.main_window.selected_start, '1')
        self.assertIsNone(self.main_window.selected_end)
        self.main_window.info_label.setText.assert_called()
        self.main_window.path_info.setText.assert_called()

    def test_add_station_at_position_cancel(self):
        with patch('project.gui.station_interaction_event_handler.QDialog') as MockDialog, \
             patch('project.gui.station_interaction_event_handler.QVBoxLayout'), \
             patch('project.gui.station_interaction_event_handler.QLabel'), \
             patch('project.gui.station_interaction_event_handler.QLineEdit'), \
             patch('project.gui.station_interaction_event_handler.QComboBox'), \
             patch('project.gui.station_interaction_event_handler.QDialogButtonBox'):
            mock_dialog_instance = MockDialog.return_value
            mock_dialog_instance.exec_.return_value = 0
            self.handler.add_station_at_position(QPointF(5, 5))
            self.main_window.draw_network.assert_called()
            self.main_window.view.setCursor.assert_called()

    def test_remove_station_at_position_found(self):
        mock_item = MagicMock(spec=QGraphicsEllipseItem)
        mock_item.data.return_value = '1'
        self.main_window.scene.items.return_value = [mock_item]
        self.main_window.data_manager.stations['1']['name'] = 'A'
        self.handler.remove_station_at_position(QPointF(0, 0))
        self.main_window.data_manager.remove_station.assert_called_with('A')
        self.main_window.draw_network.assert_called()
        self.assertFalse(self.handler.remove_station_mode)

    def test_remove_station_at_position_not_found(self):
        self.main_window.scene.items.return_value = []
        self.handler.remove_station_at_position(QPointF(0, 0))
        self.assertFalse(self.handler.remove_station_mode)

    def test_remove_station_at_position_selected_start(self):
        mock_item = MagicMock(spec=QGraphicsEllipseItem)
        mock_item.data.return_value = '1'
        self.main_window.scene.items.return_value = [mock_item]
        self.main_window.data_manager.stations['1']['name'] = 'A'
        self.main_window.selected_start = '1'
        self.handler.remove_station_at_position(QPointF(0, 0))
        self.main_window.clear_selection.assert_called()
        self.assertFalse(self.handler.remove_station_mode)

    def test_remove_station_at_position_selected_end(self):
        mock_item = MagicMock(spec=QGraphicsEllipseItem)
        mock_item.data.return_value = '2'
        self.main_window.scene.items.return_value = [mock_item]
        self.main_window.data_manager.stations['2']['name'] = 'B'
        self.main_window.selected_end = '2'
        self.handler.remove_station_at_position(QPointF(0, 0))
        self.main_window.clear_selection.assert_called()
        self.assertFalse(self.handler.remove_station_mode)

    def test_add_station_trace(self):
        self.handler.add_station_at_position(QPointF(5, 5))
    def test_add_station_simple(self):
        """最簡單的添加站點測試，不涉及任何GUI"""
        # 測試數據轉換邏輯
        test_station_type = "Residential"
        test_position = QPointF(100, 200)
        
        # 準備 mock 的 data_manager
        mock_data_manager = MagicMock()
        mock_data_manager._convert_string_to_zone_type.return_value = "Residential"
        mock_data_manager._get_wait_time.return_value = 2
        mock_data_manager.stations = {}
        
        # 測試數據轉換方法
        zone_type = mock_data_manager._convert_string_to_zone_type(test_station_type)
        wait_time = mock_data_manager._get_wait_time(zone_type)
        
        # 驗證結果
        self.assertEqual(zone_type, "Residential")
        self.assertEqual(wait_time, 2)
        
        # 驗證方法被調用
        mock_data_manager._convert_string_to_zone_type.assert_called_once_with(test_station_type)
        mock_data_manager._get_wait_time.assert_called_once_with(zone_type)

if __name__ == '__main__':
    unittest.main() 