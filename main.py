import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from project.gui.main_window_gui_builder import GUIBuilder
from project.core.csv_network_data_manager import NetworkDataManager
from project.analysis.network_path_analyzer import PathAnalyzer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data_manager = NetworkDataManager()
    
    path_analyzer = PathAnalyzer(data_manager)
    window = GUIBuilder(data_manager, path_analyzer)
    window.drawing_module.init_scene()
    window.drawing_module.draw_network()
    
    window.show()
    sys.exit(app.exec_())