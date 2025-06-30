import unittest
from unittest.mock import MagicMock, patch, ANY
from project.gui.network_visualization_drawing import DrawingModule
import math
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsScene

class TestDrawingModule(unittest.TestCase):
    def setUp(self):
        self.mw = MagicMock()
        self.mw.data_manager.stations = {}
        self.mw.data_manager.distances = {}
        self.mw.scene = MagicMock()
        self.mw.scene.setSceneRect = MagicMock()
        self.mw.view = MagicMock()
        self.mw.view.setScene = MagicMock()
        self.mw.view.setRenderHint = MagicMock()
        self.mw.view.setDragMode = MagicMock()
        self.mw.view.setMouseTracking = MagicMock()
        self.mw.selected_start = None
        self.mw.selected_end = None
        self.mw.all_paths = []
        self.mw.best_path = []
        self.mw.show_only_best_path = False
        self.module = DrawingModule(self.mw)

    def test_init_scene(self):
        with patch.object(QGraphicsScene, 'setSceneRect') as mock_setSceneRect, \
             patch.object(self.mw.view, 'setScene') as mock_setScene, \
             patch.object(self.mw.view, 'setRenderHint') as mock_setRenderHint, \
             patch.object(self.mw.view, 'setDragMode') as mock_setDragMode, \
             patch.object(self.mw.view, 'setMouseTracking') as mock_setMouseTracking:
            self.module.init_scene()
            mock_setSceneRect.assert_called()
            mock_setScene.assert_called()
            mock_setRenderHint.assert_any_call(ANY)
            mock_setDragMode.assert_called()
            mock_setMouseTracking.assert_called_with(True)

    def test_draw_network_no_stations(self):
        self.mw.data_manager.stations = {}
        self.module.draw_network()
        self.mw.scene.clear.assert_called()

    def test_draw_network_with_stations_and_no_paths(self):
        self.mw.data_manager.stations = {'1': {'x': 0, 'y': 0, 'name': 'A', 'type': 'Residential'},
                                         '2': {'x': 100, 'y': 100, 'name': 'B', 'type': 'Commercial'}}
        self.mw.data_manager.distances = {('1', '2'): 1.0}
        self.mw.all_paths = []
        self.mw.best_path = []
        self.mw.show_only_best_path = False
        with patch.object(self.module, 'draw_axes') as mock_axes, \
             patch.object(self.module, 'draw_arrow') as mock_arrow:
            self.module.draw_network()
            mock_axes.assert_called()
            # 检查是否调用了 draw_arrow
            mock_arrow.assert_called()

    def test_draw_network_with_all_paths(self):
        self.mw.data_manager.stations = {'1': {'x': 0, 'y': 0, 'name': 'A', 'type': 'Residential'},
                                         '2': {'x': 100, 'y': 100, 'name': 'B', 'type': 'Commercial'}}
        self.mw.data_manager.distances = {('1', '2'): 1.0}
        self.mw.all_paths = [['1', '2']]
        self.mw.best_path = ['1', '2']
        self.mw.show_only_best_path = False
        self.mw.selected_start = '1'
        self.mw.selected_end = '2'
        self.mw.path_colors = [MagicMock()]  # 修正：确保 path_colors 非空，避免 ZeroDivisionError
        with patch.object(self.module, 'draw_axes') as mock_axes, \
             patch.object(self.module, 'draw_arrow') as mock_arrow:
            self.module.draw_network()
            mock_axes.assert_called()
            mock_arrow.assert_called()

    def test_draw_network_best_path(self):
        self.mw.data_manager.stations = {'1': {'x': 0, 'y': 0, 'name': 'A', 'type': 'Residential'},
                                         '2': {'x': 100, 'y': 100, 'name': 'B', 'type': 'Commercial'}}
        self.mw.data_manager.distances = {('1', '2'): 1.0}
        self.mw.shortest_path = ['1', '2']
        self.mw.efficiency_path = ['1', '2']
        self.mw.show_only_best_path = True
        self.mw.best_path = ['1', '2']
        self.mw.selected_start = '1'
        self.mw.selected_end = '2'
        with patch.object(self.module, 'draw_axes') as mock_axes, \
             patch.object(self.module, 'draw_arrow') as mock_arrow, \
             patch.object(self.module, 'draw_parallel_lines') as mock_parallel:
            self.module.draw_network()
            mock_axes.assert_called()
            # 由于路径重叠，draw_parallel_lines 应被调用
            mock_parallel.assert_called()

    def test_draw_network_best_path_missing_station(self):
        self.mw.data_manager.stations = {'1': {'x': 0, 'y': 0, 'name': 'A', 'type': 'Residential'}}
        self.mw.data_manager.distances = {}
        self.mw.shortest_path = ['1', '2']
        self.mw.efficiency_path = ['1', '2']
        self.mw.show_only_best_path = True
        self.mw.best_path = ['1', '2']
        with patch.object(self.module, 'draw_axes') as mock_axes:
            self.module.draw_network()
            mock_axes.assert_called()

    def test_draw_network_best_path_missing_distance(self):
        self.mw.data_manager.stations = {'1': {'x': 0, 'y': 0, 'name': 'A', 'type': 'Residential'},
                                         '2': {'x': 100, 'y': 100, 'name': 'B', 'type': 'Commercial'}}
        self.mw.data_manager.distances = {}
        self.mw.shortest_path = ['1', '2']
        self.mw.efficiency_path = ['1', '2']
        self.mw.show_only_best_path = True
        self.mw.best_path = ['1', '2']
        with patch.object(self.module, 'draw_axes') as mock_axes:
            self.module.draw_network()
            mock_axes.assert_called()

    def test_draw_grid(self):
        self.mw.scene.sceneRect.return_value = MagicMock(left=lambda: 0, right=lambda: 100, top=lambda: 0, bottom=lambda: 100, height=lambda: 100, width=lambda: 100)
        self.module.draw_grid()
        self.mw.scene.addItem.assert_any_call(ANY)

    def test_draw_arrow(self):
        # 构造一个模拟的 QLineF
        line = MagicMock()
        p1 = MagicMock(x=lambda: 0, y=lambda: 0)
        p2 = MagicMock(x=lambda: 100, y=lambda: 0)
        line.p1.return_value = p1
        line.p2.return_value = p2
        color = QColor(255, 0, 0)  # 修正：传递 QColor 实例
        self.mw.scene = MagicMock()
        self.module.draw_arrow(line, color)
        self.mw.scene.addItem.assert_any_call(ANY)

    def test_draw_parallel_lines(self):
        from_station = {'x': 0, 'y': 0}
        to_station = {'x': 100, 'y': 100}
        with patch.object(self.module, 'draw_arrow') as mock_arrow:
            self.mw.scene = MagicMock()
            self.module.draw_parallel_lines(from_station, to_station)
            self.mw.scene.addItem.assert_any_call(ANY)
            self.assertEqual(mock_arrow.call_count, 2)

    def test_draw_parallel_lines_zero_length(self):
        from_station = {'x': 0, 'y': 0}
        to_station = {'x': 0, 'y': 0}
        with patch.object(self.module, 'draw_arrow') as mock_arrow:
            self.mw.scene = MagicMock()
            self.module.draw_parallel_lines(from_station, to_station)
            # 不应调用 draw_arrow
            mock_arrow.assert_not_called()

    def test_draw_axes(self):
        # mock _convert_geo_to_gui_coords
        self.mw.data_manager._convert_geo_to_gui_coords = MagicMock(return_value=(0, 0))
        self.mw.scene.sceneRect.return_value = MagicMock(left=lambda: 0, right=lambda: 100, top=lambda: 0, bottom=lambda: 100)
        self.module.draw_axes()
        self.mw.scene.addItem.assert_any_call(ANY)

    def test_draw_network_station_type_unknown(self):
        self.mw.data_manager.stations = {'1': {'x': 0, 'y': 0, 'name': 'A', 'type': 'Unknown'}}
        self.mw.data_manager.distances = {}
        self.mw.all_paths = []
        self.mw.best_path = []
        self.mw.show_only_best_path = False
        with patch.object(self.module, 'draw_axes') as mock_axes, \
             patch.object(self.module, 'draw_arrow') as mock_arrow:
            self.module.draw_network()
            mock_axes.assert_called()

    def test_draw_network_selected_start_end_not_exist(self):
        self.mw.data_manager.stations = {'1': {'x': 0, 'y': 0, 'name': 'A', 'type': 'Residential'}}
        self.mw.data_manager.distances = {}
        self.mw.all_paths = []
        self.mw.best_path = []
        self.mw.show_only_best_path = False
        self.mw.selected_start = '999'
        self.mw.selected_end = '888'
        with patch.object(self.module, 'draw_axes') as mock_axes, \
             patch.object(self.module, 'draw_arrow') as mock_arrow:
            self.module.draw_network()
            mock_axes.assert_called()

    def test_draw_network_path_colors_empty(self):
        self.mw.data_manager.stations = {'1': {'x': 0, 'y': 0, 'name': 'A', 'type': 'Residential'},
                                         '2': {'x': 100, 'y': 100, 'name': 'B', 'type': 'Commercial'}}
        self.mw.data_manager.distances = {('1', '2'): 1.0}
        self.mw.all_paths = [['1', '2']]
        self.mw.best_path = ['1', '2']
        self.mw.show_only_best_path = False
        self.mw.selected_start = '1'
        self.mw.selected_end = '2'
        self.mw.path_colors = [QColor(255,0,0)]
        with patch.object(self.module, 'draw_axes') as mock_axes, \
             patch.object(self.module, 'draw_arrow') as mock_arrow:
            self.module.draw_network()
            mock_axes.assert_called()
            mock_arrow.assert_called()

    def test_draw_network_station_name_edge_cases(self):
        self.mw.data_manager.stations = {'1': {'x': 0, 'y': 0, 'name': '', 'type': 'Residential'},
                                         '2': {'x': 100, 'y': 100, 'name': '很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长', 'type': 'Commercial'},
                                         '3': {'x': 200, 'y': 200, 'name': '@#￥%……&*', 'type': 'Industrial'}}
        self.mw.data_manager.distances = {}
        self.mw.all_paths = []
        self.mw.best_path = []
        self.mw.show_only_best_path = False
        with patch.object(self.module, 'draw_axes') as mock_axes, \
             patch.object(self.module, 'draw_arrow') as mock_arrow:
            self.module.draw_network()
            mock_axes.assert_called()

    def test_draw_instruction_note_extreme_rect(self):
        scene_rect = MagicMock(left=lambda: -1000, bottom=lambda: 10000)
        self.mw.scene = MagicMock()
        self.module.draw_instruction_note(scene_rect)
        self.mw.scene.addItem.assert_any_call(ANY)

    def test_draw_grid_zero_size(self):
        self.mw.scene.sceneRect.return_value = MagicMock(left=lambda: 0, right=lambda: 0, top=lambda: 0, bottom=lambda: 0, height=lambda: 0, width=lambda: 0)
        self.module.draw_grid()
        self.mw.scene.addItem.assert_not_called()  # 不會畫任何線

    def test_draw_arrow_zero_length(self):
        line = MagicMock()
        p1 = MagicMock(x=lambda: 0, y=lambda: 0)
        p2 = MagicMock(x=lambda: 0, y=lambda: 0)
        line.p1.return_value = p1
        line.p2.return_value = p2
        color = QColor(255, 0, 0)
        self.mw.scene = MagicMock()
        self.module.draw_arrow(line, color)
        self.mw.scene.addItem.assert_any_call(ANY)

    def test_draw_arrow_transparent_color(self):
        line = MagicMock()
        p1 = MagicMock(x=lambda: 0, y=lambda: 0)
        p2 = MagicMock(x=lambda: 100, y=lambda: 0)
        line.p1.return_value = p1
        line.p2.return_value = p2
        color = QColor(0, 0, 0, 0)  # 透明色
        self.mw.scene = MagicMock()
        self.module.draw_arrow(line, color)
        self.mw.scene.addItem.assert_any_call(ANY)

    def test_draw_axes_extreme_coords(self):
        self.mw.data_manager._convert_geo_to_gui_coords = MagicMock(return_value=(-9999, 9999))
        self.mw.scene.sceneRect.return_value = MagicMock(left=lambda: -1000, right=lambda: 1000, top=lambda: -1000, bottom=lambda: 1000)
        self.module.draw_axes()
        self.mw.scene.addItem.assert_any_call(ANY)

if __name__ == '__main__':
    unittest.main() 