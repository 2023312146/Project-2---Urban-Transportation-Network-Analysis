import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QLineF, QPointF
from PyQt5.QtGui import QColor, QPen, QFont, QPolygonF, QBrush
from project.module.drawing_module import DrawingModule
import sys

app = QApplication.instance() or QApplication(sys.argv)

class DummyMainWindow(QMainWindow):
    """Dummy main window class for testing drawing module"""
    """用于测试绘图模块的虚拟主窗口类"""
    def __init__(self):
        """Initialize dummy main window """
        """初始化虚拟主窗口"""
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
    """Test cases for drawing module functionality"""
    """绘图模块功能的测试用例"""
    def setUp(self):
        """Set up test environment with dummy main window and drawing module"""
        """设置测试环境，包含虚拟主窗口和绘图模块"""
        self.main_window = DummyMainWindow()
        self.drawing = DrawingModule(self.main_window)

    def test_init(self):
        """Test drawing module initialization"""
        """测试绘图模块初始化"""
        self.assertIs(self.drawing.main_window, self.main_window)

    @patch('project.module.drawing_module.QGraphicsScene')
    @patch('project.module.drawing_module.QPainter')
    def test_init_scene(self, mock_painter, mock_scene):
        """Test scene initialization"""
        """测试场景初始化"""
        self.drawing.init_scene()
        self.main_window.view.setScene.assert_called()
        self.main_window.view.setRenderHint.assert_called()
        self.main_window.view.setDragMode.assert_called()
        self.main_window.view.setMouseTracking.assert_called()

    def test_draw_network_empty(self):
        """Test drawing network with empty data"""
        """测试绘制空数据的网络"""
        self.main_window.data_manager.stations = {}
        self.main_window.data_manager.lines = {}
        self.main_window.data_manager.distances = {}
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_network_with_best_path(self):
        """Test drawing network with best path highlighting"""
        """测试绘制网络，包含最佳路径高亮"""
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
        """Test drawing network with metro lines"""
        """测试绘制网络，包含地铁线路"""
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
        """Test drawing network with selected start and end stations"""
        """测试绘制网络，包含选定的起始和终点站"""
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
        """Test drawing network with multiple paths and colors"""
        """测试绘制网络，包含多条路径和颜色"""
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
        """Test drawing network with mixed station type"""
        """测试绘制网络，包含混合类型站点"""
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Mixed'}
        }
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_network_industrial_station_type(self):
        """Test drawing network with industrial station type"""
        """测试绘制网络，包含工业类型站点"""
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Industrial'}
        }
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_grid(self):
        """Test drawing grid on the scene"""
        """测试在场景上绘制网格"""
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
        """Test drawing arrow on diagonal line"""
        """测试在斜线上绘制箭头"""
        line = QLineF(0, 0, 100, 100)
        color = QColor(255, 0, 0)
        self.drawing.draw_arrow(line, color)
        self.main_window.scene.addItem.assert_called()

    def test_draw_arrow_horizontal_line(self):
        """Test drawing arrow on horizontal line"""
        """测试在水平线上绘制箭头"""
        line = QLineF(0, 50, 100, 50)
        color = QColor(0, 255, 0)
        self.drawing.draw_arrow(line, color)
        self.main_window.scene.addItem.assert_called()

    def test_draw_arrow_vertical_line(self):
        """Test drawing arrow on vertical line"""
        """测试在垂直线上绘制箭头"""
        line = QLineF(50, 0, 50, 100)
        color = QColor(0, 0, 255)
        self.drawing.draw_arrow(line, color)
        self.main_window.scene.addItem.assert_called()

    def test_draw_network_with_missing_stations(self):
        """Test drawing network when some stations are missing"""
        """测试绘制网络时某些站点缺失的情况"""
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Commercial'}
        }
        self.main_window.data_manager.distances = {('1', '2'): 10.0}
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_network_with_missing_line_stations(self):
        """Test drawing network when line stations are missing"""
        """测试绘制网络时线路站点缺失的情况"""
        self.main_window.data_manager.lines = {
            '1': {'color': [255, 0, 0], 'stations': ['1', '2']}
        }
        self.main_window.data_manager.stations = {
            '1': {'x': 100, 'y': 100, 'name': 'A', 'type': 'Commercial', 'id': '1'}
        }
        self.drawing.draw_network()
        self.main_window.scene.clear.assert_called()

    def test_draw_axes(self):
        """测试经纬度坐标轴绘制"""
        # 设置场景尺寸
        self.main_window.scene.sceneRect.return_value = QRectF(0, 0, 1200, 900)
        # 模拟数据管理器（需包含_convert_geo_to_gui_coords方法）
        self.main_window.data_manager = MagicMock()
        self.main_window.data_manager._convert_geo_to_gui_coords.side_effect = lambda lat, lon: (
            80 + (lon - 2.237151)/(2.3955517-2.237151)*(1200-160),  # x坐标计算
            80 + (1 - (lat - 48.84216)/(48.891342-48.84216))*(900-160)  # y坐标计算
        )
        # 执行绘制
        self.drawing.draw_axes()
        # 验证至少添加了10个刻度标签（根据间隔计算）
        self.assertGreater(len(self.main_window.scene.addItem.call_args_list), 10)

if __name__ == '__main__':
    unittest.main()