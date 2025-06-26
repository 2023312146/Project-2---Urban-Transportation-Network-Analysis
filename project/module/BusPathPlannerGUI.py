import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from PyQt5.QtWidgets import (QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsPolygonItem, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton, QInputDialog, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QPainter, QFont, QPolygonF, QBrush

class BusNetworkVisualization(QMainWindow):
    def __init__(self, data_manager, path_analyzer):
        super().__init__()
        self.data_manager = data_manager
        self.path_analyzer = path_analyzer
        self.setWindowTitle("Bus Network Path Planning System")
        self.setGeometry(100, 100, 1000, 700)
        self.selected_start = None
        self.selected_end = None
        self.hovered_station = None
        self.all_paths = []
        self.best_path = []
        self.show_only_best_path = False  # 添加这个控制变量
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; font-family: Arial, sans-serif; }
            QLabel { font-size: 14px; color: #333; }
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                border: none; 
                padding: 8px; 
                border-radius: 4px; 
                min-width: 120px; 
                font-size: 14px; 
                font-family: inherit;  
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
            QGraphicsView { border: 1px solid #ddd; background-color: white; border-radius: 4px; }
            QInputDialog QLabel { font-size: 14px; }
            QInputDialog QLineEdit { font-size: 14px; height: 25px; }
            QInputDialog QComboBox { font-size: 14px; height: 25px; }
            QInputDialog QSpinBox { font-size: 14px; height: 25px; }
            QInputDialog QDoubleSpinBox { font-size: 14px; height: 25px; }
        """)
        control_panel = QWidget()
        control_panel.setStyleSheet("background-color: white; border-radius: 4px; padding: 10px;")
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignTop)
        control_layout.setSpacing(30)
        control_layout.setContentsMargins(20, 20, 20, 20)
        info_box = QWidget()
        info_box.setStyleSheet("background-color: #f9f9f9; border-radius: 4px; padding: 10px;")
        info_layout = QVBoxLayout(info_box)
        self.info_label = QLabel("Hover over stations to view information, click to select start and end points")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(self.info_label)
        control_layout.addWidget(info_box)
        path_box = QWidget()
        path_box.setStyleSheet("background-color: #f9f9f9; border-radius: 4px; padding: 10px;")
        path_layout = QVBoxLayout(path_box)
        
        self.path_info = QLabel("")
        self.path_info.setWordWrap(True)
        self.path_info.setStyleSheet("font-size: 13px;")
        self.path_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setWidget(self.path_info)
        scroll_area.setMinimumHeight(180)
        scroll_area.setMaximumHeight(350)
        
        path_layout.addWidget(scroll_area)
        control_layout.addWidget(path_box)
        button_box = QWidget()
        button_layout = QVBoxLayout(button_box)
        button_layout.setSpacing(10)
        station_btn_group = QWidget()
        station_btn_layout = QVBoxLayout(station_btn_group)
        station_btn_layout.setSpacing(8)
        buttons = [
            ("Clear Selection", self.clear_selection, "#f44336"),
            ("Add Station", self.add_station_dialog, "#2196F3"),
            ("Remove Station", self.remove_station_dialog, "#ff9800"),
            ("Update Station Type", self.update_station_type_dialog, "#9c27b0"),
            ("Add Connection", self.add_connection_dialog, "#4CAF50"),
            ("Remove Connection", self.remove_connection_dialog, "#607d8b"),
            ("Find Highest Degree Station", self.find_highest_degree_station_dialog, "#009688")
        ]
        for text, callback, color in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"""
                QPushButton {{ background-color: {color}; color: white; text-align: left; padding-left: 15px; }}
                QPushButton:hover {{ background-color: {self.darken_color(color)}; }}
            """)
            station_btn_layout.addWidget(btn)
        button_layout.addWidget(station_btn_group)
        control_layout.addWidget(button_box)
        main_layout.addWidget(control_panel, stretch=1)
        self.scene = QGraphicsScene()
        self.view = CustomGraphicsView(self)
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setMouseTracking(True)
        main_layout.addWidget(self.view, stretch=4)
        self.draw_network()

    def darken_color(self, hex_color, amount=0.7):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(comp * amount)) for comp in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def draw_network(self):
        self.scene.clear()
        self.draw_grid()
        
        # 如果有最佳路径且设置为只显示最佳路径
        if self.best_path and self.show_only_best_path:
            # 只绘制最佳路径的连线
            for i in range(len(self.best_path)-1):
                from_id = str(self.best_path[i])
                to_id = str(self.best_path[i+1])
                if (from_id, to_id) in self.data_manager.distances:
                    from_station = self.data_manager.stations[from_id]
                    to_station = self.data_manager.stations[to_id]
                    # 绘制红色路径线
                    line = QGraphicsLineItem(from_station["x"], from_station["y"], to_station["x"], to_station["y"])
                    line.setPen(QPen(QColor(255, 0, 0), 5))
                    self.scene.addItem(line)
                    # 绘制箭头
                    self.draw_arrow(line.line(), QColor(255, 0, 0))
                    # 显示距离
                    distance = self.data_manager.distances[(from_id, to_id)]
                    mid_x = (from_station["x"] + to_station["x"]) / 2
                    mid_y = (from_station["y"] + to_station["y"]) / 2
                    dist_text = QGraphicsTextItem(f"{distance:.1f}km")
                    dist_text.setPos(mid_x + 10, mid_y + 10)
                    dist_text.setDefaultTextColor(Qt.darkRed)
                    font = QFont()
                    font.setPointSize(10)
                    dist_text.setFont(font)
                    self.scene.addItem(dist_text)
            # 只绘制最佳路径上的站点
            for station_id in self.best_path:
                station_id = str(station_id)
                station_data = self.data_manager.stations[station_id]
                size = 20 if station_data["type"] != "Mixed" else 25
                station = QGraphicsEllipseItem(station_data["x"]-size/2, station_data["y"]-size/2, size, size)
                station.setData(0, station_id)
                # 设置站点颜色
                if station_data["type"] == "Commercial":
                    color = QColor(239, 83, 80)
                elif station_data["type"] == "Residential":
                    color = QColor(102, 187, 106)
                elif station_data["type"] == "Industrial":
                    color = QColor(66, 165, 245)
                else:
                    color = QColor(255, 202, 40)
                station.setBrush(color)
                station.setPen(QPen(QColor(0, 0, 0, 150), 2))
                station.setZValue(10)
                # 高亮起点和终点
                if station_id == str(self.selected_start):
                    highlight = QGraphicsEllipseItem(station_data["x"]-size/2-3, station_data["y"]-size/2-3, size+6, size+6)
                    highlight.setPen(QPen(QColor(76, 175, 80), 4))
                    highlight.setBrush(QBrush(Qt.NoBrush))
                    self.scene.addItem(highlight)
                elif station_id == str(self.selected_end):
                    highlight = QGraphicsEllipseItem(station_data["x"]-size/2-3, station_data["y"]-size/2-3, size+6, size+6)
                    highlight.setPen(QPen(QColor(244, 67, 54), 4))
                    highlight.setBrush(QBrush(Qt.NoBrush))
                    self.scene.addItem(highlight)
                self.scene.addItem(station)
                # 显示站点名称
                text = QGraphicsTextItem(station_data["name"])
                text.setPos(station_data["x"] + size/2 + 10, station_data["y"] - 15)
                text.setDefaultTextColor(QColor(33, 33, 33))
                font = QFont()
                font.setPointSize(10)
                font.setBold(True)
                text.setFont(font)
                self.scene.addItem(text)
        else:
            # 原始绘制逻辑保持不变
            for line_id, line_data in self.data_manager.lines.items():
                color = QColor(*line_data["color"])
                pen = QPen(color, 3)
                pen.setStyle(Qt.SolidLine)
                stations = line_data["stations"]
                for i in range(len(stations)-1):
                    from_station = self.data_manager.stations[str(stations[i])]
                    to_station = self.data_manager.stations[str(stations[i+1])]
                    if (str(from_station["id"]), str(to_station["id"])) in self.data_manager.distances:
                        line = QGraphicsLineItem(from_station["x"], from_station["y"], to_station["x"], to_station["y"])
                        line.setPen(pen)
                        self.scene.addItem(line)
            for (from_id, to_id), distance in self.data_manager.distances.items():
                from_station = self.data_manager.stations[str(from_id)]
                to_station = self.data_manager.stations[str(to_id)]
                is_in_path = False
                is_in_best_path = False
                path_index = -1
                if self.all_paths:
                    for idx, path in enumerate(self.all_paths):
                        for i in range(len(path)-1):
                            if str(path[i]) == str(from_id) and str(path[i+1]) == str(to_id):
                                is_in_path = True
                                path_index = idx % len(self.path_colors)
                                break
                    if self.best_path:
                        for i in range(len(self.best_path)-1):
                            if str(self.best_path[i]) == str(from_id) and str(self.best_path[i+1]) == str(to_id):
                                is_in_best_path = True
                                break
                if is_in_best_path:
                    line_color = QColor(255, 0, 0)  # 最佳路径保持红色
                    line_width = 5
                elif is_in_path:
                    line_color = self.path_colors[path_index]  # 使用对应路径的颜色
                    line_width = 4
                else:
                    line_color = QColor(0, 0, 255)  # 普通连接保持蓝色
                    line_width = 3
                line = QGraphicsLineItem(from_station["x"], from_station["y"], to_station["x"], to_station["y"])
                line.setPen(QPen(line_color, line_width))
                self.scene.addItem(line)
                self.draw_arrow(line.line(), line_color)
                mid_x = (from_station["x"] + to_station["x"]) / 2
                mid_y = (from_station["y"] + to_station["y"]) / 2
                dist_text = QGraphicsTextItem(f"{distance:.1f}km")
                dist_text.setPos(mid_x + 10, mid_y + 10)
                dist_text.setDefaultTextColor(Qt.darkBlue)
                font = QFont()
                font.setPointSize(10)
                dist_text.setFont(font)
                self.scene.addItem(dist_text)
            for station_id, station_data in self.data_manager.stations.items():
                size = 20 if station_data["type"] != "Mixed" else 25
                station = QGraphicsEllipseItem(station_data["x"]-size/2, station_data["y"]-size/2, size, size)
                station.setData(0, str(station_id))
                # 设置站点颜色
                if station_data["type"] == "Commercial":
                    color = QColor(239, 83, 80)
                elif station_data["type"] == "Residential":
                    color = QColor(102, 187, 106)
                elif station_data["type"] == "Industrial":
                    color = QColor(66, 165, 245)
                else:
                    color = QColor(255, 202, 40)
                station.setBrush(color)
                station.setPen(QPen(QColor(0, 0, 0, 150), 2))
                station.setZValue(10)
                if str(station_id) == str(self.selected_start):
                    highlight = QGraphicsEllipseItem(station_data["x"]-size/2-3, station_data["y"]-size/2-3, size+6, size+6)
                    highlight.setPen(QPen(QColor(76, 175, 80), 4))
                    highlight.setBrush(QBrush(Qt.NoBrush))
                    self.scene.addItem(highlight)
                elif str(station_id) == str(self.selected_end):
                    highlight = QGraphicsEllipseItem(station_data["x"]-size/2-3, station_data["y"]-size/2-3, size+6, size+6)
                    highlight.setPen(QPen(QColor(244, 67, 54), 4))
                    highlight.setBrush(QBrush(Qt.NoBrush))
                    self.scene.addItem(highlight)
                self.scene.addItem(station)
                text = QGraphicsTextItem(station_data["name"])
                text.setPos(station_data["x"] + size/2 + 10, station_data["y"] - 15)
                text.setDefaultTextColor(QColor(33, 33, 33))
                font = QFont()
                font.setPointSize(10)
                font.setBold(True)
                text.setFont(font)
                self.scene.addItem(text)

    def draw_grid(self):
        pen = QPen(QColor(240, 240, 240), 1)
        width = self.view.width()
        height = self.view.height()
        for y in range(0, height, 50):
            line = QGraphicsLineItem(0, y, width, y)
            line.setPen(pen)
            self.scene.addItem(line)
        for x in range(0, width, 50):
            line = QGraphicsLineItem(x, 0, x, height)
            line.setPen(pen)
            self.scene.addItem(line)

    def draw_arrow(self, line, color):
        p1 = line.p1()
        p2 = line.p2()
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2
        angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
        arrow_length = 15
        arrow_width = 8
        arrow_end1 = QPointF(
            mid_x + arrow_length * math.cos(angle + math.pi*5/6),
            mid_y + arrow_length * math.sin(angle + math.pi*5/6)
        )
        arrow_end2 = QPointF(
            mid_x + arrow_length * math.cos(angle - math.pi*5/6),
            mid_y + arrow_length * math.sin(angle - math.pi*5/6)
        )
        arrow = QPolygonF()
        arrow.append(QPointF(mid_x, mid_y))
        arrow.append(arrow_end1)
        arrow.append(arrow_end2)
        arrow_item = QGraphicsPolygonItem(arrow)
        arrow_item.setBrush(color)
        arrow_item.setPen(QPen(color, 1))
        self.scene.addItem(arrow_item)

    def handle_station_hover(self, pos):
        items = self.scene.items(pos)
        for item in items:
            if isinstance(item, QGraphicsEllipseItem):
                station_id = item.data(0)
                if station_id and station_id != self.hovered_station:
                    self.hovered_station = station_id
                    station = self.data_manager.stations[station_id]
                    conn_info = []
                    for conn_id in station["connections"]:
                        conn_station = self.data_manager.stations[conn_id]
                        distance = self.data_manager.distances.get((station_id, conn_id), 0)
                        conn_info.append(f"{conn_station['name']}: {distance:.2f}km")
                    info = (f"Station: {station['name']}\n"
                            f"Type: {station['type']}\n"
                            f"Wait time: {station['wait_time']} minutes\n"
                            f"Connections:\n  " + "\n  ".join(conn_info))
                    self.info_label.setText(info)
                    break
        else:
            if self.hovered_station:
                self.hovered_station = None

    def handle_station_click(self, pos):
        items = self.scene.items(pos)
        for item in items:
            if isinstance(item, QGraphicsEllipseItem):
                station_id = item.data(0)
                if station_id:
                    station_name = self.data_manager.stations[station_id]['name']
                    if self.selected_start is None:
                        self.selected_start = station_id
                        self.info_label.setText(f"Start point selected: {station_name}\nPlease click to select end point")
                    elif self.selected_end is None and station_id != self.selected_start:
                        self.selected_end = station_id
                        self.update_path_info()
                    else:
                        self.selected_start = station_id
                        self.selected_end = None
                        self.info_label.setText(f"Start point selected: {station_name}\nPlease click to select end point")
                        self.path_info.setText("")
                    self.draw_network()
                    break

    def update_path_info(self):
        if not self.selected_start or not self.selected_end:
            return
        self.all_paths = self.path_analyzer.find_all_paths(str(self.selected_start), str(self.selected_end))
        self.best_path = self.path_analyzer.find_best_path(str(self.selected_start), str(self.selected_end))
        
        # 设置只显示最佳路径
        self.show_only_best_path = True
        
        start_name = self.data_manager.stations.get(str(self.selected_start), {}).get("name", str(self.selected_start))
        end_name = self.data_manager.stations.get(str(self.selected_end), {}).get("name", str(self.selected_end))
        
        info_text = f"FROM {start_name} TO {end_name}<br>-----------<br>"
        if not self.all_paths:
            info_text += "No path found."
        else:
            info_text += "All reachable paths:"
        
        for idx, path in enumerate(self.all_paths):
            path = [str(station) for station in path]
            path_names = []
            for station_id in path:
                station = self.data_manager.stations.get(str(station_id), {})
                path_names.append(station.get("name", str(station_id)))
            
            total_dist = 0.0
            for j in range(len(path)-1):
                dist = self.data_manager.distances.get((str(path[j]), str(path[j+1])), 0)
                total_dist += dist
            
            path_str = " → ".join(path_names)
            info_text += f"{path_str} (distance: {total_dist:.2f}km)<br>-----------<br>"
        
        if self.best_path:
            info_text += "<br>"
            best_path = [str(station) for station in self.best_path]
            best_path_names = []
            for station_id in best_path:
                station = self.data_manager.stations.get(str(station_id), {})
                best_path_names.append(station.get("name", str(station_id)))
            
            best_dist = 0.0
            for j in range(len(best_path)-1):
                dist = self.data_manager.distances.get((str(best_path[j]), str(best_path[j+1])), 0)
                best_dist += dist
            
            best_path_str = " → ".join(best_path_names)
            info_text += f"<b>Recommended Path (Minimum Distance):</b><br>{best_path_str} (distance: {best_dist:.2f}km)"
        
        self.path_info.setText(info_text)
        self.path_info.setTextFormat(Qt.RichText)

    def clear_selection(self):
        self.selected_start = None
        self.selected_end = None
        self.all_paths = []
        self.best_path = []
        self.show_only_best_path = False  # 重置显示模式
        self.info_label.setText("Hover over stations to view information, click to select start and end points")
        self.path_info.setText("")
        self.draw_network()

    def add_station_dialog(self):
        name, ok = QInputDialog.getText(self, "Add Station", "Station name:")
        if ok:
            x, ok = QInputDialog.getInt(self, "Add Station", "X coordinate:", 500, 0, 1000)
            if ok:
                y, ok = QInputDialog.getInt(self, "Add Station", "Y coordinate:", 350, 0, 700)
                if ok:
                    station_type, ok = QInputDialog.getItem(self, "Add Station", "Station type:", ["Residential", "Commercial", "Mixed", "Industrial"])
                    if ok:
                        wait_time, ok = QInputDialog.getInt(self, "Add Station", "Wait time (minutes):", 5, 0, 60)
                        if ok:
                            self.data_manager.add_station(name, x, y, station_type, wait_time)
                            self.draw_network()

    def remove_station_dialog(self):
        if not self.data_manager.stations:
            msg = QMessageBox()
            msg.setStyleSheet(self.get_messagebox_style())
            msg.warning(self, "Warning", "No stops can be removed!")
            return
        station_names = {v['name']: k for k, v in self.data_manager.stations.items()}
        station_name, ok = QInputDialog.getItem(self, "Remove station", "Select a stop:", list(station_names.keys()))
        if ok and station_name:
            self.data_manager.remove_station(station_name)
            self.draw_network()

    def update_station_type_dialog(self):
        if not self.data_manager.stations:
            QMessageBox.warning(self, "Warning", "No stops can be updated!")
            return
        station_names = {v['name']: k for k, v in self.data_manager.stations.items()}
        station_name, ok = QInputDialog.getItem(self, "Update station type", "Select a stop:", list(station_names.keys()))
        if ok and station_name:
            station_type, ok = QInputDialog.getItem(self, "Update station type", "Stop type:", ["Residential", "Commercial", "Mixed", "Industrial"])
            if ok:
                self.data_manager.update_station_type(station_name, station_type)
                self.draw_network()

    def add_connection_dialog(self):
        if len(self.data_manager.stations) < 2:
            QMessageBox.warning(self, "warning", "You'll need at least two stops to add a connection!")
            return
        station_names = list(self.data_manager.station_name_to_id.keys())
        from_name, ok = QInputDialog.getItem(self, "Add connection", "Start stop:", station_names)
        if not ok:
            return
        to_name, ok = QInputDialog.getItem(self, "Add connection", "Target stop:", [n for n in station_names if n != from_name])
        if not ok:
            return

        from_id = self.data_manager.station_name_to_id.get(from_name)
        to_id = self.data_manager.station_name_to_id.get(to_name)

        if from_id is None or to_id is None:
            QMessageBox.warning(self, "Error", "Selected station not found.")
            return

        if (from_id, to_id) in self.data_manager.distances:
            QMessageBox.warning(self, "Warning", "The connection already exists!")
            return
        distance, ok = QInputDialog.getDouble(self, "Add connection", "distance(km):", 10.0, 0.1, 100.0)
        if ok:
            self.data_manager.add_connection(from_name, to_name, distance)
            self.draw_network()

    def remove_connection_dialog(self):
        if len(self.data_manager.distances) == 0:
            QMessageBox.warning(self, "Warning", "No connection can be removed!")
            return
        station_names = list(self.data_manager.station_name_to_id.keys())
        from_name, ok = QInputDialog.getItem(self, "Remove connection", "Start stop:", station_names)
        if not ok:
            return
        
        from_id = self.data_manager.station_name_to_id.get(from_name)
        if not from_id:
            return

        connections = []
        for f_id, t_id in self.data_manager.distances.keys():
            if f_id == from_id:
                to_station_name = self.data_manager.stations.get(t_id, {}).get('name')
                if to_station_name:
                    connections.append(to_station_name)

        if not connections:
            QMessageBox.warning(self, "Warning", "There is no exit connection at this stop!")
            return
        to_name, ok = QInputDialog.getItem(self, "Remove connection", "target stop:", connections)
        if ok:
            self.data_manager.remove_connection(from_name, to_name)
            self.draw_network()

    def find_highest_degree_station_dialog(self):
        highest_degree_station_id = self.path_analyzer.find_highest_degree_station()
        msg = QMessageBox()
        msg.setStyleSheet("""
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
        """)
        if highest_degree_station_id:
            station = self.data_manager.stations[highest_degree_station_id]
            msg.setWindowTitle("Highest Degree Station")
            msg.setText(f"<b>{station['name']}</b><br>Connections: {len(station['connections'])}")
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

import math
class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        pos = self.mapToScene(event.pos())
        self.parent.handle_station_hover(pos)
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            self.parent.handle_station_click(pos)