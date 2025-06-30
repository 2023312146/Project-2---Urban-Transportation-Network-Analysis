import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication, QLabel
from project.gui.gui_builder import GUIBuilder
from project.core.NetworkDataManager import NetworkDataManager
from project.analysis.RouteAnalyzer import PathAnalyzer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data_manager = NetworkDataManager()
    
    path_analyzer = PathAnalyzer(data_manager)
    window = GUIBuilder(data_manager, path_analyzer)
    window.show()
    sys.exit(app.exec_())