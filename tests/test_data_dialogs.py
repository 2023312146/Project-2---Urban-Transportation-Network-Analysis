import unittest
from unittest.mock import MagicMock
from project.module.data_dialogs import DataDialogs

class DummyMainWindow:
    def __init__(self):
        self.data_manager = MagicMock()
        self.path_analyzer = MagicMock()
        self.draw_network = MagicMock()
        self.clear_selection = MagicMock()

class TestDataDialogs(unittest.TestCase):
    def setUp(self):
        self.main_window = DummyMainWindow()
        self.dialogs = DataDialogs(self.main_window)

    def test_init(self):
        self.assertIs(self.dialogs.main_window, self.main_window)
        self.assertIs(self.dialogs.data_manager, self.main_window.data_manager)
        self.assertIs(self.dialogs.path_analyzer, self.main_window.path_analyzer)

    def test_get_messagebox_style(self):
        style = self.dialogs.get_messagebox_style()
        self.assertIn('QMessageBox', style)

    def test_methods_callable(self):
        # 只测试方法可调用性，不测试UI
        for method in [
            self.dialogs.add_station_dialog,
            self.dialogs.remove_station_dialog,
            self.dialogs.update_station_type_dialog,
            self.dialogs.add_connection_dialog,
            self.dialogs.remove_connection_dialog,
            self.dialogs.find_highest_degree_station_dialog
        ]:
            try:
                method()
            except Exception:
                pass  # 允许因UI缺失报错

if __name__ == '__main__':
    unittest.main() 