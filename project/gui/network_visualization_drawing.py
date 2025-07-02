from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsLineItem,  QGraphicsView, QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsRectItem
)
from PyQt5.QtGui import QColor, QPen, QPainter, QFont, QBrush, QPolygonF
import math
from PyQt5.QtCore import Qt, QPointF, QRectF  # 新增QRectF导入

class DrawingModule:
    def __init__(self, main_window):
        self.main_window = main_window  # 持有主窗口引用

    def init_scene(self):
        """初始化图形场景并绑定到视图"""
        self.main_window.scene = QGraphicsScene()  # 创建场景实例
        # 设置一个合理的场景大小，底部增加额外空间用于显示坐标轴
        self.main_window.scene.setSceneRect(0, 0, 1000, 850)  # 高度从800增加到850
        self.main_window.view.setScene(self.main_window.scene)  # 视图绑定场景
        self.main_window.view.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        self.main_window.view.setRenderHint(QPainter.SmoothPixmapTransform)  # 平滑缩放
        # 使用NoDrag模式，显示普通鼠标
        self.main_window.view.setDragMode(QGraphicsView.NoDrag)
        self.main_window.view.setMouseTracking(True)  # 启用鼠标追踪

    def draw_network(self):
        mw = self.main_window
        mw.scene.clear()

        # 动态计算场景范围（包含所有站点+边距）
        stations = list(mw.data_manager.stations.values())
        if not stations:
            return  # 无站点时跳过
        
        # 收集所有站点的坐标
        x_coords = [s['x'] for s in stations]
        y_coords = [s['y'] for s in stations]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        padding = 50  # 四周预留50px边距
        
        # 设置场景范围（包含所有点+边距）
        scene_rect = QRectF(
            min_x - padding,  # 左边界
            min_y - padding,  # 上边界
            max_x - min_x + 2*padding,  # 宽度
            max_y - min_y + 2*padding   # 高度
        )
        mw.scene.setSceneRect(scene_rect)

        # 绘制坐标轴（固定在场景最左/最下）
        self.draw_axes()
        # self.draw_grid()  # 移除背景网格，避免重叠
        
        # 添加场景左下角的操作提示
        self.draw_instruction_note(scene_rect)
        
        if mw.best_path and mw.show_only_best_path:
            # 收集所有需要绘制的边
            edges_to_draw = {}
            
            # 处理最短路径的边
            if hasattr(mw, 'shortest_path') and mw.shortest_path:
                for i in range(len(mw.shortest_path)-1):
                    from_id = str(mw.shortest_path[i])
                    to_id = str(mw.shortest_path[i+1])
                    edge_key = (from_id, to_id)
                    if edge_key not in edges_to_draw:
                        edges_to_draw[edge_key] = {'shortest': True, 'efficiency': False}
                    else:
                        edges_to_draw[edge_key]['shortest'] = True
            
            # 处理最高效路径的边
            if hasattr(mw, 'efficiency_path') and mw.efficiency_path:
                for i in range(len(mw.efficiency_path)-1):
                    from_id = str(mw.efficiency_path[i])
                    to_id = str(mw.efficiency_path[i+1])
                    edge_key = (from_id, to_id)
                    if edge_key not in edges_to_draw:
                        edges_to_draw[edge_key] = {'shortest': False, 'efficiency': True}
                    else:
                        edges_to_draw[edge_key]['efficiency'] = True
            
            # 绘制所有边
            for (from_id, to_id), edge_info in edges_to_draw.items():
                if from_id not in mw.data_manager.stations or to_id not in mw.data_manager.stations:
                    continue
                if (from_id, to_id) not in mw.data_manager.distances:
                    continue
                
                from_station = mw.data_manager.stations[from_id]
                to_station = mw.data_manager.stations[to_id]
                
                # 检查是否两条路径都包含这条边
                is_in_both = edge_info['shortest'] and edge_info['efficiency']
                
                if is_in_both:
                    # 绘制并行的两条线
                    self.draw_parallel_lines(from_station, to_station)
                else:
                    # 绘制单条线
                    if edge_info['shortest']:
                        # 绘制红色线（最短路径）
                        line = QGraphicsLineItem(from_station["x"], from_station["y"], to_station["x"], to_station["y"])
                        line.setPen(QPen(QColor(255, 0, 0), 5))
                        mw.scene.addItem(line)
                        self.draw_arrow(line.line(), QColor(255, 0, 0))
                    elif edge_info['efficiency']:
                        # 绘制绿色线（最高效路径）
                        line = QGraphicsLineItem(from_station["x"], from_station["y"], to_station["x"], to_station["y"])
                        line.setPen(QPen(QColor(0, 255, 0), 5))  
                        mw.scene.addItem(line)
                        self.draw_arrow(line.line(), QColor(0, 255, 0))
                
                # 显示距离标签
                distance = mw.data_manager.distances[(from_id, to_id)]
                mid_x = (from_station["x"] + to_station["x"]) / 2
                mid_y = (from_station["y"] + to_station["y"]) / 2
                dist_text = QGraphicsTextItem(f"{distance:.1f}km")
                dist_text.setPos(mid_x + 10, mid_y + 10)
                
                # 根据边的类型设置标签颜色
                if is_in_both:
                    dist_text.setDefaultTextColor(Qt.darkRed)  # 重叠边用红色标签
                elif edge_info['shortest']:
                    dist_text.setDefaultTextColor(Qt.darkRed)
                else:
                    dist_text.setDefaultTextColor(Qt.darkGreen)
                
                font = QFont()
                font.setPointSize(10)
                dist_text.setFont(font)
                mw.scene.addItem(dist_text)
            
            # 收集路径中的所有站点ID
            path_stations = set()
            if hasattr(mw, 'shortest_path') and mw.shortest_path:
                path_stations.update([str(station_id) for station_id in mw.shortest_path])
            if hasattr(mw, 'efficiency_path') and mw.efficiency_path:
                path_stations.update([str(station_id) for station_id in mw.efficiency_path])
            
            # 绘制路径中的站点
            for station_id in path_stations:
                if station_id not in mw.data_manager.stations:
                    continue
                
                station_data = mw.data_manager.stations[station_id]
                size = 20 if station_data["type"] != "Mixed" else 25
                station = QGraphicsEllipseItem(station_data["x"]-size/2, station_data["y"]-size/2, size, size)
                station.setData(0, station_id)
                
                # 根据站点类型设置颜色
                if station_data["type"] == "Commercial":
                    color = QColor(239, 83, 80)
                elif station_data["type"] == "Residential":
                    color = QColor(102, 187, 106)
                elif station_data["type"] == "Industrial":
                    color = QColor(66, 165, 245)
                else:  # Mixed
                    color = QColor(255, 202, 40)
                
                station.setBrush(color)
                station.setPen(QPen(QColor(0, 0, 0, 150), 2))
                station.setZValue(10)  # 确保站点在连线上方
                
                # 高亮起点和终点
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
                
                # 添加站点名称标签
                text = QGraphicsTextItem(station_data["name"])
                text.setPos(station_data["x"] + size/2 + 5, station_data["y"] - 15)
                text.setDefaultTextColor(QColor(33, 33, 33))
                font = QFont()
                font.setPointSize(10)
                font.setBold(True)
                text.setFont(font)
                mw.scene.addItem(text)
                
        else:
            # 预处理：识别双向连接
            bidirectional_edges = set()
            for (from_id, to_id) in mw.data_manager.distances.keys():
                if (to_id, from_id) in mw.data_manager.distances:
                    # 确保只添加一次（较小ID在前）
                    edge_pair = tuple(sorted([from_id, to_id]))
                    bidirectional_edges.add(edge_pair)
            
            # 绘制所有连接
            for (from_id, to_id), distance in mw.data_manager.distances.items():
                from_id = str(from_id)
                to_id = str(to_id)
                if from_id not in mw.data_manager.stations or to_id not in mw.data_manager.stations:
                    continue
                
                from_station = mw.data_manager.stations[from_id]
                to_station = mw.data_manager.stations[to_id]
                
                # 检查是否为双向连接
                is_bidirectional = tuple(sorted([from_id, to_id])) in bidirectional_edges
                
                # 检查是否在路径中
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
                
                if is_bidirectional:
                    # 只处理ID较小的方向，避免重复绘制
                    if from_id > to_id:
                        continue
                    
                    # 对于双向连接，绘制两条平行线
                    self.draw_bidirectional_connection(
                        from_station, 
                        to_station, 
                        is_in_best_path,
                        is_in_path,
                        path_index,
                        distance
                    )
                else:
                    # 单向连接
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
                    
                    # 显示距离标签
                    mid_x = (from_station["x"] + to_station["x"]) / 2
                    mid_y = (from_station["y"] + to_station["y"]) / 2
                    dist_text = QGraphicsTextItem(f"{distance:.1f}km")
                    dist_text.setPos(mid_x + 10, mid_y + 10)
                    dist_text.setDefaultTextColor(Qt.darkBlue)
                    font = QFont()
                    font.setPointSize(10)
                    dist_text.setFont(font)
                    mw.scene.addItem(dist_text)
            
            # 绘制所有站点
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

    def draw_grid(self):
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

    def draw_parallel_lines(self, from_station, to_station):
        """绘制并行的两条线（左边红线，右边绿线）"""
        mw = self.main_window
        
        # 计算垂直于路径方向的偏移
        dx = to_station["x"] - from_station["x"]
        dy = to_station["y"] - from_station["y"]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            # 单位垂直向量
            perp_x = -dy / length
            perp_y = dx / length
            offset = 3  # 偏移距离
            
            # 绘制左边的红线
            left_from_x = from_station["x"] + perp_x * offset
            left_from_y = from_station["y"] + perp_y * offset
            left_to_x = to_station["x"] + perp_x * offset
            left_to_y = to_station["y"] + perp_y * offset
            
            left_line = QGraphicsLineItem(left_from_x, left_from_y, left_to_x, left_to_y)
            left_line.setPen(QPen(QColor(255, 0, 0), 3))  
            mw.scene.addItem(left_line)
            self.draw_arrow(left_line.line(), QColor(255, 0, 0))
            
            # 绘制右边的绿线
            right_from_x = from_station["x"] - perp_x * offset
            right_from_y = from_station["y"] - perp_y * offset
            right_to_x = to_station["x"] - perp_x * offset
            right_to_y = to_station["y"] - perp_y * offset
            
            right_line = QGraphicsLineItem(right_from_x, right_from_y, right_to_x, right_to_y)
            right_line.setPen(QPen(QColor(0, 255, 0), 3))  
            mw.scene.addItem(right_line)
            self.draw_arrow(right_line.line(), QColor(0, 255, 0))

    def draw_axes(self):
        """绘制固定在场景最左/最下的经纬度坐标轴"""
        mw = self.main_window
        scene_rect = mw.scene.sceneRect()  # 获取动态计算的场景范围
        axis_pen = QPen(QColor(0, 0, 0), 1)
        grid_pen = QPen(QColor(240, 240, 240), 1)
        text_font = QFont()
        text_font.setPointSize(8)

        # 经纬度范围（与数据管理器保持一致）
        min_lat = 48.84216
        max_lat = 48.891342
        min_lon = 2.237151
        max_lon = 2.3955517

        # 绘制底部经度轴（固定在场景最下边）
        x_axis = QGraphicsLineItem(scene_rect.left(), scene_rect.bottom(), scene_rect.right(), scene_rect.bottom())
        x_axis.setPen(axis_pen)
        mw.scene.addItem(x_axis)

        # 绘制左侧纬度轴（固定在场景最左边）
        y_axis = QGraphicsLineItem(scene_rect.left(), scene_rect.top(), scene_rect.left(), scene_rect.bottom())
        y_axis.setPen(axis_pen)
        mw.scene.addItem(y_axis)

        # 绘制经度刻度及垂直网格线（基于场景范围）
        lon_step = 0.02
        for lon in [min_lon + i * lon_step for i in range(int((max_lon - min_lon)/lon_step) + 1)]:
            x, _ = mw.data_manager._convert_geo_to_gui_coords(min_lat, lon)
            # 仅绘制在场景范围内的网格线
            if scene_rect.left() <= x <= scene_rect.right():
                # 垂直网格线（从场景顶部到底部）
                vertical_grid = QGraphicsLineItem(x, scene_rect.top(), x, scene_rect.bottom())
                vertical_grid.setPen(grid_pen)
                mw.scene.addItem(vertical_grid)
                # 底部刻度线
                tick = QGraphicsLineItem(x, scene_rect.bottom(), x, scene_rect.bottom() + 5)
                tick.setPen(axis_pen)
                mw.scene.addItem(tick)
                # 刻度标签
                label = QGraphicsTextItem(f"{lon:.4f}°E")
                label.setPos(x - 15, scene_rect.bottom() + 10)
                label.setFont(text_font)
                mw.scene.addItem(label)

        # 绘制纬度刻度及水平网格线（基于场景范围）
        lat_step = 0.01
        for lat in [min_lat + i * lat_step for i in range(int((max_lat - min_lat)/lat_step) + 1)]:
            _, y = mw.data_manager._convert_geo_to_gui_coords(lat, min_lon)
            # 仅绘制在场景范围内的网格线
            if scene_rect.top() <= y <= scene_rect.bottom():
                # 水平网格线（从场景左侧到右侧）
                horizontal_grid = QGraphicsLineItem(scene_rect.left(), y, scene_rect.right(), y)
                horizontal_grid.setPen(grid_pen)
                mw.scene.addItem(horizontal_grid)
                # 左侧刻度线
                tick = QGraphicsLineItem(scene_rect.left() - 5, y, scene_rect.left(), y)
                tick.setPen(axis_pen)
                mw.scene.addItem(tick)
                # 刻度标签
                label = QGraphicsTextItem(f"{lat:.4f}°N")
                label.setPos(scene_rect.left() - 50, y - 8)
                label.setFont(text_font)
                mw.scene.addItem(label)

    def draw_instruction_note(self, scene_rect):
        """在场景左下角绘制操作指引说明"""
        mw = self.main_window
        
        # 定位在场景左下角
        note_x = scene_rect.left() + 20  # 左边缘+20像素
        note_y = scene_rect.bottom() - 50  # 下边缘-50像素
        
        # 创建文字说明（分成两行）
        instruction = QGraphicsTextItem("Hover over the stop to view the information,\nand click to select the start and end stop")
        instruction.setPos(note_x, note_y)
        
        # 设置文字样式
        font = QFont("Arial", 11)
        instruction.setFont(font)
        instruction.setDefaultTextColor(QColor(50, 50, 50, 220))  # 深灰色，稍微透明
        
        # 创建文字背景
        text_rect = instruction.boundingRect()
        bg_rect = text_rect.adjusted(-10, -5, 10, 5)  # 扩大背景范围
        
        # 添加背景矩形
        bg = QGraphicsRectItem(bg_rect)
        bg.setPos(note_x, note_y)
        bg.setBrush(QBrush(QColor(255, 255, 255, 200)))  # 白色半透明背景
        bg.setPen(QPen(QColor(200, 200, 200), 1))  # 浅灰色边框
        mw.scene.addItem(bg)
        mw.scene.addItem(instruction)

    def draw_bidirectional_connection(self, from_station, to_station, is_in_best_path, is_in_path, path_index, distance):
        mw = self.main_window
        
        # 计算站点之间的方向向量
        dx = to_station["x"] - from_station["x"]
        dy = to_station["y"] - from_station["y"]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return  # 避免除零错误
        
        # 计算垂直于连接线的单位向量，用于偏移
        perp_x = -dy / length
        perp_y = dx / length
        
        # 每条线的偏移量
        offset = 5  # 平行线之间的间距
        
        # 确定连接线的颜色和宽度
        if is_in_best_path:
            line_color1 = QColor(255, 0, 0)  # 最佳路径红色
            line_color2 = QColor(255, 0, 0)
            line_width = 3
        elif is_in_path:
            path_color = getattr(mw, 'path_colors', [QColor(255,0,0)])[path_index]
            line_color1 = path_color
            line_color2 = path_color
            line_width = 3
        else:
            line_color1 = QColor(0, 0, 255)  # 蓝色表示一般连接
            line_color2 = QColor(0, 0, 255)
            line_width = 2
        
        # 绘制左侧线（从起点到终点，表示出边）
        left_from_x = from_station["x"] + perp_x * offset
        left_from_y = from_station["y"] + perp_y * offset
        left_to_x = to_station["x"] + perp_x * offset
        left_to_y = to_station["y"] + perp_y * offset
        
        left_line = QGraphicsLineItem(left_from_x, left_from_y, left_to_x, left_to_y)
        left_line.setPen(QPen(line_color1, line_width))
        mw.scene.addItem(left_line)
        self.draw_arrow(left_line.line(), line_color1)
        
        # 绘制右侧线（从终点到起点，表示入边）
        right_from_x = from_station["x"] - perp_x * offset
        right_from_y = from_station["y"] - perp_y * offset
        right_to_x = to_station["x"] - perp_x * offset
        right_to_y = to_station["y"] - perp_y * offset
        
        right_line = QGraphicsLineItem(right_to_x, right_to_y, right_from_x, right_from_y)
        right_line.setPen(QPen(line_color2, line_width))
        mw.scene.addItem(right_line)
        self.draw_arrow(right_line.line(), line_color2)
        
        # 在连接中间显示距离
        mid_x = (from_station["x"] + to_station["x"]) / 2
        mid_y = (from_station["y"] + to_station["y"]) / 2

        dist_text = QGraphicsTextItem(f"{distance:.1f}km")
        dist_text.setPos(mid_x + 10, mid_y + 5)
        dist_text.setDefaultTextColor(Qt.darkBlue)
        font = QFont()
        font.setPointSize(10)
        dist_text.setFont(font)
        mw.scene.addItem(dist_text)