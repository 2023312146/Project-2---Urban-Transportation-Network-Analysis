import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor
from project.module.BusPathPlannerGUI import BusNetworkVisualization
from project.module.NetworkDataManager import NetworkDataManager
from project.module.RouteAnalyzer import PathAnalyzer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data_manager = NetworkDataManager()
    path_analyzer = PathAnalyzer(data_manager)
    window = BusNetworkVisualization(data_manager, path_analyzer)
    # 添加路径颜色初始化
    window.path_colors = [
        QColor(255, 255, 0),   # 黄色
        QColor(0, 255, 0),     # 绿色
        QColor(0, 255, 255),   # 青色
        QColor(255, 0, 255),   # 紫色
        QColor(255, 165, 0),   # 橙色
        QColor(0, 0, 255),     # 蓝色
        QColor(255, 192, 203)  # 粉色
    ]
    window.show()
    sys.exit(app.exec_())