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

    def test_on_traffic_period_changed_with_selection(self):
        """測試交通時段改變時有起終點選擇的情況"""
        self.gui.selected_start = MagicMock()
        self.gui.selected_end = MagicMock()
        self.gui.update_path_info = MagicMock()
        self.gui.draw_network = MagicMock()
        
        self.gui.on_traffic_period_changed("Morning rush hour")
        
        self.gui.update_path_info.assert_called_once()
        self.gui.draw_network.assert_called_once()

    def test_on_traffic_period_changed_without_selection(self):
        """測試交通時段改變時沒有起終點選擇的情況"""
        self.gui.selected_start = None
        self.gui.selected_end = None
        self.gui.update_path_info = MagicMock()
        self.gui.draw_network = MagicMock()
        
        self.gui.on_traffic_period_changed("Evening rush hour")
        
        self.gui.update_path_info.assert_not_called()
        self.gui.draw_network.assert_called_once()

    def test_show_stop_utilization_analysis(self):
        """測試顯示站點利用率分析"""
        with patch('project.gui.main_window_gui_builder.StopUtilizationAnalyzer') as mock_analyzer_class:
            with patch('project.gui.main_window_gui_builder.StopUtilizationDisplay') as mock_dialog_class:
                mock_analyzer = MagicMock()
                mock_analyzer_class.return_value = mock_analyzer
                mock_dialog = MagicMock()
                mock_dialog_class.return_value = mock_dialog
                
                self.gui.show_stop_utilization_analysis()
                
                mock_analyzer_class.assert_called_once_with(self.gui.data_manager)
                mock_analyzer.generate_random_data.assert_called_once()
                mock_dialog_class.assert_called_once_with(mock_analyzer, self.gui)
                mock_dialog.remove_stop_signal.connect.assert_called_once_with(self.gui.remove_stop_by_id)
                mock_dialog.add_stop_signal.connect.assert_called_once_with(self.gui.add_stop_at_location)
                mock_dialog.exec_.assert_called_once()

    def test_remove_stop_by_id_success(self):
        """測試成功刪除站點"""
        mock_stop = MagicMock()
        mock_stop.name = "Test Stop"
        self.gui.data_manager.network.get_stop_by_id.return_value = mock_stop
        self.gui.data_manager.remove_station = MagicMock()
        self.gui.draw_network = MagicMock()
        
        self.gui.remove_stop_by_id("1")
        
        self.gui.data_manager.network.get_stop_by_id.assert_called_once_with("1")
        self.gui.data_manager.remove_station.assert_called_once_with("Test Stop")
        self.gui.draw_network.assert_called_once()

    def test_remove_stop_by_id_not_found(self):
        """測試刪除不存在的站點"""
        self.gui.data_manager.network.get_stop_by_id.return_value = None
        self.gui.data_manager.remove_station = MagicMock()
        self.gui.draw_network = MagicMock()
        
        self.gui.remove_stop_by_id("999")
        
        self.gui.data_manager.remove_station.assert_not_called()
        self.gui.draw_network.assert_not_called()

    def test_remove_stop_by_id_exception(self):
        """測試刪除站點時發生異常"""
        mock_stop = MagicMock()
        mock_stop.name = "Test Stop"
        self.gui.data_manager.network.get_stop_by_id.return_value = mock_stop
        self.gui.data_manager.remove_station = MagicMock(side_effect=Exception("Delete failed"))
        
        with patch('project.gui.main_window_gui_builder.QMessageBox.warning') as mock_warning:
            self.gui.remove_stop_by_id("1")
            mock_warning.assert_called_once()

    def test_add_stop_at_location_success(self):
        """測試成功添加站點"""
        with patch('project.gui.main_window_gui_builder.CoordinateUtils') as mock_coord_utils:
            mock_coord_utils.calculate_haversine_distance.return_value = 1.5
            
            self.gui.data_manager._convert_geo_to_gui_coords.return_value = (100, 200)
            self.gui.data_manager.add_station = MagicMock()
            self.gui.data_manager.station_name_to_id = {"Existing Stop": "1"}
            self.gui.data_manager.add_connection = MagicMock()
            self.gui.drawing_module.init_scene = MagicMock()
            self.gui.draw_network = MagicMock()
            
            # 模擬連接站點
            mock_connect_stop = MagicMock()
            mock_connect_stop.latitude = 30.1
            mock_connect_stop.longitude = 120.1
            self.gui.data_manager.network.get_stop_by_id.return_value = mock_connect_stop
            
            self.gui.add_stop_at_location(30.0, 120.0, "New Stop", ["Existing Stop"])
            
            self.gui.data_manager._convert_geo_to_gui_coords.assert_called_once_with(30.0, 120.0)
            self.gui.data_manager.add_station.assert_called_once_with("New Stop", 100, 200, "Mixed")
            self.gui.data_manager.add_connection.assert_called()
            self.gui.drawing_module.init_scene.assert_called_once()
            self.gui.draw_network.assert_called_once()

    def test_add_stop_at_location_no_connections(self):
        """測試添加站點但不連接其他站點"""
        self.gui.data_manager._convert_geo_to_gui_coords.return_value = (100, 200)
        self.gui.data_manager.add_station = MagicMock()
        self.gui.drawing_module.init_scene = MagicMock()
        self.gui.draw_network = MagicMock()
        
        self.gui.add_stop_at_location(30.0, 120.0, "New Stop")
        
        self.gui.data_manager.add_station.assert_called_once_with("New Stop", 100, 200, "Mixed")
        self.gui.drawing_module.init_scene.assert_called_once()
        self.gui.draw_network.assert_called_once()

    def test_add_stop_at_location_connection_error(self):
        """測試添加站點時連接錯誤"""
        with patch('project.gui.main_window_gui_builder.CoordinateUtils') as mock_coord_utils:
            mock_coord_utils.calculate_haversine_distance.return_value = 1.5
            
            self.gui.data_manager._convert_geo_to_gui_coords.return_value = (100, 200)
            self.gui.data_manager.add_station = MagicMock()
            self.gui.data_manager.station_name_to_id = {"Existing Stop": "1"}
            self.gui.data_manager.add_connection = MagicMock(side_effect=Exception("Connection failed"))
            self.gui.drawing_module.init_scene = MagicMock()
            self.gui.draw_network = MagicMock()
            
            # 模擬連接站點
            mock_connect_stop = MagicMock()
            mock_connect_stop.latitude = 30.1
            mock_connect_stop.longitude = 120.1
            self.gui.data_manager.network.get_stop_by_id.return_value = mock_connect_stop
            
            self.gui.add_stop_at_location(30.0, 120.0, "New Stop", ["Existing Stop"])
            
            # 即使連接失敗，站點仍應該被添加
            self.gui.data_manager.add_station.assert_called_once()
            self.gui.drawing_module.init_scene.assert_called_once()
            self.gui.draw_network.assert_called_once()

    def test_add_stop_at_location_exception(self):
        """測試添加站點時發生異常"""
        self.gui.data_manager._convert_geo_to_gui_coords = MagicMock(side_effect=Exception("Conversion failed"))
        
        with patch('project.gui.main_window_gui_builder.QMessageBox.warning') as mock_warning:
            self.gui.add_stop_at_location(30.0, 120.0, "New Stop")
            mock_warning.assert_called_once()

    def test_calculate_distance(self):
        """測試距離計算"""
        with patch('project.gui.main_window_gui_builder.CoordinateUtils') as mock_coord_utils:
            mock_coord_utils.calculate_haversine_distance.return_value = 2.5
            
            result = self.gui._calculate_distance(30.0, 120.0, 30.1, 120.1)
            
            mock_coord_utils.calculate_haversine_distance.assert_called_once_with(30.0, 120.0, 30.1, 120.1)
            self.assertEqual(result, 2.5)

    def test_legend_label_properties(self):
        """測試圖例標籤屬性"""
        self.assertIsNotNone(self.gui.legend_label)
        self.assertEqual(self.gui.legend_label.width(), 320)
        self.assertEqual(self.gui.legend_label.height(), 300)
        self.assertIn("Color annotations", self.gui.legend_label.text())

    def test_legend_position_update(self):
        """測試圖例位置更新"""
        self.gui.width = MagicMock(return_value=1000)
        self.gui.legend_label.width = MagicMock(return_value=320)
        self.gui.legend_label.move = MagicMock()
        
        self.gui.update_legend_position()
        
        # 驗證位置計算：x = 1000 - 320 - 20 = 660, y = 20
        self.gui.legend_label.move.assert_called_once_with(660, 20)

if __name__ == '__main__':
    unittest.main() 