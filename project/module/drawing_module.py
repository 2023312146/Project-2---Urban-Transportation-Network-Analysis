from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QGraphicsEllipseItem,
    QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsView
)
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPen, QFont, QPolygonF, QBrush, QPainter
import math

class DrawingModule:
    def __init__(self, main_window):
        self.main_window = main_window  # 持有主窗口引用

    # 新增：场景初始化方法（解决AttributeError）
    def init_scene(self):
        """初始化图形场景并绑定到视图"""
        self.main_window.scene = QGraphicsScene()  # 创建场景实例
        self.main_window.view.setScene(self.main_window.scene)  # 视图绑定场景
        self.main_window.view.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        self.main_window.view.setRenderHint(QPainter.SmoothPixmapTransform)  # 平滑缩放
        self.main_window.view.setDragMode(QGraphicsView.ScrollHandDrag)  # 手型拖拽模式
        self.main_window.view.setMouseTracking(True)  # 启用鼠标追踪

    def draw_network(self):
        mw = self.main_window
        mw.scene.clear()
        self.draw_grid()
        if mw.best_path and mw.show_only_best_path:
            for i in range(len(mw.best_path)-1):
                from_id = str(mw.best_path[i])
                to_id = str(mw.best_path[i+1])
                if from_id not in mw.data_manager.stations or to_id not in mw.data_manager.stations:
                    continue
                if (from_id, to_id) in mw.data_manager.distances:
                    from_station = mw.data_manager.stations[from_id]
                    to_station = mw.data_manager.stations[to_id]
                    line = QGraphicsLineItem(from_station["x"], from_station["y"], to_station["x"], to_station["y"])
                    line.setPen(QPen(QColor(255, 0, 0), 5))
                    mw.scene.addItem(line)
                    self.draw_arrow(line.line(), QColor(255, 0, 0))
                    distance = mw.data_manager.distances[(from_id, to_id)]
                    mid_x = (from_station["x"] + to_station["x"]) / 2
                    mid_y = (from_station["y"] + to_station["y"]) / 2
                    dist_text = QGraphicsTextItem(f"{distance:.1f}km")
                    dist_text.setPos(mid_x + 10, mid_y + 10)
                    dist_text.setDefaultTextColor(Qt.darkRed)
                    font = QFont()
                    font.setPointSize(10)
                    dist_text.setFont(font)
                    mw.scene.addItem(dist_text)
            for station_id in mw.best_path:
                station_id = str(station_id)
                if station_id not in mw.data_manager.stations:
                    continue
                station_data = mw.data_manager.stations[station_id]
                size = 20 if station_data["type"] != "Mixed" else 25
                station = QGraphicsEllipseItem(station_data["x"]-size/2, station_data["y"]-size/2, size, size)
                station.setData(0, station_id)
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
                if station_id == str(mw.selected_start):
                    highlight = QGraphicsEllipseItem(station_data["x"]-size/2-3, station_data["y"]-size/2-3, size+6, size+6)
                    highlight.setPen(QPen(QColor(76, 175, 80), 4))
                    highlight.setBrush(QBrush(Qt.NoBrush))
                    mw.scene.addItem(highlight)
                elif station_id == str(mw.selected_end):
                    highlight = QGraphicsEllipseItem(station_data["x"]-size/2-3, station_data["y"]-size/2-3, size+6, size+6)
                    highlight.setPen(QPen(QColor(244, 67, 54), 4))
                    highlight.setBrush(QBrush(Qt.NoBrush))
                    mw.scene.addItem(highlight)
                mw.scene.addItem(station)
                text = QGraphicsTextItem(station_data["name"])
                text.setPos(station_data["x"] + size/2 + 10, station_data["y"] - 15)
                text.setDefaultTextColor(QColor(33, 33, 33))
                font = QFont()
                font.setPointSize(10)
                font.setBold(True)
                text.setFont(font)
                mw.scene.addItem(text)
        else:
            for line_id, line_data in mw.data_manager.lines.items():
                color = QColor(*line_data["color"])
                pen = QPen(color, 3)
                pen.setStyle(Qt.SolidLine)
                stations = line_data["stations"]
                for i in range(len(stations)-1):
                    from_id = str(stations[i])
                    to_id = str(stations[i+1])
                    if from_id not in mw.data_manager.stations or to_id not in mw.data_manager.stations:
                        continue
                    from_station = mw.data_manager.stations[from_id]
                    to_station = mw.data_manager.stations[to_id]
                    if (str(from_station["id"]), str(to_station["id"])) in mw.data_manager.distances:
                        line = QGraphicsLineItem(from_station["x"], from_station["y"], to_station["x"], to_station["y"])
                        line.setPen(pen)
                        mw.scene.addItem(line)
            for (from_id, to_id), distance in mw.data_manager.distances.items():
                from_id = str(from_id)
                to_id = str(to_id)
                if from_id not in mw.data_manager.stations or to_id not in mw.data_manager.stations:
                    continue
                from_station = mw.data_manager.stations[from_id]
                to_station = mw.data_manager.stations[to_id]
                is_in_path = False
                is_in_best_path = False
                path_index = -1
                if mw.all_paths:
                    for idx, path in enumerate(mw.all_paths):
                        for i in range(len(path)-1):
                            if str(path[i]) == str(from_id) and str(path[i+1]) == str(to_id):
                                is_in_path = True
                                path_index = idx % len(getattr(mw, 'path_colors', [QColor(255,0,0)]))
                                break
                    if mw.best_path:
                        for i in range(len(mw.best_path)-1):
                            if str(mw.best_path[i]) == str(from_id) and str(mw.best_path[i+1]) == str(to_id):
                                is_in_best_path = True
                                break
                if is_in_best_path:
                    line_color = QColor(255, 0, 0)
                    line_width = 5
                elif is_in_path:
                    line_color = getattr(mw, 'path_colors', [QColor(255,0,0)])[path_index]
                    line_width = 4
                else:
                    line_color = QColor(0, 0, 255)
                    line_width = 3
                line = QGraphicsLineItem(from_station["x"], from_station["y"], to_station["x"], to_station["y"])
                line.setPen(QPen(line_color, line_width))
                mw.scene.addItem(line)
                self.draw_arrow(line.line(), line_color)
                mid_x = (from_station["x"] + to_station["x"]) / 2
                mid_y = (from_station["y"] + to_station["y"]) / 2
                dist_text = QGraphicsTextItem(f"{distance:.1f}km")
                dist_text.setPos(mid_x + 10, mid_y + 10)
                dist_text.setDefaultTextColor(Qt.darkBlue)
                font = QFont()
                font.setPointSize(10)
                dist_text.setFont(font)
                mw.scene.addItem(dist_text)
            for station_id, station_data in mw.data_manager.stations.items():
                size = 20 if station_data["type"] != "Mixed" else 25
                station = QGraphicsEllipseItem(station_data["x"]-size/2, station_data["y"]-size/2, size, size)
                station.setData(0, str(station_id))
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
                if str(station_id) == str(mw.selected_start):
                    highlight = QGraphicsEllipseItem(station_data["x"]-size/2-3, station_data["y"]-size/2-3, size+6, size+6)
                    highlight.setPen(QPen(QColor(76, 175, 80), 4))
                    highlight.setBrush(QBrush(Qt.NoBrush))
                    mw.scene.addItem(highlight)
                elif str(station_id) == str(mw.selected_end):
                    highlight = QGraphicsEllipseItem(station_data["x"]-size/2-3, station_data["y"]-size/2-3, size+6, size+6)
                    highlight.setPen(QPen(QColor(244, 67, 54), 4))
                    highlight.setBrush(QBrush(Qt.NoBrush))
                    mw.scene.addItem(highlight)
                mw.scene.addItem(station)
                text = QGraphicsTextItem(station_data["name"])
                text.setPos(station_data["x"] + size/2 + 10, station_data["y"] - 15)
                text.setDefaultTextColor(QColor(33, 33, 33))
                font = QFont()
                font.setPointSize(10)
                font.setBold(True)
                text.setFont(font)
                mw.scene.addItem(text)

    # 新增：网格绘制方法（解决AttributeError）
    def draw_grid(self):
        """绘制背景网格（50px间隔的浅灰色线）"""
        pen = QPen(QColor(240, 240, 240), 1)  # 浅灰色画笔
        scene_rect = self.main_window.scene.sceneRect()  # 获取场景范围
        
        # 绘制水平线
        for y in range(0, int(scene_rect.height()), 50):
            line = QGraphicsLineItem(scene_rect.left(), y, scene_rect.right(), y)
            line.setPen(pen)
            self.main_window.scene.addItem(line)
        
        # 绘制垂直线
        for x in range(0, int(scene_rect.width()), 50):
            line = QGraphicsLineItem(x, scene_rect.top(), x, scene_rect.bottom())
            line.setPen(pen)
            self.main_window.scene.addItem(line)

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
        self.main_window.scene.addItem(arrow_item)