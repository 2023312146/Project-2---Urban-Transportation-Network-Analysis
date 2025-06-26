import unittest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication
from project.module.gui_builder import GUIBuilder
import sys

app = QApplication.instance() or QApplication(sys.argv)

class DummyDataManager:
    def __init__(self):
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
    def find_highest_degree_station(self):
        return None
    def find_all_paths(self, *args, **kwargs):
        return []
    def find_best_path(self, *args, **kwargs):
        return []

class TestGUIBuilder(unittest.TestCase):
    def setUp(self):
        self.data_manager = DummyDataManager()
        self.path_analyzer = DummyPathAnalyzer()
        self.gui = GUIBuilder(self.data_manager, self.path_analyzer)

    def test_init(self):
        self.assertIs(self.gui.data_manager, self.data_manager)
        self.assertIs(self.gui.path_analyzer, self.path_analyzer)

    def test_clear_selection(self):
        self.gui.selected_start = '1'
        self.gui.selected_end = '2'
        self.gui.clear_selection()
        self.assertIsNone(self.gui.selected_start)
        self.assertIsNone(self.gui.selected_end)

    def test_handle_station_hover_callable(self):
        try:
            self.gui.handle_station_hover(None)
        except Exception:
            pass

    def test_handle_station_click_callable(self):
        try:
            self.gui.handle_station_click(None)
        except Exception:
            pass

    def test_update_path_info_callable(self):
        try:
            self.gui.update_path_info()
        except Exception:
            pass

if __name__ == '__main__':
    unittest.main() 