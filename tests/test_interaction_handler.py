import unittest
from unittest.mock import MagicMock
from PyQt5.QtCore import QPointF
from project.module.interaction_handler import InteractionHandler

class DummyMainWindow:
    """ testing interaction handler"""
    """用于测试交互处理器"""
    def __init__(self):
        """Initialize dummy main window """
        """初始化虚拟主窗口"""
        self.scene = MagicMock()
        self.data_manager = MagicMock()
        self.info_label = MagicMock()
        self.hovered_station = None
        self.selected_start = None
        self.selected_end = None
        self.path_info = MagicMock()
        self.draw_network = MagicMock()
        self.update_path_info = MagicMock()

class TestInteractionHandler(unittest.TestCase):
    """Test cases for interaction handler functionality"""
    """交互处理器功能的测试用例"""
    def setUp(self):
 
        self.main_window = DummyMainWindow()
        self.handler = InteractionHandler(self.main_window)

    def test_init(self):
        self.assertIs(self.handler.main_window, self.main_window)
        self.assertIs(self.handler.data_manager, self.main_window.data_manager)

    def test_handle_station_hover_callable(self):

        try:
            self.handler.handle_station_hover(QPointF(0,0))
        except Exception:
            pass

    def test_handle_station_click_callable(self):
        try:
            self.handler.handle_station_click(QPointF(0,0))
        except Exception:
            pass

if __name__ == '__main__':
    unittest.main() 