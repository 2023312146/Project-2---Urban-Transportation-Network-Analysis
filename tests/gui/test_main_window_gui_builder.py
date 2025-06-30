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
        if hasattr(self.gui, 'selected_start'):
            delattr(self.gui, 'selected_start')
        if hasattr(self.gui, 'selected_end'):
            delattr(self.gui, 'selected_end')
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

    def test_darken_color_various_cases(self):
        gui = self.gui
        # 黑色
        self.assertEqual(gui.darken_color('#000000'), '#000000')
        # 白色
        self.assertEqual(gui.darken_color('#ffffff'), '#b2b2b2')
        # 普通色
        self.assertEqual(gui.darken_color('#123456'), '#0c243c')
        # amount=1
        self.assertEqual(gui.darken_color('#123456', 1), '#123456')
        # amount=0
        self.assertEqual(gui.darken_color('#123456', 0), '#000000')
        # amount>1
        self.assertEqual(gui.darken_color('#123456', 2), '#2468ac')
        # amount<0
        self.assertEqual(gui.darken_color('#123456', -1), '#000000')

    def test_clear_selection_no_optional_attrs(self):
        # 移除所有可選屬性
        for attr in ['shortest_path','efficiency_path','shortest_distance','efficiency_distance','efficiency_value','paths_are_same']:
            if hasattr(self.gui, attr):
                delattr(self.gui, attr)
        self.gui.info_label = MagicMock()
        self.gui.path_info = MagicMock()
        self.gui.draw_network = MagicMock()
        self.gui.clear_selection()
        self.gui.info_label.setText.assert_called()
        self.gui.path_info.setText.assert_called()
        self.gui.draw_network.assert_called()

    def test_clear_selection_with_real_label(self):
        from PyQt5.QtWidgets import QLabel
        self.gui.info_label = QLabel()
        self.gui.path_info = QLabel()
        self.gui.draw_network = MagicMock()
        self.gui.clear_selection()
        self.assertEqual(self.gui.info_label.text(), "Click to select start and end points")
        self.assertEqual(self.gui.path_info.text(), "")
        self.gui.draw_network.assert_called()

    def test_handle_station_hover_no_handler(self):
        if hasattr(self.gui, 'interaction_handler'):
            delattr(self.gui, 'interaction_handler')
        pos = MagicMock()
        with self.assertRaises(AttributeError):
            self.gui.handle_station_hover(pos)

    def test_handle_station_click_no_handler(self):
        if hasattr(self.gui, 'interaction_handler'):
            delattr(self.gui, 'interaction_handler')
        pos = MagicMock()
        with self.assertRaises(AttributeError):
            self.gui.handle_station_click(pos)

    def test_save_data_success(self):
        self.gui.data_manager.save_data_to_csv = MagicMock()
        with patch('project.gui.main_window_gui_builder.QMessageBox.information') as mock_info:
            self.gui.save_data()
            mock_info.assert_called()

    def test_save_data_exception(self):
        self.gui.data_manager.save_data_to_csv = MagicMock(side_effect=Exception("fail"))
        with patch('project.gui.main_window_gui_builder.QMessageBox.critical') as mock_critical:
            self.gui.save_data()
            mock_critical.assert_called()

if __name__ == '__main__':
    unittest.main() 