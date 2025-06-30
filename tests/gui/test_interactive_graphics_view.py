import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, QPoint, QPointF
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
        event = QMouseEvent(QMouseEvent.MouseMove, QPointF(10, 10), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        with patch.object(self.view, 'mapToScene', return_value=QPointF(1, 1)):
            self.view.mouseMoveEvent(event)
        self.parent.handle_station_hover.assert_called()
        self.assertEqual(self.view.cursor().shape(), Qt.ArrowCursor)

    def test_mouse_move_event_add_station(self):
        self.parent.interaction_handler.add_station_mode = True
        event = QMouseEvent(QMouseEvent.MouseMove, QPointF(10, 10), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        with patch.object(self.view, 'mapToScene', return_value=QPointF(1, 1)), \
             patch('PyQt5.QtWidgets.QToolTip.showText') as mock_tip:
            self.view.mouseMoveEvent(event)
            self.assertEqual(self.view.cursor().shape(), Qt.CrossCursor)
            mock_tip.assert_called()

    def test_mouse_move_event_remove_station(self):
        self.parent.interaction_handler.remove_station_mode = True
        event = QMouseEvent(QMouseEvent.MouseMove, QPointF(10, 10), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        with patch.object(self.view, 'mapToScene', return_value=QPointF(1, 1)), \
             patch('PyQt5.QtWidgets.QToolTip.showText') as mock_tip:
            self.view.mouseMoveEvent(event)
            self.assertEqual(self.view.cursor().shape(), Qt.ForbiddenCursor)
            mock_tip.assert_called()

    def test_mouse_press_event(self):
        event = QMouseEvent(QMouseEvent.MouseButtonPress, QPointF(10, 10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
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
        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)
        self.parent.interaction_handler.add_station_mode = True
        self.parent.interaction_handler.remove_station_mode = True
        self.view.keyPressEvent(event)
        self.assertFalse(self.parent.interaction_handler.add_station_mode)
        self.assertFalse(self.parent.interaction_handler.remove_station_mode)
        self.parent.info_label.setText.assert_called()

if __name__ == '__main__':
    unittest.main() 