import unittest
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QPoint
from project.module.custom_view import CustomGraphicsView

import sys

app = QApplication.instance() or QApplication(sys.argv)

class DummyParent(QMainWindow):
    """mouse event handling"""
    """用于测试鼠标事件处理"""
    def __init__(self):
        """Initialize dummy parent with event tracking flags"""
        """初始化虚拟父类，包含事件跟踪标志"""
        super().__init__()
        self.hovered = False
        self.clicked = False
    def handle_station_hover(self, pos):
        """Handle station hover event"""
        """处理站点悬停事件"""
        self.hovered = True
    def handle_station_click(self, pos):
        """Handle station click event"""
        """处理站点点击事件"""
        self.clicked = True

class TestCustomGraphicsView(unittest.TestCase):
    """Test cases for custom graphics view functionality"""
    """自定义图形视图功能的测试用例"""
    def setUp(self):
        """Set up test environment with dummy parent and custom view"""
        """设置测试环境，包含虚拟父类和自定义视图"""
        self.parent = DummyParent()
        self.view = CustomGraphicsView(self.parent)

    def test_init(self):
        """Test custom graphics view initialization"""
        """测试自定义图形视图初始化"""
        self.assertIsInstance(self.view, CustomGraphicsView)
        self.assertEqual(self.view.parent, self.parent)

    def test_mouseMoveEvent_calls_parent(self):
        """Test that mouse move events are forwarded to parent"""
        """测试鼠标移动事件是否转发给父类"""
        from PyQt5.QtGui import QMouseEvent
        event = QMouseEvent(QMouseEvent.MouseMove, QPoint(10, 10), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.view.mouseMoveEvent(event)
        self.assertTrue(self.parent.hovered)

    def test_mousePressEvent_calls_parent(self):
        """Test that mouse press events are forwarded to parent"""
        """测试鼠标按下事件是否转发给父类"""
        from PyQt5.QtGui import QMouseEvent
        event = QMouseEvent(QMouseEvent.MouseButtonPress, QPoint(10, 10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        self.view.mousePressEvent(event)
        self.assertTrue(self.parent.clicked)

if __name__ == '__main__':
    unittest.main() 