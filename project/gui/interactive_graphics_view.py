from PyQt5.QtWidgets import QGraphicsView, QToolTip, QApplication, QLabel
from PyQt5.QtCore import Qt, QPoint, QPointF, QTimer
from PyQt5.QtGui import QCursor

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setMouseTracking(True) 
        self.last_hovered_station = None  
        self.last_mouse_pos = QPoint()  
        self.move_threshold = 5  
        
        # 创建自定义持久悬停标签
        self.hover_label = QLabel(parent)
        self.hover_label.setStyleSheet("""
            background-color: #2a2a2a; 
            color: #ffffff; 
            border: 2px solid #444444;
            border-radius: 6px;
            padding: 12px;
            font-size: 14px;
            font-weight: bold;
            font-family: Arial, sans-serif;
        """)
        self.hover_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.hover_label.setWordWrap(True)
        self.hover_label.setMinimumWidth(350)  # 设置最小宽度
        self.hover_label.setMaximumWidth(500)  # 设置最大宽度
        self.hover_label.hide()  # 初始隐藏
        
        # 添加延迟处理定时器
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.setInterval(100)  # 100ms延迟
        self.hover_timer.timeout.connect(self.process_hover)
        
        # 保存当前处理的位置
        self.current_hover_pos = None
        
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        
        # 计算鼠标移动距离
        current_pos = event.pos()
        if self.last_mouse_pos.isNull():
            self.last_mouse_pos = current_pos
            
        # 如果移动距离小于阈值，不处理（除非是首次移动）
        move_distance = (current_pos - self.last_mouse_pos).manhattanLength()
        if move_distance < self.move_threshold and self.current_hover_pos is not None:
            return
            
        # 更新最后位置
        self.last_mouse_pos = current_pos
        
        # 保存当前要处理的位置
        self.current_hover_pos = self.mapToScene(current_pos)
        
        # 启动延迟处理定时器（如果移动较大，停止之前的定时器并重新开始）
        self.hover_timer.stop()
        self.hover_timer.start()
        
    def process_hover(self):
        """定时器触发时处理悬停事件"""
        if not self.current_hover_pos:
            return
            
        # 获取鼠标悬停的站点信息
        tooltip_info = self.parent.handle_station_hover(self.current_hover_pos)
        
        # 如果获取到站点信息，则显示自定义标签
        if tooltip_info:
            # 更新标签内容
            self.hover_label.setText(tooltip_info)
            self.hover_label.adjustSize()  # 根据内容调整大小
            
            # 将场景坐标转换为全局坐标
            view_pos = self.mapFromScene(self.current_hover_pos)
            global_pos = self.mapToGlobal(view_pos)
            
            # 获取屏幕尺寸和悬浮窗尺寸
            screen_rect = QApplication.desktop().screenGeometry()
            label_width = self.hover_label.width()
            label_height = self.hover_label.height()
            
            # 计算最佳位置，避免超出屏幕边缘
            x_pos = global_pos.x() + 15
            y_pos = global_pos.y() + 15
            
            # 检查右边缘
            if x_pos + label_width > screen_rect.right():
                x_pos = global_pos.x() - label_width - 10  # 放在鼠标左侧
                
            # 检查下边缘
            if y_pos + label_height > screen_rect.bottom():
                y_pos = global_pos.y() - label_height - 10  # 放在鼠标上方
            
            # 定位标签
            self.hover_label.move(x_pos, y_pos)
            
            # 显示标签
            self.hover_label.show()
        else:
            # 无站点时隐藏标签
            self.hover_label.hide()
            self.last_hovered_station = None  # 重置跟踪
        
            # 如果处于添加或删除站点模式，更新光标形状和提示
        if hasattr(self.parent, 'interaction_handler'):
            if self.parent.interaction_handler.add_station_mode:
                self.setCursor(Qt.CrossCursor)  # 十字光标表示添加
                QToolTip.showText(self.mapToGlobal(self.mapFromScene(self.current_hover_pos)), "点击此处添加新站点")
            elif self.parent.interaction_handler.remove_station_mode:
                self.setCursor(Qt.ForbiddenCursor)  # 禁止光标表示删除
                QToolTip.showText(self.mapToGlobal(self.mapFromScene(self.current_hover_pos)), "点击站点删除它")
            else:
                self.setCursor(Qt.ArrowCursor)  # 默认光标
                QToolTip.hideText()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            self.parent.handle_station_click(pos)
            
    def wheelEvent(self, event):
        """处理鼠标滚轮事件，实现缩放功能"""
        # 获取当前缩放因子
        factor = 1.2
        
        # 根据滚轮方向确定缩放方向
        if event.angleDelta().y() > 0:
            # 向上滚动，放大
            self.scale(factor, factor)
        else:
            # 向下滚动，缩小
            self.scale(1/factor, 1/factor)
            
    def keyPressEvent(self, event):
        """处理键盘事件，实现取消当前模式"""
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Escape:
            if hasattr(self.parent, 'interaction_handler'):
                handler = self.parent.interaction_handler
                
                # 取消添加/删除站点模式
                if handler.add_station_mode or handler.remove_station_mode:
                    handler.add_station_mode = False
                    handler.remove_station_mode = False
                    self.setCursor(Qt.ArrowCursor)
                    self.parent.info_label.setText("已退出站点编辑模式")
            
            # 取消连接操作模式（关键修改：显式重置属性）
            if hasattr(self.parent, 'data_dialogs'):
                data_dialogs = self.parent.data_dialogs
                if hasattr(data_dialogs, 'connection_mode') and data_dialogs.connection_mode:
                    # 调用取消方法（假设该方法可能未完全清理）
                    if hasattr(data_dialogs, 'cancel_connection_mode'):
                        data_dialogs.cancel_connection_mode()
                    
                    # 显式重置状态属性
                    data_dialogs.selected_from_station = None
                    data_dialogs.connection_mode = None
                    
                    # 恢复光标
                    self.setCursor(Qt.ArrowCursor)
                    self.parent.info_label.setText("已取消连接操作")

    def leaveEvent(self, event):
        """鼠标离开视图时隐藏标签"""
        super().leaveEvent(event)
        self.hover_label.hide()
        self.last_hovered_station = None
        self.hover_timer.stop()  # 停止定时器