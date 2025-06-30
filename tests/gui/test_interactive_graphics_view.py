import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, QPoint, QPointF, QEvent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QMouseEvent, QWheelEvent, QKeyEvent
import sys

# 避免 QApplication 重复创建
app = QApplication.instance() or QApplication(sys.argv)

from project.gui.interactive_graphics_view import CustomGraphicsView

class TestCustomGraphicsView(unittest.TestCase):
    def setUp(self):
        # parent 传 None，后续用 patch.object 注入 parent 属性
        self.view = CustomGraphicsView(None)
        self.parent = MagicMock()
        self.parent.handle_station_hover = MagicMock()
        self.parent.handle_station_click = MagicMock()
        self.parent.info_label = MagicMock()
        self.parent.interaction_handler = MagicMock()
        self.parent.interaction_handler.add_station_mode = False
        self.parent.interaction_handler.remove_station_mode = False
        self.parent.data_dialogs = MagicMock()
        # 注入 parent 属性
        self.view.parent = self.parent

    def test_mouse_move_event_default(self):
        # 確保移動距離大於 move_threshold
        self.view.last_mouse_pos = QPoint(0, 0)
        event = QMouseEvent(QMouseEvent.Type.MouseMove, QPointF(10, 10), Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
        with patch.object(self.view, 'mapToScene', return_value=QPointF(1, 1)):
            self.view.mouseMoveEvent(event)
        self.parent.handle_station_hover.assert_not_called()  # 由於 process_hover 是延遲觸發，這裡不會立即呼叫
        # 強制觸發 process_hover
        self.view.current_hover_pos = QPointF(1, 1)
        self.parent.handle_station_hover.return_value = "測試站點"
        self.view.process_hover()
        self.parent.handle_station_hover.assert_called()
        self.assertEqual(self.view.cursor().shape(), Qt.CursorShape.ArrowCursor)

    def test_mouse_move_event_add_station(self):
        self.parent.interaction_handler.add_station_mode = True
        # 明确设置 handle_station_hover 返回有效信息（非 None）
        self.parent.handle_station_hover.return_value = "測試站點"  # 关键修改：确保返回非空
        event = QMouseEvent(QMouseEvent.Type.MouseMove, QPointF(10, 10), Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
        with patch.object(self.view, 'mapToScene', return_value=QPointF(1, 1)), \
             patch('PyQt5.QtWidgets.QToolTip.showText') as mock_tip:
            self.view.mouseMoveEvent(event)
            # 模拟定时器触发（实际由 hover_timer 自动触发）
            self.view.process_hover()  # 手动触发后，状态应与定时器触发一致
            # 验证光标形状
            self.assertEqual(self.view.cursor().shape(), Qt.CursorShape.CrossCursor)
            # 验证工具提示被调用（因 handle_station_hover 返回非空）
            mock_tip.assert_called()

    def test_mouse_move_event_remove_station(self):
        self.parent.interaction_handler.remove_station_mode = True
        event = QMouseEvent(QMouseEvent.Type.MouseMove, QPointF(10, 10), Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
        with patch.object(self.view, 'mapToScene', return_value=QPointF(1, 1)), \
             patch('PyQt5.QtWidgets.QToolTip.showText') as mock_tip:
            self.view.mouseMoveEvent(event)
            # 手動觸發 process_hover
            self.view.current_hover_pos = QPointF(1, 1)
            self.parent.handle_station_hover.return_value = "測試站點"
            self.view.process_hover()
            self.assertEqual(self.view.cursor().shape(), Qt.CursorShape.ForbiddenCursor)
            mock_tip.assert_called()

    def test_mouse_press_event(self):
        event = QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(10, 10), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        with patch.object(self.view, 'mapToScene', return_value=QPointF(1, 1)):
            self.view.mousePressEvent(event)
        self.parent.handle_station_click.assert_called()

    def test_wheel_event_zoom(self):
        # QWheelEvent 构造参数较多，使用 MagicMock 并 patch angleDelta
        event = MagicMock(spec=QWheelEvent)
        event.angleDelta.return_value.y.return_value = 120
        with patch.object(self.view, 'scale') as mock_scale:
            self.view.wheelEvent(event)
            mock_scale.assert_called()

    def test_key_press_event_escape(self):
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        self.parent.interaction_handler.add_station_mode = True
        self.parent.interaction_handler.remove_station_mode = True
        self.view.keyPressEvent(event)
        self.assertFalse(self.parent.interaction_handler.add_station_mode)
        self.assertFalse(self.parent.interaction_handler.remove_station_mode)
        self.parent.info_label.setText.assert_called()

    def test_process_hover_none_pos(self):
        self.view.current_hover_pos = None
        # 不應有異常
        self.view.process_hover()
        self.assertFalse(self.view.hover_label.isVisible())

    def test_process_hover_no_tooltip(self):
        self.view.current_hover_pos = QPointF(1, 1)
        self.parent.handle_station_hover.return_value = None
        self.view.process_hover()
        self.assertFalse(self.view.hover_label.isVisible())
        self.assertIsNone(self.view.last_hovered_station)

    def test_process_hover_no_interaction_handler(self):
        self.view.current_hover_pos = QPointF(1, 1)
        self.parent.handle_station_hover.return_value = 'info'
        del self.parent.interaction_handler
        self.view.process_hover()
        self.assertTrue(self.view.hover_label.isVisible())

    def test_process_hover_add_station_mode(self):
        self.view.current_hover_pos = QPointF(1, 1)
        self.parent.handle_station_hover.return_value = 'info'
        self.parent.interaction_handler.add_station_mode = True
        self.parent.interaction_handler.remove_station_mode = False
        with patch('PyQt5.QtWidgets.QToolTip.showText') as mock_tip:
            self.view.process_hover()
            self.assertTrue(self.view.hover_label.isVisible())
            self.assertEqual(self.view.cursor().shape(), Qt.CursorShape.CrossCursor)
            mock_tip.assert_called()

    def test_process_hover_remove_station_mode(self):
        self.view.current_hover_pos = QPointF(1, 1)
        self.parent.handle_station_hover.return_value = 'info'
        self.parent.interaction_handler.add_station_mode = False
        self.parent.interaction_handler.remove_station_mode = True
        with patch('PyQt5.QtWidgets.QToolTip.showText') as mock_tip:
            self.view.process_hover()
            self.assertTrue(self.view.hover_label.isVisible())
            self.assertEqual(self.view.cursor().shape(), Qt.CursorShape.ForbiddenCursor)
            mock_tip.assert_called()

    def test_process_hover_default_cursor(self):
        self.view.current_hover_pos = QPointF(1, 1)
        self.parent.handle_station_hover.return_value = 'info'
        self.parent.interaction_handler.add_station_mode = False
        self.parent.interaction_handler.remove_station_mode = False
        with patch('PyQt5.QtWidgets.QToolTip.hideText') as mock_hide:
            self.view.process_hover()
            self.assertTrue(self.view.hover_label.isVisible())
            self.assertEqual(self.view.cursor().shape(), Qt.CursorShape.ArrowCursor)
            mock_hide.assert_called()

    def test_mouse_press_event_not_left(self):
        event = QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(10, 10), Qt.MouseButton.RightButton, Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier)
        with patch.object(self.view, 'mapToScene', return_value=QPointF(1, 1)):
            self.view.mousePressEvent(event)
        self.parent.handle_station_click.assert_not_called()

    def test_wheel_event_zoom_out(self):
        event = MagicMock(spec=QWheelEvent)
        event.angleDelta.return_value.y.return_value = -120
        with patch.object(self.view, 'scale') as mock_scale:
            self.view.wheelEvent(event)
            mock_scale.assert_called_with(1/1.2, 1/1.2)

    def test_key_press_event_no_interaction_handler(self):
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        del self.parent.interaction_handler
        self.view.keyPressEvent(event)  # 不應異常

    def test_key_press_event_no_data_dialogs(self):
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        del self.parent.data_dialogs
        self.view.keyPressEvent(event)  

    def test_key_press_event_data_dialogs_no_selected_from_station(self):
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        self.parent.data_dialogs.selected_from_station = None
        self.view.keyPressEvent(event)  

    def test_key_press_event_data_dialogs_with_original_click_handler(self):
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        self.parent.data_dialogs.selected_from_station = 1
        self.parent.data_dialogs.connection_mode = 'test'
        self.parent.data_dialogs.original_click_handler = MagicMock()
        self.view.keyPressEvent(event)
        self.assertIsNone(self.parent.data_dialogs.selected_from_station)
        self.assertIsNone(self.parent.data_dialogs.connection_mode)
        self.parent.info_label.setText.assert_called()
        self.assertEqual(self.view.cursor().shape(), Qt.CursorShape.ArrowCursor)

    def test_leave_event(self):
        self.view.hover_label.show()
        self.view.last_hovered_station = None
        self.view.hover_timer.start()
        event = QEvent(QEvent.Type.Leave)
        self.view.leaveEvent(event)
        self.assertFalse(self.view.hover_label.isVisible())
        self.assertIsNone(self.view.last_hovered_station)
        self.assertFalse(self.view.hover_timer.isActive())

if __name__ == '__main__':
    unittest.main()