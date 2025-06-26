import unittest
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QPoint
from project.module.custom_view import CustomGraphicsView

import sys

app = QApplication.instance() or QApplication(sys.argv)

class DummyParent(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hovered = False
        self.clicked = False
    def handle_station_hover(self, pos):
        self.hovered = True
    def handle_station_click(self, pos):
        self.clicked = True

class TestCustomGraphicsView(unittest.TestCase):
    def setUp(self):
        self.parent = DummyParent()
        self.view = CustomGraphicsView(self.parent)

    def test_init(self):
        self.assertIsInstance(self.view, CustomGraphicsView)
        self.assertEqual(self.view.parent, self.parent)

    def test_mouseMoveEvent_calls_parent(self):
        from PyQt5.QtGui import QMouseEvent
        event = QMouseEvent(QMouseEvent.MouseMove, QPoint(10, 10), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.view.mouseMoveEvent(event)
        self.assertTrue(self.parent.hovered)

    def test_mousePressEvent_calls_parent(self):
        from PyQt5.QtGui import QMouseEvent
        event = QMouseEvent(QMouseEvent.MouseButtonPress, QPoint(10, 10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        self.view.mousePressEvent(event)
        self.assertTrue(self.parent.clicked)

if __name__ == '__main__':
    unittest.main() 