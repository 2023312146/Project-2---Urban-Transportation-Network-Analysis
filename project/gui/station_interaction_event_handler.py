from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtWidgets import (QGraphicsEllipseItem, QInputDialog, QDialog, QVBoxLayout, 
                          QLabel, QComboBox, QDialogButtonBox, QLineEdit)
from project.algorithms.distance_calculation import calculate_distance_between_stops_by_id

class InteractionHandler:
    def __init__(self, main_window):
        self.main_window = main_window  
        self.data_manager = main_window.data_manager 
        self.add_station_mode = False 
        self.remove_station_mode = False 
        self.hover_area_padding = 10.0  

    def handle_station_hover(self, pos: QPointF):
        # 如果已经有悬停的站点，优先检查这个站点是否仍在悬停区域内
        if self.main_window.hovered_station:
            station_id = self.main_window.hovered_station
            # 确保station_id存在于stations字典中
            if station_id not in self.data_manager.stations:
                self.main_window.hovered_station = None
                return None
                
            station = self.data_manager.stations[station_id]
            # 获取站点图形项的边界矩形
            size = 20 if station["type"] != "Mixed" else 25
            item_rect = QRectF(
                station["x"] - size/2 - self.hover_area_padding,
                station["y"] - size/2 - self.hover_area_padding,
                size + 2 * self.hover_area_padding,
                size + 2 * self.hover_area_padding
            )
            # 如果鼠标仍在扩大的边界矩形内，继续使用当前悬停的站点
            if item_rect.contains(pos):
                # 仍在同一站点内，返回缓存的提示信息
                tooltip_info = self._get_station_tooltip(station_id)
                return tooltip_info

        # 查找鼠标下方的站点
        items = self.main_window.scene.items(pos)
        for item in items:
            if isinstance(item, QGraphicsEllipseItem):
                station_id = item.data(0)
                if station_id and station_id in self.data_manager.stations:
                    # 扩大检测区域
                    station = self.data_manager.stations[station_id]
                    size = 20 if station["type"] != "Mixed" else 25
                    item_rect = QRectF(
                        station["x"] - size/2 - self.hover_area_padding,
                        station["y"] - size/2 - self.hover_area_padding,
                        size + 2 * self.hover_area_padding,
                        size + 2 * self.hover_area_padding
                    )
                    
                    # 如果鼠标在扩大的检测区域内
                    if item_rect.contains(pos):
                        self.main_window.hovered_station = station_id
                        tooltip_info = self._get_station_tooltip(station_id)
                        return tooltip_info
        if self.main_window.hovered_station:
            self.main_window.hovered_station = None
            
        return None
        
    def _get_station_tooltip(self, station_id):
        """获取站点的工具提示信息"""
        # 确保station_id存在于stations字典中
        if station_id not in self.data_manager.stations:
            return None
            
        station = self.data_manager.stations[station_id]
        
        # 获取站点的地理坐标（经纬度）
        stop_obj = self.data_manager.get_stop_by_id(station_id)
        lat = lon = "未知"
        if stop_obj:
            lat = stop_obj.latitude
            lon = stop_obj.longitude
        
        # 收集连接信息(仅用于工具提示，不再更新左上角面板)
        conn_info = []
        for conn_id in station["connections"]:
            conn_station = self.data_manager.stations[conn_id]
            distance = self.data_manager.distances.get((station_id, conn_id), 0)
            conn_info.append(f"{conn_station['name']}: {distance:.2f}km")
        
        # 收集出站连接信息(Out)
        outgoing_connections = []
        for conn_id in station["connections"]:
            conn_station = self.data_manager.stations[conn_id]
            distance = self.data_manager.distances.get((station_id, conn_id), 0)
            outgoing_connections.append(f"{conn_station['name']} ({distance:.1f}km)")
            
        # 收集入站连接信息(In)
        incoming_connections = []
        for other_id, other_station in self.data_manager.stations.items():
            if station_id in other_station["connections"]:
                distance = self.data_manager.distances.get((other_id, station_id), 0)
                incoming_connections.append(f"{other_station['name']} ({distance:.1f}km)")
        
        # 格式化连接信息
        connections_text = ""
        if outgoing_connections:
            connections_text += "Outgoing Connections:\n"
            connections_text += " • " + "\n • ".join(outgoing_connections) + "\n"
        if incoming_connections:
            connections_text += "Incoming Connections:\n"
            connections_text += " • " + "\n • ".join(incoming_connections)
        
        # 格式化坐标，处理未知情况
        coord_text = f"({lat}, {lon})"
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            coord_text = f"({lat:.6f}, {lon:.6f})"

        # 返回悬停提示信息，添加连接信息
        tooltip_info = (f"Stop: {station['name']}\n"
                        f"Type: {station['type']}\n"
                        f"Wait time: {station['wait_time']} minutes\n"
                       f"Coordinates: {coord_text}\n\n"
                       f"{connections_text}")
        return tooltip_info

    def handle_station_click(self, pos: QPointF):
        # 处理添加站点模式
        if self.add_station_mode:
            self.add_station_at_position(pos)
            return
            
        # 处理删除站点模式
        if self.remove_station_mode:
            self.remove_station_at_position(pos)
            return
            
        # 原有的站点选择逻辑
        items = self.main_window.scene.items(pos)
        for item in items:
            if isinstance(item, QGraphicsEllipseItem):
                station_id = item.data(0)
                if station_id:
                    station_name = self.data_manager.stations[station_id]['name']
                    if self.main_window.selected_start is None:
                        self.main_window.selected_start = station_id
                        self.main_window.info_label.setText(f"Start point selected: {station_name}\nPlease click to select end point")
                    elif self.main_window.selected_end is None and station_id != self.main_window.selected_start:
                        self.main_window.selected_end = station_id
                        self.main_window.update_path_info()
                    else:
                        self.main_window.selected_start = station_id
                        self.main_window.selected_end = None
                        self.main_window.info_label.setText(f"Start point selected: {station_name}\nPlease click to select end point")
                        self.main_window.path_info.setText("")
                    self.main_window.draw_network()
                    break
                    
    def add_station_at_position(self, pos: QPointF):
        print('進入 add_station_at_position')
        print('data_manager id (主程式):', id(self.data_manager))
        # 將場景坐標轉換為GUI坐標
        x, y = pos.x(), pos.y()
        
        # 打開名稱輸入對話框
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Add New Station")
        dialog.setMinimumWidth(300)
        
        # 創建佈局
        layout = QVBoxLayout(dialog)
        
        # 添加名稱輸入
        layout.addWidget(QLabel("Station Name:"))
        default_name = f"Station_{len(self.data_manager.stations) + 1}"
        name_edit = QLineEdit(default_name)
        layout.addWidget(name_edit)
        
        # 添加站點類型選擇（保留）
        layout.addWidget(QLabel("Zone Type:"))
        type_combo = QComboBox()
        type_combo.addItems(["Residential", "Commercial", "Industrial", "Mixed"])
        type_combo.setCurrentText("Residential")  # 默認選擇Residential
        layout.addWidget(type_combo)
        
        # 移除原有的等待時間輸入控件（關鍵修改點）
        
        # 添加按鈕
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # 顯示對話框並等待結果
        result = dialog.exec_()
        print('dialog.exec_() 回傳:', result)
        if result == QDialog.Accepted:
            print('Dialog accepted')
            station_name = name_edit.text()
            print('station_name:', station_name)
            if not station_name:
                station_name = default_name  # 如果沒有輸入名稱，使用默認名稱
                print('使用默認名稱:', station_name)
            
            station_type = type_combo.currentText()
            print('station_type:', station_type)
            
            # 自動根據區域類型獲取等待時間（通過NetworkDataManager的內部映射）
            zone_type = self.data_manager._convert_string_to_zone_type(station_type)
            print('zone_type:', zone_type)
            wait_time = self.data_manager._get_wait_time(zone_type)
            print('wait_time:', wait_time)
            
            # 創建新站點（不再需要手動傳遞wait_time，由zone_type自動確定）
            print('準備呼叫 add_station')
            print('data_manager id (呼叫前):', id(self.data_manager))
            self.data_manager.add_station(station_name, x, y, station_type)
            print('add_station 已呼叫')
        else:
            print('Dialog not accepted')
        
        # 退出添加模式
        self.add_station_mode = False
        
        # 重繪網絡
        self.main_window.draw_network()
        
        # 恢復正常鼠標
        self.main_window.view.setCursor(Qt.CursorShape.ArrowCursor)
        
    def remove_station_at_position(self, pos: QPointF):
        """删除指定位置的站点"""
        items = self.main_window.scene.items(pos)
        for item in items:
            if isinstance(item, QGraphicsEllipseItem):
                station_id = item.data(0)
                if station_id:
                    station_name = self.data_manager.stations[station_id]['name']
                    self.data_manager.remove_station(station_name)
                    
                    # 退出删除模式
                    self.remove_station_mode = False
                    
                    # 如果删除的是当前选中的站点，清除选择
                    if station_id == self.main_window.selected_start or station_id == self.main_window.selected_end:
                        self.main_window.clear_selection()
                    else:
                        # 刷新视图
                        self.main_window.draw_network()
                    return
                    
        # 退出删除模式（如果没有找到站点）
        self.remove_station_mode = False