import sys
import os

# 获取项目根目录（向上三级）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 确保项目根目录在sys.path中
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from project.module.visualization import BusNetworkVisualization
from project.module.network_data import NetworkDataManager
from project.module.path_analysis import PathAnalyzer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data_manager = NetworkDataManager()
    path_analyzer = PathAnalyzer(data_manager)
    window = BusNetworkVisualization(data_manager, path_analyzer)
    window.show()
    sys.exit(app.exec_())