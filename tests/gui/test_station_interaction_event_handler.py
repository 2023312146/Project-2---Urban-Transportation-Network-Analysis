import unittest
import sys
import os
from unittest.mock import MagicMock, patch, call
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import QGraphicsEllipseItem, QDialog
from project.gui.station_interaction_event_handler import InteractionHandler
from project.gui.station_interaction_event_handler import calculate_distance_between_stops_by_id  # 假设需要导入

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class DummyStop:
    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon

class MockMainWindow:
    def __init__(self):
        self.data_manager = MagicMock()
        self.hovered_station = None
        self.selected_start = None
        self.selected_end = None
        self.info_label = MagicMock()
        self.path_info = MagicMock()
        self.draw_network = MagicMock()
        self.clear_selection = MagicMock()
        self.update_path_info = MagicMock()
        self.view = MagicMock()
        self.scene = MagicMock()

class TestInteractionHandler(unittest.TestCase):
    def setUp(self):
        self.main_window = MockMainWindow()
        # 初始化数据管理器模拟对象
        self.main_window.data_manager.stations = {
            '1': {'x': 0, 'y': 0, 'name': 'A', 'type': 'Residential', 'wait_time': 5, 'connections': ['2']},
            '2': {'x': 10, 'y': 10, 'name': 'B', 'type': 'Commercial', 'wait_time': 3, 'connections': ['1']}
        }
        self.main_window.data_manager.distances = {('1', '2'): 1.5, ('2', '1'): 1.5}
        self.main_window.data_manager.get_stop_by_id.return_value = DummyStop(1.1, 2.2)
        self.handler = InteractionHandler(self.main_window)

    # 测试初始化方法
    def test_init(self):
        self.assertEqual(self.handler.main_window, self.main_window)
        self.assertEqual(self.handler.data_manager, self.main_window.data_manager)
        self.assertFalse(self.handler.add_station_mode)
        self.assertFalse(self.handler.remove_station_mode)
        self.assertEqual(self.handler.hover_area_padding, 10.0)

    # 测试 handle_station_hover - 悬停在已缓存的站点内
    def test_handle_station_hover_cached_station_inside(self):
        self.main_window.hovered_station = '1'
        pos = QPointF(0, 0)  # 站点1的坐标附近
        with patch.object(self.handler, '_get_station_tooltip') as mock_tooltip:
            mock_tooltip.return_value = "Tooltip"
            result = self.handler.handle_station_hover(pos)
            self.assertEqual(result, "Tooltip")
            mock_tooltip.assert_called_with('1')

    # 测试 handle_station_hover - 悬停在已缓存的站点外
    def test_handle_station_hover_cached_station_outside(self):
        self.main_window.hovered_station = '1'
        pos = QPointF(100, 100)  # 远离站点1的位置
        self.handler.handle_station_hover(pos)
        self.assertIsNone(self.main_window.hovered_station)

    # 测试 handle_station_hover - 找到新站点
    def test_handle_station_hover_new_station_found(self):
        mock_item = MagicMock(spec=QGraphicsEllipseItem)
        mock_item.data.return_value = '1'
        self.main_window.scene.items.return_value = [mock_item]
        pos = QPointF(0, 0)
        with patch.object(self.handler, '_get_station_tooltip') as mock_tooltip:
            mock_tooltip.return_value = "Tooltip"
            result = self.handler.handle_station_hover(pos)
            self.assertEqual(result, "Tooltip")
            self.assertEqual(self.main_window.hovered_station, '1')

    # 测试 _get_station_tooltip - 正常情况
    def test_get_station_tooltip_normal(self):
        tooltip = self.handler._get_station_tooltip('1')
        self.assertIn("Stop: A", tooltip)
        self.assertIn("Type: Residential", tooltip)
        self.assertIn("Coordinates: (1.100000, 2.200000)", tooltip)
        self.assertIn("Outgoing Connections:\n • B (1.5km)", tooltip)

    # 测试 _get_station_tooltip - 无stop_obj
    def test_get_station_tooltip_no_stop_obj(self):
        self.main_window.data_manager.get_stop_by_id.return_value = None
        tooltip = self.handler._get_station_tooltip('1')
        self.assertIn("Coordinates: (未知, 未知)", tooltip)

    # 测试 handle_station_click - 添加模式
    def test_handle_station_click_add_mode(self):
        self.handler.add_station_mode = True
        with patch.object(self.handler, 'add_station_at_position') as mock_add:
            self.handler.handle_station_click(QPointF(1, 1))
            mock_add.assert_called_once_with(QPointF(1, 1))

    # 测试 handle_station_click - 删除模式
    def test_handle_station_click_remove_mode(self):
        self.handler.remove_station_mode = True
        with patch.object(self.handler, 'remove_station_at_position') as mock_remove:
            self.handler.handle_station_click(QPointF(1, 1))
            mock_remove.assert_called_once_with(QPointF(1, 1))

    # 测试 handle_station_click - 选择起点和终点
    def test_handle_station_click_select_start_end(self):
        mock_item = MagicMock(spec=QGraphicsEllipseItem)
        mock_item.data.return_value = '1'
        self.main_window.scene.items.return_value = [mock_item]
        # 第一次点击选起点
        self.handler.handle_station_click(QPointF(0, 0))
        self.assertEqual(self.main_window.selected_start, '1')
        self.main_window.info_label.setText.assert_called_with("Start point selected: A\nPlease click to select end point")
        # 第二次点击选终点
        mock_item.data.return_value = '2'
        self.handler.handle_station_click(QPointF(10, 10))
        self.assertEqual(self.main_window.selected_end, '2')
        self.main_window.update_path_info.assert_called_once()

    # 测试 add_station_at_position - 位置冲突
    def test_add_station_at_position_conflict(self):
        with patch('PyQt5.QtWidgets.QMessageBox.exec_'):
            self.handler.add_station_at_position(QPointF(0, 0))  # 与站点1位置冲突
            self.main_window.view.setCursor.assert_called_with(Qt.ArrowCursor)
            self.assertFalse(self.handler.add_station_mode)

    # 测试 remove_station_at_position - 找到站点
    def test_remove_station_at_position_found(self):
        mock_item = MagicMock(spec=QGraphicsEllipseItem)
        mock_item.data.return_value = '1'
        self.main_window.scene.items.return_value = [mock_item]
        self.handler.remove_station_at_position(QPointF(0, 0))
        self.main_window.data_manager.remove_station.assert_called_with('A')
        self.assertFalse(self.handler.remove_station_mode)

    # 测试 remove_station_at_position - 未找到站点
    def test_remove_station_at_position_not_found(self):
        self.main_window.scene.items.return_value = []
        self.handler.remove_station_at_position(QPointF(0, 0))
        self.assertFalse(self.handler.remove_station_mode)

    # 测试 remove_station_at_position - 删除选中的起点
    def test_remove_station_at_position_selected_start(self):
        mock_item = MagicMock(spec=QGraphicsEllipseItem)
        mock_item.data.return_value = '1'
        self.main_window.scene.items.return_value = [mock_item]
        self.main_window.selected_start = '1'
        self.handler.remove_station_at_position(QPointF(0, 0))
        self.main_window.clear_selection.assert_called_once()
        self.assertFalse(self.handler.remove_station_mode)

if __name__ == '__main__':
    unittest.main()