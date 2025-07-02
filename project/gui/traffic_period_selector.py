from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtCore import pyqtSignal
from project.algorithms.traffic_condition_manager import TrafficConditionManager

class TrafficPeriodSelector(QWidget):
    """
    交通时段选择器，提供"早高峰/普通时段/晚高峰"切换功能
    """
    # 定义信号，当交通时段改变时触发
    periodChanged = pyqtSignal(str)
    
    def __init__(self, parent=None, traffic_manager=None):
        super().__init__(parent)
        self.traffic_manager = traffic_manager or TrafficConditionManager()
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 添加标签
        label = QLabel("Traffic hours:")
        label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(label)
        
        # 添加下拉框
        self.period_combo = QComboBox()
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                min-width: 150px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #ddd;
                border-left-style: solid;
            }
        """)
        
        # 添加选项
        self.period_combo.addItem(TrafficConditionManager.PEAK_MORNING)  # 早高峰
        self.period_combo.addItem(TrafficConditionManager.NORMAL)        # 普通时段
        self.period_combo.addItem(TrafficConditionManager.PEAK_EVENING)  # 晚高峰
        
        # 设置默认值
        self.period_combo.setCurrentText(self.traffic_manager.get_current_period())
        
        # 连接信号
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        
        layout.addWidget(self.period_combo)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setMaximumHeight(40)
        
    def on_period_changed(self, period):
        """当用户选择不同交通时段时触发"""
        self.traffic_manager.set_period(period)
        self.periodChanged.emit(period)
        
    def get_current_period(self):
        """获取当前选择的交通时段"""
        return self.period_combo.currentText() 