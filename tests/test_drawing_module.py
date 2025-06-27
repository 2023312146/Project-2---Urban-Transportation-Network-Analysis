import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QLineF, QPointF
from PyQt5.QtGui import QColor, QPen, QFont, QPolygonF, QBrush
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

    @patch('project.module.drawing_module.QGraphicsScene')
    @patch('project.module.drawing_module.QPainter')
    def test_init_scene(self, mock_painter, mock_scene):
        self.drawing.init_scene()
        self.main_window.view.setScene.assert_called()
        self.main_window.view.setRenderHint.assert_called()
        self.main_window.view.setDragMode.assert_called()
        self.main_window.view.setMouseTracking.assert_called()

    def test_draw_network_empty(self):
        self.main_window.data_manager.stations = {}
        self.main_window.data_manager.lines = {}
        self.main_window.data_manager.distances = {}
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_network_with_best_path(self):
        self.main_window.best_path = ['1', '2']
        self.main_window.show_only_best_path = True
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Commercial'},
            '2': {'x': 200, 'y': 200, 'name': 'B', 'type': 'Residential'}
        }
        self.main_window.data_manager.distances = {('1', '2'): 10.0}
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_network_with_lines(self):
        self.main_window.best_path = []
        self.main_window.data_manager.lines = {
            '1': {'color': [255, 0, 0], 'stations': ['1', '2']}
        }
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Commercial', 'id': '1'},
            '2': {'x': 200, 'y': 200, 'name': 'B', 'type': 'Residential', 'id': '2'}
        }
        self.main_window.data_manager.distances = {('1', '2'): 10.0}
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_network_with_selected_stations(self):
        self.main_window.selected_start = '1'
        self.main_window.selected_end = '2'
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Commercial'},
            '2': {'x': 200, 'y': 200, 'name': 'B', 'type': 'Residential'}
        }
        self.main_window.data_manager.distances = {('1', '2'): 10.0}
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_network_with_paths(self):
        self.main_window.all_paths = [['1', '2']]
        self.main_window.best_path = ['1', '2']
        self.main_window.path_colors = [QColor(255, 0, 0)]
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Commercial'},
            '2': {'x': 200, 'y': 200, 'name': 'B', 'type': 'Residential'}
        }
        self.main_window.data_manager.distances = {('1', '2'): 10.0}
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_network_mixed_station_type(self):
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Mixed'}
        }
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_network_industrial_station_type(self):
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Industrial'}
        }
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_grid(self):
        self.main_window.scene.sceneRect.return_value = MagicMock()
        self.main_window.scene.sceneRect.return_value.left.return_value = 0
        self.main_window.scene.sceneRect.return_value.right.return_value = 1000
        self.main_window.scene.sceneRect.return_value.top.return_value = 0
        self.main_window.scene.sceneRect.return_value.bottom.return_value = 1000
        self.main_window.scene.sceneRect.return_value.height.return_value = 1000
        self.main_window.scene.sceneRect.return_value.width.return_value = 1000
        self.drawing.draw_grid()
        self.main_window.scene.addItem.assert_called()

    def test_draw_arrow(self):
        line = QLineF(0, 0, 100, 100)
        color = QColor(255, 0, 0)
        self.drawing.draw_arrow(line, color)
        self.main_window.scene.addItem.assert_called()

    def test_draw_arrow_horizontal_line(self):
        line = QLineF(0, 50, 100, 50)
        color = QColor(0, 255, 0)
        self.drawing.draw_arrow(line, color)
        self.main_window.scene.addItem.assert_called()

    def test_draw_arrow_vertical_line(self):
        line = QLineF(50, 0, 50, 100)
        color = QColor(0, 0, 255)
        self.drawing.draw_arrow(line, color)
        self.main_window.scene.addItem.assert_called()

    def test_draw_network_with_missing_stations(self):
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Commercial'}
        }
        self.main_window.data_manager.distances = {('1', '2'): 10.0}  # 站点2不存在
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_network_with_missing_line_stations(self):
        self.main_window.data_manager.lines = {
            '1': {'color': [255, 0, 0], 'stations': ['1', '2']}
        }
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Commercial', 'id': '1'}
            # 站点2不存在
        }
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

if __name__ == '__main__':
    unittest.main() 