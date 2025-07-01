from PyQt5.QtWidgets import QInputDialog, QMessageBox, QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox, QLineEdit, QHBoxLayout
from PyQt5.QtCore import Qt
from project.algorithms.distance_calculation import calculate_distance_between_stops_by_id

class DataDialogs:
    def __init__(self, main_window):
        self.main_window = main_window
        self.data_manager = main_window.data_manager
        self.path_analyzer = main_window.path_analyzer
        self.selected_from_station = None  # 用于存储添加/删除连接时选中的起始站点
        self.connection_mode = None  # 'add' 或 'remove' 表示当前连接操作模式

    def add_station_dialog(self):
        """添加站点对话框，现在支持直接点击添加"""
        # 启用添加站点模式
        self.main_window.interaction_handler.add_station_mode = True
        
        # 确保使用十字形鼠标
        self.main_window.view.setCursor(Qt.CrossCursor)

    def remove_station_dialog(self):
        """删除站点对话框，现在支持直接点击删除"""
        if not self.data_manager.stations:
            return
        
        # 启用删除站点模式
        self.main_window.interaction_handler.remove_station_mode = True
        
        # 设置禁止光标（表示删除）
        self.main_window.view.setCursor(Qt.ForbiddenCursor)

    def update_station_type_dialog(self):
        if not self.data_manager.stations:
            return
        station_names = {v['name']: k for k, v in self.data_manager.stations.items()}
        station_name, ok = QInputDialog.getItem(self.main_window, "Update station type", "Select a stop:", list(station_names.keys()))
        if ok and station_name:
            station_type, ok = QInputDialog.getItem(self.main_window, "Update station type", "Stop type:", ["Residential", "Commercial", "Mixed", "Industrial"])
            if ok:
                self.data_manager.update_station_type(station_name, station_type)
                self.main_window.draw_network()

    def add_connection_dialog(self):
        """添加连接，直接进入点击选择站点模式"""
        if len(self.data_manager.stations) < 2:
            return
        
        # 直接启动连接点击模式
        self.start_connection_click_mode('add')
        
        # 使用手型光标表示连接操作
        self.main_window.view.setCursor(Qt.PointingHandCursor)

    def remove_connection_dialog(self):
        """删除连接，使用点击选择站点模式"""
        if len(self.data_manager.distances) == 0:
            return
        
        # 启动连接点击模式，但用于删除
        self.start_connection_click_mode('remove')
        
        # 使用禁止光标表示删除操作
        self.main_window.view.setCursor(Qt.ForbiddenCursor)

    def start_connection_click_mode(self, mode='add'):
        self.selected_from_station = None
        self.connection_mode = mode
        
        # 保存原来的点击处理函数
        self.original_click_handler = self.main_window.handle_station_click
        
        # 重写点击处理函数
        def connection_click_handler(pos):
            items = self.main_window.scene.items(pos)
            for item in items:
                if hasattr(item, 'data') and callable(item.data):
                    station_id = item.data(0)
                    if station_id:
                        if self.selected_from_station is None:
                            # 选择第一个站点
                            self.selected_from_station = station_id
                        else:
                            # 选择第二个站点
                            to_station_id = station_id
                            if to_station_id == self.selected_from_station:
                                return
                                
                            from_name = self.data_manager.stations[self.selected_from_station]['name']
                            to_name = self.data_manager.stations[to_station_id]['name']
                            
                            if self.connection_mode == 'add':
                                # 检查连接是否已存在
                                if (self.selected_from_station, to_station_id) in self.data_manager.distances:
                                    return
                                    
                                # 直接计算距离并添加连接
                                distance = calculate_distance_between_stops_by_id(self.data_manager, self.selected_from_station, to_station_id)
                                self.data_manager.add_connection(from_name, to_name, distance)
                            else:  # self.connection_mode == 'remove'
                                # 检查连接是否存在
                                if (self.selected_from_station, to_station_id) not in self.data_manager.distances:
                                    return
                                
                                # 直接删除连接
                                self.data_manager.remove_connection(from_name, to_name)
                            
                            # 恢复原始点击处理函数
                            self.main_window.handle_station_click = self.original_click_handler
                            
                            # 清除状态并刷新
                            self.selected_from_station = None
                            self.connection_mode = None
                            
                            # 恢复鼠标样式
                            self.main_window.view.setCursor(Qt.ArrowCursor)
                            
                            # 重绘网络
                            self.main_window.draw_network()
                            
                        return
                
        # 设置临时点击处理函数
        self.main_window.handle_station_click = connection_click_handler

    def find_highest_degree_station_dialog(self):
        highest_degree_station_id = self.path_analyzer.find_highest_degree_station()
        msg = QMessageBox()
        msg.setStyleSheet(self.get_messagebox_style())
        if highest_degree_station_id:
            station = self.data_manager.stations[highest_degree_station_id]
            out_degree = len(station['connections'])
            in_degree = 0
            for s in self.data_manager.stations.values():
                if highest_degree_station_id in s['connections']:
                    in_degree += 1
            total_degree = in_degree + out_degree
            msg.setWindowTitle("Highest Degree Station")
            msg.setText(f"<b>{station['name']}</b><br>Degree (in+out): {total_degree} (in: {in_degree}, out: {out_degree})")
        else:
            msg.setWindowTitle("Highest Degree Station")
            msg.setText("No stations available")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def get_messagebox_style(self):
        return """
            QMessageBox {
                font-size: 14px;
            }
            QLabel {
                font-size: 16px;
                min-width: 300px;
            }
            QPushButton {
                min-width: 80px;
                font-size: 14px;
                padding: 5px;
            }
        """