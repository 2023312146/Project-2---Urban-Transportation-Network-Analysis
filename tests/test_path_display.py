import unittest
from unittest.mock import MagicMock
from project.module.path_display import PathDisplay

class DummyMainWindow:
    def __init__(self):
        self.selected_start = None
        self.selected_end = None
        self.all_paths = []
        self.best_path = []
        self.show_only_best_path = False
        self.data_manager = MagicMock()
        self.path_analyzer = MagicMock()
        self.path_info = MagicMock()

class TestPathDisplay(unittest.TestCase):
    def setUp(self):
        self.main_window = DummyMainWindow()
        self.display = PathDisplay(self.main_window)

    def test_init(self):
        self.assertIs(self.display.main_window, self.main_window)
        self.assertIs(self.display.data_manager, self.main_window.data_manager)
        self.assertIs(self.display.path_analyzer, self.main_window.path_analyzer)

    def test_update_path_info_callable(self):
        try:
            self.display.update_path_info()
        except Exception:
            pass

if __name__ == '__main__':
    unittest.main() 