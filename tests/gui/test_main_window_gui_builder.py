import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
import sys
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtCore import QSize

app = QApplication.instance() or QApplication(sys.argv)
from project.gui.main_window_gui_builder import GUIBuilder

class TestMainWindowGuiBuilder(unittest.TestCase):
    def setUp(self):
        self.data_manager = MagicMock()
        self.path_analyzer = MagicMock()
        # patch依赖组件，避免真实UI和信号
        patcher1 = patch('project.gui.main_window_gui_builder.DataDialogs', MagicMock())
        patcher2 = patch('project.gui.main_window_gui_builder.DrawingModule', MagicMock())
        patcher3 = patch('project.gui.main_window_gui_builder.InteractionHandler', MagicMock())
        patcher4 = patch('project.gui.main_window_gui_builder.PathDisplay', MagicMock())
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        self.addCleanup(patcher4.stop)
        patcher1.start()
        patcher2.start()
        patcher3.start()
        patcher4.start()
        self.gui = GUIBuilder(self.data_manager, self.path_analyzer)

    def test_init_ui_and_properties(self):
        self.assertIsNotNone(self.gui.info_label)
        self.assertIsNotNone(self.gui.path_info)
        self.assertIsNotNone(self.gui.legend_label)
        self.assertIsNotNone(self.gui.view)
        self.assertIsNotNone(self.gui.scene)
        self.assertTrue(hasattr(self.gui, 'draw_network'))

    def test_clear_selection(self):
        self.gui.selected_start = 'A'
        self.gui.selected_end = 'B'
        self.gui.all_paths = [1]
        self.gui.best_path = [2]
        self.gui.show_only_best_path = True
        self.gui.shortest_path = [1]
        self.gui.efficiency_path = [2]
        self.gui.shortest_distance = 1.0
        self.gui.efficiency_distance = 2.0
        self.gui.efficiency_value = 3.0
        self.gui.paths_are_same = True
        self.gui.info_label = MagicMock()
        self.gui.path_info = MagicMock()
        self.gui.draw_network = MagicMock()
        self.gui.clear_selection()
        self.assertIsNone(self.gui.selected_start)
        self.assertIsNone(self.gui.selected_end)
        self.assertEqual(self.gui.all_paths, [])
        self.assertEqual(self.gui.best_path, [])
        self.assertFalse(self.gui.show_only_best_path)
        self.gui.info_label.setText.assert_called()
        self.gui.path_info.setText.assert_called()
        self.gui.draw_network.assert_called()

    def test_handle_station_hover_and_click(self):
        self.gui.interaction_handler = MagicMock()
        pos = MagicMock()
        self.gui.handle_station_hover(pos)
        self.gui.interaction_handler.handle_station_hover.assert_called_with(pos)
        self.gui.handle_station_click(pos)
        self.gui.interaction_handler.handle_station_click.assert_called_with(pos)

    def test_update_path_info(self):
        self.gui.path_display = MagicMock()
        self.gui.update_path_info()
        self.gui.path_display.update_path_info.assert_called()

    def test_resizeEvent_and_update_legend_position(self):
        event = QResizeEvent(QSize(500, 500), QSize(400, 400))
        self.gui.legend_label = MagicMock()
        self.gui.width = MagicMock(return_value=500)
        self.gui.legend_label.width = MagicMock(return_value=100)
        self.gui.legend_label.move = MagicMock()
        self.gui.resizeEvent(event)
        self.gui.legend_label.move.assert_called()
        self.gui.update_legend_position()
        self.gui.legend_label.move.assert_called()

if __name__ == '__main__':
    unittest.main() 