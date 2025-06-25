import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
                             QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem,
                             QGraphicsPolygonItem, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QPainter, QFont, QPolygonF, QBrush

from project.algorithms.algorithms import dijkstra, find_all_paths as find_all_paths_algo
from project.module.network import TransportNetwork
from project.module.stop import Stop, ZoneType

class BusNetworkVisualization(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bus Network Path Planning System") 
        self.setGeometry(100, 100, 1000, 700)
        
        # 初始化数据
        self.stations = {}
        self.lines = {}
        self.distances = {} 
        self.selected_start = None
        self.selected_end = None
        self.hovered_station = None
        self.all_paths = []  # 存储所有路径
        self.best_path = []  # 存储最优路径
        
        # 创建固定数据（使用提供的站点数据）
        self.create_fixed_data()
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        # 主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        
        # 应用样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 12px;
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 50px;
                border-radius: 4px;
                min-width: 100px;
                font-size: 20px;
                font-family: inherit;  
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QGraphicsView {
                border: 1px solid #ddd;
                background-color: white;
                border-radius: 4px;
            }
        """)
        
        # 左侧控制面板
        control_panel = QWidget()
        control_panel.setStyleSheet("background-color: white; border-radius: 4px; padding: 10px;")
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignTop)
        control_layout.setSpacing(30)  # 增加间距
        control_layout.setContentsMargins(20, 20, 20, 20)  # 设置边距
        
        # 信息显示区域
        info_box = QWidget()
        info_box.setStyleSheet("background-color: #f9f9f9; border-radius: 4px; padding: 10px;")
        info_layout = QVBoxLayout(info_box)
        
        self.info_label = QLabel("Hover over stations to view information, click to select start and end points")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(self.info_label)
        control_layout.addWidget(info_box)
        
        # 路径信息显示区域
        path_box = QWidget()
        path_box.setStyleSheet("background-color: #f9f9f9; border-radius: 4px; padding: 10px;")
        path_layout = QVBoxLayout(path_box)
        
        self.path_info = QLabel("")
        self.path_info.setWordWrap(True)
        self.path_info.setStyleSheet("font-size: 13px;")
        path_layout.addWidget(self.path_info)
        control_layout.addWidget(path_box)
        
        # 按钮区域
        button_box = QWidget()
        button_layout = QVBoxLayout(button_box)
        button_layout.setSpacing(10)
        
        # 按钮组1 - 站点操作
        station_btn_group = QWidget()
        station_btn_layout = QVBoxLayout(station_btn_group)
        station_btn_layout.setSpacing(8)
        
        # 添加按钮图标和悬停效果
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
                QPushButton {{
                    background-color: {color};
                    color: white;
                    text-align: left;
                    padding-left: 15px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            station_btn_layout.addWidget(btn)
        
        button_layout.addWidget(station_btn_group)
        control_layout.addWidget(button_box)
        
        main_layout.addWidget(control_panel, stretch=1)
        
        # 右侧图形视图
        self.scene = QGraphicsScene()
        self.view = CustomGraphicsView(self)
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setMouseTracking(True)
        
        main_layout.addWidget(self.view, stretch=4)
        
        self.draw_network()

    def _create_transport_network(self):
        network = TransportNetwork()
        
        zone_type_map = {
            "Residential": ZoneType.RESIDENTIAL,
            "Commercial": ZoneType.COMMERCIAL,
            "Industrial": ZoneType.INDUSTRIAL,
            "Mixed": ZoneType.MIXED,
        }

        stops = {}
        for station_id, station_data in self.stations.items():
            zone_type_str = station_data['type']
            zone_type = zone_type_map.get(zone_type_str, ZoneType.MIXED)
            stop = Stop(
                stop_ID=station_data['id'],
                name=station_data['name'],
                latitude=station_data['lat'],
                longitude=station_data['lon'],
                zone_type=zone_type
            )
            stops[station_id] = stop

        for stop in stops.values():
            network.add_stop(stop)

        for (from_id, to_id), distance in self.distances.items():
            from_stop = stops.get(from_id)
            to_stop = stops.get(to_id)
            if from_stop and to_stop:
                network.add_route(from_stop, to_stop, distance)

        return network, stops

    def darken_color(self, hex_color, amount=0.7):
        """颜色变暗效果"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(comp * amount)) for comp in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def create_fixed_data(self):
        """使用提供的站点数据创建有向图"""
        # 创建9个站点
        coordinates = [
            (48.8588443, 2.3470599),  # 1 Chatelet
            (48.8433221, 2.3748736),  # 2 Gare de Lyon
            (48.853, 2.3691),         # 3 Bastille
            (48.8470364, 2.3955517),  # 4 Nation
            (48.87093, 2.3325),       # 5 Opera
            (48.867653, 2.363378),    # 6 Republique
            (48.84216, 2.321732),     # 7 Montparnasse
            (48.891342, 2.237151),    # 8 La Defense
            (48.87561, 2.325482)      # 9 Saint-Lazare
        ]
        
        # 站点名称和类型映射（根据图片数据）
        station_info = {
            1: {"name": "Chatelet", "type": "Residential"},
            2: {"name": "Gare de Lyon", "type": "Commercial"},
            3: {"name": "Bastille", "type": "Industrial"},
            4: {"name": "Nation", "type": "Residential"},
            5: {"name": "Opera", "type": "Industrial"},
            6: {"name": "Republique", "type": "Commercial"},
            7: {"name": "Montparnasse", "type": "Residential"},
            8: {"name": "La Defense", "type": "Mixed"},
            9: {"name": "Saint-Lazare", "type": "Commercial"}
        }
        
        # 计算最小和最大经纬度用于归一化
        min_lat = min(lat for lat, lon in coordinates)
        max_lat = max(lat for lat, lon in coordinates)
        min_lon = min(lon for lat, lon in coordinates)
        max_lon = max(lon for lat, lon in coordinates)
        
        # 视图尺寸参数 - 放大比例
        view_width = 1200  # 从800增加到1200
        view_height = 900   # 从600增加到900
        padding = 80        # 从50增加到80
        
        for i, (lat, lon) in enumerate(coordinates, start=1):
            # 归一化到0-1范围
            norm_lat = (lat - min_lat) / (max_lat - min_lat)
            norm_lon = (lon - min_lon) / (max_lon - min_lon)
            
            # 映射到视图坐标
            x = padding + norm_lon * (view_width - 2*padding)
            y = padding + (1 - norm_lat) * (view_height - 2*padding)  # 1- 是因为y轴向下
            
            # 使用图片中的数据设置名称和类型
            info = station_info[i]
            self.stations[i] = {
                "id": i,
                "name": info["name"],
                "lat": lat,
                "lon": lon,
                "x": x,
                "y": y,
                "type": info["type"],
                "wait_time": 5,  # 固定等待时间
                "connections": []  # 出站连接
            }
        
        # 移除圆形分布坐标计算部分
        
        # 添加有向连接和距离（使用提供的千米数据）
        connections = [
            (1, 2, 10.5), (2, 3, 8.3), (3, 4, 12.1), (4, 5, 9.4),
            (5, 6, 7.2), (6, 7, 11.6), (7, 8, 6.5), (8, 9, 8.9),
            (9, 1, 15.4), (1, 3, 7.8), (2, 5, 10.2), (3, 7, 14.3)
        ]
        
        for from_id, to_id, distance in connections:
            self.stations[from_id]["connections"].append(to_id)
            self.distances[(from_id, to_id)] = distance  # 直接使用千米单位
        
        # 创建3条线路（简单分配）
        self.lines = {
            1: {"id": 1, "name": "线路1", "color": QColor(0, 0, 255), "stations": [1, 2, 3, 4]},  # 蓝色
            2: {"id": 2, "name": "线路2", "color": QColor(0, 0, 255), "stations": [5, 6, 7, 8]},  # 蓝色
            3: {"id": 3, "name": "线路3", "color": QColor(0, 0, 255), "stations": [9, 1, 3, 7]}   # 蓝色
        }

    def draw_network(self):
        self.scene.clear()
        
        # 添加背景网格
        self.draw_grid()
        
        # 先绘制所有线路（蓝色）
        for line_id, line_data in self.lines.items():
            color = line_data["color"]
            pen = QPen(color, 3)  # 线宽从2增加到3
            pen.setStyle(Qt.SolidLine)
            
            stations = line_data["stations"]
            for i in range(len(stations)-1):
                from_station = self.stations[stations[i]]
                to_station = self.stations[stations[i+1]]
                
                # 只绘制线路定义的连接（可能不是所有连接）
                if (from_station["id"], to_station["id"]) in self.distances:
                    line = QGraphicsLineItem(from_station["x"], from_station["y"], 
                                           to_station["x"], to_station["y"])
                    line.setPen(pen)
                    self.scene.addItem(line)
        
        # 绘制所有有向连接（默认蓝色带箭头）
        for (from_id, to_id), distance in self.distances.items():
            from_station = self.stations[from_id]
            to_station = self.stations[to_id]
            
            # 检查是否是路径中的连接
            is_in_path = False
            is_in_best_path = False
            
            if self.all_paths:
                for path in self.all_paths:
                    for i in range(len(path)-1):
                        if path[i] == from_id and path[i+1] == to_id:
                            is_in_path = True
                            break
                
                if self.best_path:
                    for i in range(len(self.best_path)-1):
                        if self.best_path[i] == from_id and self.best_path[i+1] == to_id:
                            is_in_best_path = True
                            break
            
            # 设置线条颜色
            if is_in_best_path:
                line_color = QColor(255, 0, 0)  # 红色 - 最佳路径
                line_width = 5
            elif is_in_path:
                line_color = QColor(255, 255, 0)  # 黄色 - 普通路径
                line_width = 4
            else:
                line_color = QColor(0, 0, 255)  # 蓝色 - 默认
                line_width = 3
            
            # 绘制线段
            line = QGraphicsLineItem(from_station["x"], from_station["y"], 
                                   to_station["x"], to_station["y"])
            line.setPen(QPen(line_color, line_width))
            self.scene.addItem(line)
            
            # 绘制箭头
            self.draw_arrow(line.line(), line_color)
            
            # 显示距离
            mid_x = (from_station["x"] + to_station["x"]) / 2
            mid_y = (from_station["y"] + to_station["y"]) / 2
            dist_text = QGraphicsTextItem(f"{distance:.1f}km")
            dist_text.setPos(mid_x + 10, mid_y + 10)
            dist_text.setDefaultTextColor(Qt.darkBlue)
            font = QFont()
            font.setPointSize(10)
            dist_text.setFont(font)
            self.scene.addItem(dist_text)

        # 绘制站点（加大站点尺寸）
        # 优化站点绘制
        for station_id, station_data in self.stations.items():
            if station_data["type"] == "Commercial":
                color = QColor(239, 83, 80)  # 更鲜艳的红色
            elif station_data["type"] == "Residential":
                color = QColor(102, 187, 106)  # 更鲜艳的绿色
            elif station_data["type"] == "Industrial":
                color = QColor(66, 165, 245)  # 更鲜艳的蓝色
            else:  # Mixed
                color = QColor(255, 202, 40)  # 更鲜艳的黄色
            
            size = 20 if station_data["type"] != "Mixed" else 25
            
            # 添加阴影效果
            station = QGraphicsEllipseItem(station_data["x"]-size/2, station_data["y"]-size/2, 
                                         size, size)
            station.setData(0, station_id)  # 添加这行，设置站点ID到图形项
            station.setBrush(color)
            station.setPen(QPen(QColor(0, 0, 0, 150), 2))  # 半透明边框
            station.setZValue(10)  # 确保站点在最上层
            
            # 高亮选中的站点
            if station_id == self.selected_start:
                highlight = QGraphicsEllipseItem(station_data["x"]-size/2-3, station_data["y"]-size/2-3, 
                                                size+6, size+6)
                highlight.setPen(QPen(QColor(76, 175, 80), 4))
                highlight.setBrush(QBrush(Qt.NoBrush))  # 修改这里
                self.scene.addItem(highlight)
            elif station_id == self.selected_end:
                highlight = QGraphicsEllipseItem(station_data["x"]-size/2-3, station_data["y"]-size/2-3, 
                                                size+6, size+6)
                highlight.setPen(QPen(QColor(244, 67, 54), 4))
                highlight.setBrush(QBrush(Qt.NoBrush))  # 修改这里
                self.scene.addItem(highlight)
            
            self.scene.addItem(station)
            
            # 添加站点名称
            text = QGraphicsTextItem(station_data["name"])
            text.setPos(station_data["x"] + size/2 + 10, station_data["y"] - 15)
            text.setDefaultTextColor(QColor(33, 33, 33))  # 深灰色文字
            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            text.setFont(font)
            self.scene.addItem(text)

    def draw_grid(self):
        """绘制背景网格"""
        pen = QPen(QColor(240, 240, 240), 1)
        width = self.view.width()
        height = self.view.height()
        
        # 水平线
        for y in range(0, height, 50):
            line = QGraphicsLineItem(0, y, width, y)
            line.setPen(pen)
            self.scene.addItem(line)
        
        # 垂直线
        for x in range(0, width, 50):
            line = QGraphicsLineItem(x, 0, x, height)
            line.setPen(pen)
            self.scene.addItem(line)

    def draw_arrow(self, line, color):
        """绘制箭头在连接线的正中间"""
        # 获取线段的起点(p1)和终点(p2)
        p1 = line.p1()  # 起点（连接起始站）
        p2 = line.p2()  # 终点（连接目标站）

        # 计算线段中点
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2

        # 计算线段方向角度
        angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())

        # 箭头参数（加大箭头）
        arrow_length = 15  # 从10增加到15
        arrow_width = 8    # 从5增加到8

        # 计算箭头两个翼点的位置
        arrow_end1 = QPointF(
            mid_x + arrow_length * math.cos(angle + math.pi*5/6),
            mid_y + arrow_length * math.sin(angle + math.pi*5/6)
        )
        arrow_end2 = QPointF(
            mid_x + arrow_length * math.cos(angle - math.pi*5/6),
            mid_y + arrow_length * math.sin(angle - math.pi*5/6)
        )

        # 创建箭头三角形
        arrow = QPolygonF()
        arrow.append(QPointF(mid_x, mid_y))  # 箭头尖端（中点）
        arrow.append(arrow_end1)
        arrow.append(arrow_end2)

        # 创建箭头图形项
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
                    station = self.stations[station_id]
                    
                    # 构建连接信息
                    conn_info = []
                    for conn_id in station["connections"]:
                        conn_station = self.stations[conn_id]
                        distance = self.distances.get((station_id, conn_id), 0)
                        conn_info.append(f"{conn_station['name']}: {distance:.2f}km")  # 直接显示千米
                    
                    info = (f"Station: {station['name']}\n"
                            f"Type: {station['type']}\n"
                            f"Wait time: {station['wait_time']} minutes\n"
                            f"Connections:\n  " + "\n  ".join(conn_info))
                    
                    self.info_label.setText(info)
                    break
        else:
            if self.hovered_station:
                self.hovered_station = None
                self.info_label.setText("鼠标悬停查看站点信息，点击选择起点和终点")
    
    def handle_station_click(self, pos):
        items = self.scene.items(pos)
        
        for item in items:
            if isinstance(item, QGraphicsEllipseItem):
                station_id = item.data(0)  # 这里现在可以正确获取站点ID了
                if station_id:
                    if self.selected_start is None:
                        self.selected_start = station_id
                        self.info_label.setText(f"Start point selected: {self.stations[station_id]['name']}\nPlease click to select end point")
                    elif self.selected_end is None and station_id != self.selected_start:
                        self.selected_end = station_id
                        self.update_path_info()
                    else:
                        self.selected_start = station_id
                        self.selected_end = None
                        self.info_label.setText(f"Start point selected: {self.stations[station_id]['name']}\nPlease click to select end point")
                        self.path_info.setText("")
                    
                    self.draw_network()
                    break
    
    def find_all_paths(self, start, end):
        """查找所有从start到end的路径, 使用algorithms.py中的算法"""
        network, stops_map = self._create_transport_network()
        start_stop = stops_map.get(start)
        end_stop = stops_map.get(end)

        if not start_stop or not end_stop:
            self.all_paths = []
            return

        all_paths_result = find_all_paths_algo(network, start_stop, end_stop)
        
        self.all_paths = []
        for path, _ in all_paths_result:
            self.all_paths.append([stop.stop_ID for stop in path])

    def find_best_path(self, start, end):
        """找出距离最短的路径, 使用dijkstra算法"""
        network, stops_map = self._create_transport_network()
        start_stop = stops_map.get(start)
        end_stop = stops_map.get(end)

        if not start_stop or not end_stop:
            self.best_path = []
            return

        best_path_stops, _ = dijkstra(network, start_stop, end_stop)

        if best_path_stops:
            self.best_path = [s.stop_ID for s in best_path_stops]
        else:
            self.best_path = []

    def update_path_info(self):
        """更新路径信息显示"""
        if not self.selected_start or not self.selected_end:
            return
        
        self.all_paths = []
        self.best_path = []
        
        self.find_all_paths(self.selected_start, self.selected_end)
        self.find_best_path(self.selected_start, self.selected_end)
        
        info_text = f"从 {self.stations[self.selected_start]['name']} 到 {self.stations[self.selected_end]['name']}\n\n"
        
        # 显示所有路径
        info_text += "所有可能的路径:\n"
        for i, path in enumerate(self.all_paths, 1):
            total_dist = sum(self.distances.get((path[j], path[j+1]), 0) 
                             for j in range(len(path)-1))
            
            path_str = " → ".join(self.stations[station_id]['name'] for station_id in path)
            info_text += f"{i}. {path_str} (总距离: {total_dist:.2f}km)\n"  # 直接显示千米
        
        # 显示最佳路径
        if self.best_path:
            best_dist = sum(self.distances.get((self.best_path[j], self.best_path[j+1]), 0)
                            for j in range(len(self.best_path)-1))
            best_path_str = " → ".join(self.stations[station_id]['name'] for station_id in self.best_path)
            
            info_text += f"\n推荐最短路径:\n{best_path_str} (总距离: {best_dist:.2f}km)"  # 直接显示千米
        
        self.path_info.setText(info_text)
    
    def clear_selection(self):
        """清除所有选择"""
        self.selected_start = None
        self.selected_end = None
        self.all_paths = []
        self.best_path = []
        self.info_label.setText("Hover over stations to view information, click to select start and end points")
        self.path_info.setText("")
        self.draw_network()

    def add_station_dialog(self):
        """Add station dialog"""
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
                            self.add_station(name, x, y, station_type, wait_time)

    def add_station(self, name, x, y, station_type="Residential", wait_time=5):
        """Add new station"""
        new_id = max(self.stations.keys()) + 1 if self.stations else 1
        self.stations[new_id] = {
            "id": new_id,
            "name": name,
            "x": x,
            "y": y,
            "type": station_type,
            "wait_time": wait_time,
            "connections": []
        }
        self.draw_network()

    def remove_station_dialog(self):
        """Remove station dialog"""
        if not self.stations:
            QMessageBox.warning(self, "警告", "没有站点可以移除！")
            return
        
        station_id, ok = QInputDialog.getInt(self, "Remove station", "输入站点ID:", min(self.stations.keys()), min(self.stations.keys()), max(self.stations.keys()))
        if ok:
            self.remove_station(station_id)

    def remove_station(self, station_id):
        """Remove station"""
        if station_id in self.stations:
            del self.stations[station_id]
            # 更新连接信息
            for station in self.stations.values():
                if station_id in station["connections"]:
                    station["connections"].remove(station_id)
            # 更新线路信息
            for line in self.lines.values():
                if station_id in line["stations"]:
                    line["stations"].remove(station_id)
            self.draw_network()
        else:
            QMessageBox.warning(self, "警告", f"站点ID {station_id} 不存在！")

    def update_station_type_dialog(self):
        """Update station type dialog"""
        station_id, ok = QInputDialog.getInt(self, "Update station type", "输入站点ID:", min(self.stations.keys()), min(self.stations.keys()), max(self.stations.keys()))
        if ok:
            station_type, ok = QInputDialog.getItem(self, "Update station type", "站点类型:", ["Residential", "Commercial", "Mixed", "Industrial"])
            if ok:
                self.update_station_type(station_id, station_type)

    def update_station_type(self, station_id, new_type):
        """Update station type"""
        if station_id in self.stations:
            self.stations[station_id]["type"] = new_type
            self.draw_network()

    def add_connection_dialog(self):
        """Add connection dialog"""
        # 第一步：选择起点和终点
        from_id, ok = QInputDialog.getInt(self, "Add connection", "起始站点ID:", min(self.stations.keys()), min(self.stations.keys()), max(self.stations.keys()))
        if not ok:
            return
            
        to_id, ok = QInputDialog.getInt(self, "Add connection", "目标站点ID:", min(self.stations.keys()), min(self.stations.keys()), max(self.stations.keys()))
        if not ok:
            return
            
        # 检查连接是否已存在
        if (from_id, to_id) in self.distances:
            QMessageBox.warning(self, "警告", "该连接已存在！")
            return
            
        # 第二步：输入距离（千米）
        distance, ok = QInputDialog.getDouble(self, "Add connection", "距离（千米）:", 10.0, 0.1, 100.0)
        if ok:
            self.add_connection(from_id, to_id, distance)
        
    def add_connection(self, from_id, to_id, distance):
        """Add connection"""
        # 添加连接关系
        self.stations[from_id]["connections"].append(to_id)
        self.distances[(from_id, to_id)] = distance  # 直接使用千米单位
        self.draw_network()

    def remove_connection_dialog(self):
        """Remove connection dialog"""
        from_id, ok = QInputDialog.getInt(self, "Remove connection", "起始站点ID:", min(self.stations.keys()), min(self.stations.keys()), max(self.stations.keys()))
        if ok:
            to_id, ok = QInputDialog.getInt(self, "Remove connection", "目标站点ID:", min(self.stations.keys()), min(self.stations.keys()), max(self.stations.keys()))
            if ok:
                self.remove_connection(from_id, to_id)

    def remove_connection(self, from_id, to_id):
        """Remove connection"""
        if from_id in self.stations and to_id in self.stations:
            if to_id in self.stations[from_id]["connections"]:
                self.stations[from_id]["connections"].remove(to_id)
            if (from_id, to_id) in self.distances:
                del self.distances[(from_id, to_id)]
            self.draw_network()

    def find_highest_degree_station_dialog(self):
        """Find highest degree station dialog"""
        highest_degree_station = self.find_highest_degree_station()
        if highest_degree_station:
            station = self.stations[highest_degree_station]
            QMessageBox.information(self, "中心度最高的站点", f"中心度最高的站点是：{station['name']}\n连接数：{len(station['connections'])}")
        else:
            QMessageBox.information(self, "中心度最高的站点", "没有站点。")

    def find_highest_degree_station(self):
        """找到连接最多的站点"""
        max_degree = 0
        highest_degree_station = None
        for station_id, station in self.stations.items():
            degree = len(station["connections"])
            if degree > max_degree:
                max_degree = degree
                highest_degree_station = station_id
        return highest_degree_station

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BusNetworkVisualization()
    window.show()
    sys.exit(app.exec_())