import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from project.module.gui_builder import GUIBuilder
from project.module.NetworkDataManager import NetworkDataManager
from project.module.RouteAnalyzer import PathAnalyzer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data_manager = NetworkDataManager()
    
    path_analyzer = PathAnalyzer(data_manager)
    window = GUIBuilder(data_manager, path_analyzer)
    window.show()
    sys.exit(app.exec_())