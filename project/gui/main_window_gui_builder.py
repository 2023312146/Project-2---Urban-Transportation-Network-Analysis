from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QPushButton, QGraphicsScene)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPainter
from project.gui.interactive_graphics_view import CustomGraphicsView
from project.gui.stop_and_route_dialogs_gui import DataDialogs
from project.gui.network_visualization_drawing import DrawingModule
from project.gui.station_interaction_event_handler import InteractionHandler
from project.gui.path_analysis_result_display import PathDisplay
from PyQt5.QtWidgets import QMessageBox  # 新增导入

class GUIBuilder(QMainWindow):
    def __init__(self, data_manager, path_analyzer):
        super().__init__()
        self.data_manager = data_manager
        self.path_analyzer = path_analyzer
        self.selected_start = None
        self.selected_end = None
        self.hovered_station = None
        self.all_paths = []
        self.best_path = []
        self.show_only_best_path = False
        self.data_dialogs = DataDialogs(self)
        self.drawing_module = DrawingModule(self)
        self.interaction_handler = InteractionHandler(self)
        self.path_display = PathDisplay(self)
        self.init_ui()
        self.draw_network = self.drawing_module.draw_network

    def init_ui(self):
        self.setWindowTitle("Bus Network Path Planning System")
        self.setGeometry(100, 100, 1000, 700)
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
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        control_panel = QWidget()
        control_panel.setStyleSheet("background-color: white; border-radius: 4px; padding: 10px;")
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignTop)
        control_layout.setSpacing(20)  # 减少面板间距
        control_layout.setContentsMargins(20, 20, 20, 20)
        
        # 保留信息标签但隐藏起来（供其他功能使用）
        self.info_label = QLabel("Click to select start and end points")
        self.info_label.setVisible(False)
        
        # 路径信息面板 - 现在占据更多空间
        path_box = QWidget()
        path_box.setStyleSheet("background-color: #f9f9f9; border-radius: 4px; padding: 10px;")
        path_layout = QVBoxLayout(path_box)
        
        # 添加路径面板标题
        path_title = QLabel("<b>Path Information</b>")
        path_title.setStyleSheet("font-size: 16px;")
        path_layout.addWidget(path_title)
        
        self.path_info = QLabel("")
        self.path_info.setWordWrap(True)
        self.path_info.setStyleSheet("font-size: 13px;")
        self.path_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setWidget(self.path_info)
        scroll_area.setMinimumHeight(250)  # 增加高度
        scroll_area.setMaximumHeight(400)  # 增加最大高度
        path_layout.addWidget(scroll_area)
        control_layout.addWidget(path_box)
        
        # 按钮分组配置（类型化颜色编码）
        BUTTON_GROUPS = [
            {
                "title": "Stop management",
                "color": "#2196F3",  # 蓝色系（信息类操作）
                "buttons": [
                    ("Add Station", self.data_dialogs.add_station_dialog),
                    ("Remove Station", self.data_dialogs.remove_station_dialog),
                    ("Update Station Type", self.data_dialogs.update_station_type_dialog)
                ]
            },
            {
                "title": "Connection management",
                "color": "#4CAF50",  # 绿色系（创建/修改类操作）
                "buttons": [
                    ("Add Connection", self.data_dialogs.add_connection_dialog),
                    ("Remove Connection", self.data_dialogs.remove_connection_dialog)
                ]
            },
            {
                "title": "Analytical tools",
                "color": "#009688",  # 青色系（数据分析类操作）
                "buttons": [
                    ("Find Highest Degree Station", self.data_dialogs.find_highest_degree_station_dialog)
                ]
            },
            {
                "title": "File Operations",
                "color": "#9c27b0",  # 紫色系（文件操作）
                "buttons": [
                    ("Save Data", self.save_data),
                    ("Clear Selection", self.clear_selection)  # 新增Clean按钮，关联清除逻辑
                ]
            }
        ]
        button_box = QWidget()
        button_layout = QVBoxLayout(button_box)
        button_layout.setSpacing(5)  # 增加组间间距
        for group in BUTTON_GROUPS:
            # 创建组标题
            group_title = QLabel(f"<b>{group['title']}</b>")
            group_title.setStyleSheet(f"color: {group['color']}; font-size: 16px;")
            button_layout.addWidget(group_title)
            
            # 创建组内按钮容器
            group_container = QWidget()
            group_layout = QVBoxLayout(group_container)
            group_layout.setSpacing(8)
            
            # 创建组内按钮
            for text, callback in group["buttons"]:
                btn = QPushButton(text)
                base_color = group["color"]
                btn.setStyleSheet(f"""
                    QPushButton {{ 
                        background-color: {base_color}; 
                        color: white; 
                        text-align: left; 
                        padding-left: 15px; 
                        border-radius: 4px;
                        min-width: 120px;
                        font-size: 14px;
                        padding: 8px;
                    }}
                    QPushButton:hover {{ background-color: {self.darken_color(base_color)}; }}
                """)
                btn.clicked.connect(callback)
                group_layout.addWidget(btn)
            
            button_layout.addWidget(group_container)
        control_layout.addWidget(button_box)
        main_layout.addWidget(control_panel, stretch=1)
        self.view = CustomGraphicsView(self)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        main_layout.addWidget(self.view, stretch=4)

        # 添加右上角图例注释
        self.legend_label = QLabel(self)
        self.legend_label.setStyleSheet("background: rgba(255,255,255,0.93); border-radius:8px; padding:10px; border:1px solid #ddd;")
        self.legend_label.setText(
            "<span style='font-size:30px; font-weight:bold;'>Color annotations</span><br>----------------<br>"
            "<span style='font-size:20px;'>Path Type</span><br>"
            "<span style='font-size:20px; color:#0000ff;'>■</span> <span style='font-size:20px;'>Normal Path</span><br>"
            "<span style='font-size:20px; color:#ff0000;'>■</span> <span style='font-size:20px;'>Shortest Path</span><br>"
            "<span style='font-size:20px; color:#00ff00;'>■</span> <span style='font-size:20px;'>Most Efficient Path</span><br>----------------<br>"
            "<span style='font-size:20px;'>Zone Type</span><br>"
            "<span style='font-size:20px; color:#ef5350;'>■</span> <span style='font-size:20px;'>Commercial</span><br>"
            "<span style='font-size:20px; color:#66bb6a;'>■</span> <span style='font-size:20px;'>Residential</span><br>"
            "<span style='font-size:20px; color:#42a5f5;'>■</span> <span style='font-size:20px;'>Industrial</span><br>"
            "<span style='font-size:20px; color:#ffca28;'>■</span> <span style='font-size:20px;'>Mixed</span>"
        )
        self.legend_label.setFixedWidth(320)
        self.legend_label.setFixedHeight(300)
        self.legend_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.legend_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.legend_label.raise_()
        self.update_legend_position()

    def darken_color(self, hex_color, amount=0.7):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(comp * amount)) for comp in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def clear_selection(self):
        self.selected_start = None
        self.selected_end = None
        self.all_paths = []
        self.best_path = []
        self.show_only_best_path = False
        # 清除路径属性
        if hasattr(self, 'shortest_path'):
            delattr(self, 'shortest_path')
        if hasattr(self, 'efficiency_path'):
            delattr(self, 'efficiency_path')
        if hasattr(self, 'shortest_distance'):
            delattr(self, 'shortest_distance')
        if hasattr(self, 'efficiency_distance'):
            delattr(self, 'efficiency_distance')
        if hasattr(self, 'efficiency_value'):
            delattr(self, 'efficiency_value')
        if hasattr(self, 'paths_are_same'):
            delattr(self, 'paths_are_same')
        self.info_label.setText("Click to select start and end points")
        self.path_info.setText("")
        self.draw_network()

    def handle_station_hover(self, pos):
        return self.interaction_handler.handle_station_hover(pos)

    def handle_station_click(self, pos):
        self.interaction_handler.handle_station_click(pos)

    def update_path_info(self):
        self.path_display.update_path_info()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_legend_position()

    def update_legend_position(self):
        margin = 20
        x = self.width() - self.legend_label.width() - margin
        y = margin
        self.legend_label.move(x, y)

    def save_data(self):
        """保存当前数据到CSV文件"""
        try:
            self.data_manager.save_data_to_csv()  # 调用数据管理器的保存方法
            QMessageBox.information(self, "Save Successful", "The data has been successfully saved to the default CSV file!")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"An error occurred while saving:{str(e)}")