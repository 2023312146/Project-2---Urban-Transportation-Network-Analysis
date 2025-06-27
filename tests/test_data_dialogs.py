import unittest
from unittest.mock import MagicMock, patch
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

    @patch('project.module.data_dialogs.QInputDialog')
    def test_add_station_dialog(self, mock_input):
        # 模拟所有输入都点击OK
        mock_input.getText.return_value = ("StationA", True)
        mock_input.getInt.side_effect = [(100, True), (200, True), (5, True)]
        mock_input.getItem.return_value = ("Residential", True)
        self.dialogs.add_station_dialog()
        self.main_window.data_manager.add_station.assert_called()
        self.main_window.draw_network.assert_called()

    @patch('project.module.data_dialogs.QInputDialog')
    @patch('project.module.data_dialogs.QMessageBox')
    def test_remove_station_dialog_empty(self, mock_msgbox, mock_input):
        self.main_window.data_manager.stations = {}
        self.dialogs.remove_station_dialog()
        mock_msgbox().warning.assert_called()

    @patch('project.module.data_dialogs.QInputDialog')
    def test_remove_station_dialog(self, mock_input):
        self.main_window.data_manager.stations = {1: {'name': 'A'}}
        mock_input.getItem.return_value = ("A", True)
        self.dialogs.remove_station_dialog()
        self.main_window.data_manager.remove_station.assert_called()
        self.main_window.clear_selection.assert_called()
        self.main_window.draw_network.assert_called()

    @patch('project.module.data_dialogs.QInputDialog')
    @patch('project.module.data_dialogs.QMessageBox')
    def test_update_station_type_dialog_empty(self, mock_msgbox, mock_input):
        self.main_window.data_manager.stations = {}
        self.dialogs.update_station_type_dialog()
        mock_msgbox.warning.assert_called()

    @patch('project.module.data_dialogs.QInputDialog')
    def test_update_station_type_dialog(self, mock_input):
        self.main_window.data_manager.stations = {1: {'name': 'A'}}
        mock_input.getItem.side_effect = [("A", True), ("Commercial", True)]
        self.dialogs.update_station_type_dialog()
        self.main_window.data_manager.update_station_type.assert_called()
        self.main_window.draw_network.assert_called()

    @patch('project.module.data_dialogs.QInputDialog')
    @patch('project.module.data_dialogs.QMessageBox')
    def test_add_connection_dialog_too_few(self, mock_msgbox, mock_input):
        self.main_window.data_manager.stations = {1: {'name': 'A'}}
        self.dialogs.add_connection_dialog()
        mock_msgbox.warning.assert_called()

    @patch('project.module.data_dialogs.QInputDialog')
    @patch('project.module.data_dialogs.QMessageBox')
    def test_add_connection_dialog_exists(self, mock_msgbox, mock_input):
        self.main_window.data_manager.stations = {1: {'name': 'A'}, 2: {'name': 'B'}}
        self.main_window.data_manager.station_name_to_id = {'A': 1, 'B': 2}
        self.main_window.data_manager.distances = {(1, 2): 10}
        mock_input.getItem.side_effect = [("A", True), ("B", True)]
        self.dialogs.add_connection_dialog()
        mock_msgbox.warning.assert_called()

    @patch('project.module.data_dialogs.QInputDialog')
    def test_add_connection_dialog_success(self, mock_input):
        self.main_window.data_manager.stations = {1: {'name': 'A'}, 2: {'name': 'B'}}
        self.main_window.data_manager.station_name_to_id = {'A': 1, 'B': 2}
        self.main_window.data_manager.distances = {}
        mock_input.getItem.side_effect = [("A", True), ("B", True)]
        mock_input.getDouble.return_value = (10.0, True)
        self.dialogs.add_connection_dialog()
        self.main_window.data_manager.add_connection.assert_called()
        self.main_window.draw_network.assert_called()

    @patch('project.module.data_dialogs.QInputDialog')
    @patch('project.module.data_dialogs.QMessageBox')
    def test_remove_connection_dialog_empty(self, mock_msgbox, mock_input):
        self.main_window.data_manager.distances = {}
        self.dialogs.remove_connection_dialog()
        mock_msgbox.warning.assert_called()

    @patch('project.module.data_dialogs.QInputDialog')
    @patch('project.module.data_dialogs.QMessageBox')
    def test_remove_connection_dialog_no_exit(self, mock_msgbox, mock_input):
        self.main_window.data_manager.distances = {(1, 2): 10}
        self.main_window.data_manager.station_name_to_id = {'A': 1, 'B': 2}
        self.main_window.data_manager.stations = {1: {'name': 'A'}, 2: {'name': 'B'}}
        mock_input.getItem.return_value = ("A", True)
        # 让A没有出边 - 修改distances，让A没有出边连接
        self.main_window.data_manager.distances = {(2, 1): 10}  # 只有B到A的连接，A没有出边
        self.dialogs.remove_connection_dialog()
        mock_msgbox.warning.assert_called()

    @patch('project.module.data_dialogs.QInputDialog')
    def test_remove_connection_dialog_success(self, mock_input):
        self.main_window.data_manager.distances = {(1, 2): 10}
        self.main_window.data_manager.station_name_to_id = {'A': 1, 'B': 2}
        self.main_window.data_manager.stations = {1: {'name': 'A'}, 2: {'name': 'B'}}
        mock_input.getItem.side_effect = [("A", True), ("B", True)]
        self.dialogs.remove_connection_dialog()
        self.main_window.data_manager.remove_connection.assert_called()
        self.main_window.draw_network.assert_called()

    @patch('project.module.data_dialogs.QMessageBox')
    def test_find_highest_degree_station_dialog(self, mock_msgbox):
        self.main_window.path_analyzer.find_highest_degree_station.return_value = 1
        self.main_window.data_manager.stations = {
            1: {'name': 'A', 'connections': [2]},
            2: {'name': 'B', 'connections': []}
        }
        self.dialogs.find_highest_degree_station_dialog()
        mock_msgbox().setText.assert_called()

if __name__ == '__main__':
    unittest.main() 