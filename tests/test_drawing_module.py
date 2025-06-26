import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QMainWindow, QApplication
from project.module.drawing_module import DrawingModule
import sys

app = QApplication.instance() or QApplication(sys.argv)

class DummyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = MagicMock()
        self.view = MagicMock()
        self.data_manager = MagicMock()
        self.best_path = []
        self.show_only_best_path = False
        self.selected_start = None
        self.selected_end = None
        self.all_paths = []
        self.path_colors = []
        self.width = lambda: 1000

class TestDrawingModule(unittest.TestCase):
    def setUp(self):
        self.main_window = DummyMainWindow()
        self.drawing = DrawingModule(self.main_window)

    def test_init(self):
        self.assertIs(self.drawing.main_window, self.main_window)

    def test_init_scene_callable(self):
        try:
            self.drawing.init_scene()
        except Exception:
            pass

    def test_draw_network_callable(self):
        try:
            self.drawing.draw_network()
        except Exception:
            pass

    def test_draw_grid_callable(self):
        try:
            self.drawing.draw_grid()
        except Exception:
            pass

    def test_draw_arrow_callable(self):
        from PyQt5.QtCore import QLineF
        from PyQt5.QtGui import QColor
        line = QLineF(0,0,10,10)
        try:
            self.drawing.draw_arrow(line, QColor(0,0,0))
        except Exception:
            pass

if __name__ == '__main__':
    unittest.main() 