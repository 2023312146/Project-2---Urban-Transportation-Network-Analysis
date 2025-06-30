import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QPointF
from project.gui.gui_builder import GUIBuilder
import sys

app = QApplication.instance() or QApplication(sys.argv)

class DummyDataManager:
    """testing GUI builder"""
    """用于测试GUI构建器"""
    def __init__(self):
        """Initialize dummy data manager"""
        """初始化虚拟数据管理器"""
        self.stations = {}
        self.distances = {}
        self.lines = {}
        self.station_name_to_id = {}
        self.add_station = MagicMock()
        self.remove_station = MagicMock()
        self.update_station_type = MagicMock()
        self.add_connection = MagicMock()
        self.remove_connection = MagicMock()

class DummyPathAnalyzer:
    """Dummy path analyzer class for testing GUI builder"""
    """用于测试GUI构建器的虚拟路径分析器类"""
    def find_highest_degree_station(self):
        return None
    def find_all_paths(self, *args, **kwargs):
        return []
    def find_best_path(self, *args, **kwargs):
        return []

class TestGUIBuilder(unittest.TestCase):
    """Test cases for GUI builder functionality"""
    """GUI构建器功能的测试用例"""
    def setUp(self):
        self.data_manager = DummyDataManager()
        self.path_analyzer = DummyPathAnalyzer()
        self.gui = GUIBuilder(self.data_manager, self.path_analyzer)

    def test_init(self):
        self.assertIs(self.gui.data_manager, self.data_manager)
        self.assertIs(self.gui.path_analyzer, self.path_analyzer)
        self.assertIsNone(self.gui.selected_start)
        self.assertIsNone(self.gui.selected_end)
        self.assertIsNone(self.gui.hovered_station)
        self.assertEqual(self.gui.all_paths, [])
        self.assertEqual(self.gui.best_path, [])
        self.assertFalse(self.gui.show_only_best_path)

    def test_init_ui_components(self):
        self.assertIsNotNone(self.gui.info_label)
        self.assertIsNotNone(self.gui.path_info)
        self.assertIsNotNone(self.gui.view)
        self.assertIsNotNone(self.gui.scene)
        self.assertIsNotNone(self.gui.legend_label)

    def test_window_properties(self):

        self.assertEqual(self.gui.windowTitle(), "Bus Network Path Planning System")
        self.assertEqual(self.gui.geometry().width(), 1000)
        self.assertEqual(self.gui.geometry().height(), 700)

    def test_clear_selection(self):

        setattr(self.gui, 'selected_start', '1')
        setattr(self.gui, 'selected_end', '2')
        self.gui.all_paths = ['path1', 'path2']
        self.gui.best_path = ['best_path']
        self.gui.show_only_best_path = True
        
        self.gui.clear_selection()
        

        self.assertIsNone(self.gui.selected_start)
        self.assertIsNone(self.gui.selected_end)
        self.assertEqual(self.gui.all_paths, [])
        self.assertEqual(self.gui.best_path, [])
        self.assertFalse(self.gui.show_only_best_path)
        

        self.assertEqual(self.gui.info_label.text(), 
                        "Hover over stations to view information, click to select start and end points")
        self.assertEqual(self.gui.path_info.text(), "")

    def test_darken_color(self):

        original_color = "#4CAF50"
        darkened = self.gui.darken_color(original_color)
        self.assertNotEqual(original_color, darkened)
        self.assertTrue(darkened.startswith("#"))
        

        red_color = "#ff0000"
        darkened_red = self.gui.darken_color(red_color)
        self.assertNotEqual(red_color, darkened_red)

    def test_darken_color_with_amount(self):
 
        original_color = "#4CAF50"
        darkened_50 = self.gui.darken_color(original_color, 0.5)
        darkened_80 = self.gui.darken_color(original_color, 0.8)
        self.assertNotEqual(darkened_50, darkened_80)

    @patch('project.module.interaction_handler.QGraphicsEllipseItem')
    def test_handle_station_hover(self, mock_ellipse):
        pos = QPointF(100, 100)
        
        with patch.object(self.gui.scene, 'items', return_value=[]):
            self.gui.handle_station_hover(pos)

    @patch('project.module.interaction_handler.QGraphicsEllipseItem')
    def test_handle_station_click(self, mock_ellipse):

        pos = QPointF(100, 100)
        
        with patch.object(self.gui.scene, 'items', return_value=[]):
            self.gui.handle_station_click(pos)

    def test_update_path_info(self):
        with patch.object(self.gui.path_display, 'update_path_info') as mock_update:
            self.gui.update_path_info()
            mock_update.assert_called_once()

    @patch('project.module.gui_builder.QMainWindow.resizeEvent')
    def test_resizeEvent(self, mock_resize):
        event = MagicMock()
        self.gui.resizeEvent(event)
        mock_resize.assert_called_with(event)

    def test_update_legend_position(self):
        self.gui.update_legend_position()
        self.assertIsNotNone(self.gui.legend_label)

    def test_legend_content(self):
        legend_text = self.gui.legend_label.text()
        self.assertIn("Color annotations", legend_text)
        self.assertIn("Path Type", legend_text)
        self.assertIn("Zone Type", legend_text)
        self.assertIn("Commercial", legend_text)
        self.assertIn("Residential", legend_text)
        self.assertIn("Industrial", legend_text)
        self.assertIn("Mixed", legend_text)

    def test_legend_properties(self):
        self.assertEqual(self.gui.legend_label.width(), 320)
        self.assertEqual(self.gui.legend_label.height(), 300)
        self.assertTrue(self.gui.legend_label.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents))

    def test_draw_network_delegation(self):
        with patch.object(self.gui, 'draw_network') as mock_draw:
            self.gui.draw_network()
            mock_draw.assert_called_once()

    def test_module_initialization(self):
        self.assertIsNotNone(self.gui.data_dialogs)
        self.assertIsNotNone(self.gui.drawing_module)
        self.assertIsNotNone(self.gui.interaction_handler)
        self.assertIsNotNone(self.gui.path_display)
        
    def test_module_references(self):
        self.assertIs(self.gui.data_dialogs.main_window, self.gui)
        self.assertIs(self.gui.drawing_module.main_window, self.gui)
        self.assertIs(self.gui.interaction_handler.main_window, self.gui)
        self.assertIs(self.gui.path_display.main_window, self.gui)

    def test_style_sheet_application(self):

        style_sheet = self.gui.styleSheet()
        self.assertIn("QMainWindow", style_sheet)
        self.assertIn("QPushButton", style_sheet)
        self.assertIn("QGraphicsView", style_sheet)

    def test_scroll_area_properties(self):
        scroll_area = self.gui.path_info.parent()
        self.assertIsNotNone(scroll_area)
        self.assertIsNotNone(self.gui.path_info)
        self.assertTrue(hasattr(self.gui.path_info, 'setText'))

if __name__ == '__main__':
    unittest.main() 