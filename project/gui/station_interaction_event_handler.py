from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtWidgets import (QGraphicsEllipseItem, QInputDialog, QDialog, QVBoxLayout, 
                          QLabel, QComboBox, QDialogButtonBox, QLineEdit, QMessageBox)
from project.algorithms.distance_calculation import calculate_distance_between_stops_by_id
import math

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
        
        # 返回悬停提示信息，添加连接信息
        tooltip_info = (f"Stop: {station['name']}\n"
                        f"Type: {station['type']}\n"
                        f"Wait time: {station['wait_time']} minutes\n"
                       f"Coordinates: ({lat:.6f}, {lon:.6f})\n\n"
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
        """在指定位置添加新站点"""
        # 将场景坐标转换为GUI坐标
        x, y = pos.x(), pos.y()
        
        
        proximity_threshold = 30 
        for station_data in self.data_manager.stations.values():
            station_x = station_data["x"]
            station_y = station_data["y"]
            distance = math.sqrt((x - station_x)**2 + (y - station_y)**2)
            if distance < proximity_threshold:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("警告")
                msg.setText("此处已有点")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                
                # 退出添加模式
                self.add_station_mode = False
                
                # 恢复正常鼠标
                self.main_window.view.setCursor(Qt.ArrowCursor)
                return
        
        # 打开名称输入对话框
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Add New Station")
        dialog.setMinimumWidth(300)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        
        # 添加名称输入
        layout.addWidget(QLabel("Station Name:"))
        default_name = f"Station_{len(self.data_manager.stations) + 1}"
        name_edit = QLineEdit(default_name)
        layout.addWidget(name_edit)
        
        # 添加站点类型选择（保留）
        layout.addWidget(QLabel("Zone Type:"))
        type_combo = QComboBox()
        type_combo.addItems(["Residential", "Commercial", "Industrial", "Mixed"])
        type_combo.setCurrentText("Residential")  # 默认选择Residential
        layout.addWidget(type_combo)
        
        # 移除原有的等待时间输入控件（关键修改点）
        
        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # 显示对话框并等待结果
        result = dialog.exec_()
        if result == QDialog.Accepted:
            station_name = name_edit.text()
            if not station_name:
                station_name = default_name  # 如果没有输入名称，使用默认名称
                
            station_type = type_combo.currentText()
            
            # 自动根据区域类型获取等待时间（通过NetworkDataManager的内部映射）
            zone_type = self.data_manager._convert_string_to_zone_type(station_type)
            wait_time = self.data_manager._get_wait_time(zone_type)
            
            # 创建新站点（不再需要手动传递wait_time，由zone_type自动确定）
            self.data_manager.add_station(station_name, x, y, station_type)
        
        # 退出添加模式
        self.add_station_mode = False
        
        # 重绘网络
        self.main_window.draw_network()
        
        # 恢复正常鼠标
        self.main_window.view.setCursor(Qt.ArrowCursor)
        
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
