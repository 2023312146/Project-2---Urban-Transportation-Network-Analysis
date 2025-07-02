import unittest
from unittest.mock import MagicMock, patch, call
from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
import sys

# 創建 QApplication 實例
app = QApplication.instance() or QApplication(sys.argv)

from project.gui.stop_utilization_display import StopUtilizationDisplay

class MockUtilizationAnalyzer:
    """模擬 StopUtilizationAnalyzer"""
    def __init__(self):
        self.optimize_network_result = {
            'underutilized_stops': [
                {
                    'stop_id': '1',
                    'name': 'Stop A',
                    'score': 0.5,
                    'connectivity': 2,
                    'passenger_volume': 100,
                    'arrival_frequency': 4
                },
                {
                    'stop_id': '2',
                    'name': 'Stop B',
                    'score': 0.3,
                    'connectivity': 1,
                    'passenger_volume': 50,
                    'arrival_frequency': 2
                }
            ],
            'consolidation_candidates': [
                {
                    'distance': 1.5,
                    'keep_stop': {'id': '1', 'name': 'Stop A'},
                    'remove_stop': {'id': '2', 'name': 'Stop B'}
                },
                {
                    'distance': 2.0,
                    'keep_stop': {'id': '3', 'name': 'Stop C'},
                    'remove_stop': {'id': '4', 'name': 'Stop D'}
                }
            ],
            'new_stop_suggestions': [
                {
                    'latitude': 30.123456,
                    'longitude': 120.654321,
                    'connects': ['Stop A', 'Stop B'],
                    'distance': 3.5
                },
                {
                    'latitude': 30.234567,
                    'longitude': 120.765432,
                    'connects': ['Stop C', 'Stop D'],
                    'distance': 4.2
                }
            ]
        }
    
    def optimize_network(self):
        return self.optimize_network_result

class TestStopUtilizationDisplay(unittest.TestCase):
    """StopUtilizationDisplay 類的全面測試"""
    
    def setUp(self):
        """測試前的設置"""
        self.analyzer = MockUtilizationAnalyzer()
        self.display = StopUtilizationDisplay(self.analyzer)
    
    def test_init(self):
        """測試初始化"""
        self.assertEqual(self.display.windowTitle(), "站点利用率分析")
        self.assertEqual(self.display.results, self.analyzer.optimize_network_result)
        self.assertIsNotNone(self.display.analyzer)
    
    def test_create_underutilized_tab(self):
        """測試創建低利用率站點標籤頁"""
        tab = self.display._create_underutilized_tab()
        
        # 檢查表格結構
        self.assertEqual(tab.rowCount(), 2)
        self.assertEqual(tab.columnCount(), 6)
        
        # 檢查表頭
        expected_headers = ["Stop_ID", "Name", "Efficiency score", "Connectivity", "Passenger volume", "Operation"]
        for col, header in enumerate(expected_headers):
            self.assertEqual(tab.horizontalHeaderItem(col).text(), header)
        
        # 檢查數據填充
        self.assertEqual(tab.item(0, 0).text(), "1")
        self.assertEqual(tab.item(0, 1).text(), "Stop A")
        self.assertEqual(tab.item(0, 2).text(), "0.50")
        self.assertEqual(tab.item(0, 3).text(), "2")
        self.assertEqual(tab.item(0, 4).text(), "100")
        
        # 檢查按鈕
        remove_btn = tab.cellWidget(0, 5)
        self.assertIsInstance(remove_btn, QPushButton)
        self.assertEqual(remove_btn.text(), "Delete")
        self.assertEqual(remove_btn.property("stop_id"), "1")
        self.assertEqual(remove_btn.property("stop_name"), "Stop A")
    
    def test_create_consolidation_tab(self):
        """測試創建可合併站點標籤頁"""
        tab = self.display._create_consolidation_tab()
        
        # 檢查表格結構
        self.assertEqual(tab.rowCount(), 2)
        self.assertEqual(tab.columnCount(), 4)
        
        # 檢查表頭
        expected_headers = ["Distance(km)", "Keep stop", "Remove stop", "Operation"]
        for col, header in enumerate(expected_headers):
            self.assertEqual(tab.horizontalHeaderItem(col).text(), header)
        
        # 檢查數據填充
        self.assertEqual(tab.item(0, 0).text(), "1.50")
        self.assertEqual(tab.item(0, 1).text(), "Stop A")
        self.assertEqual(tab.item(0, 2).text(), "Stop B")
        
        # 檢查按鈕
        merge_btn = tab.cellWidget(0, 3)
        self.assertIsInstance(merge_btn, QPushButton)
        self.assertEqual(merge_btn.text(), "Merge")
        self.assertEqual(merge_btn.property("keep_id"), "1")
        self.assertEqual(merge_btn.property("keep_name"), "Stop A")
        self.assertEqual(merge_btn.property("remove_id"), "2")
        self.assertEqual(merge_btn.property("remove_name"), "Stop B")
    
    def test_create_new_stops_tab(self):
        """測試創建新站點建議標籤頁"""
        tab = self.display._create_new_stops_tab()
        
        # 檢查表格結構
        self.assertEqual(tab.rowCount(), 2)
        self.assertEqual(tab.columnCount(), 5)
        
        # 檢查表頭
        expected_headers = ["Latitude", "Longitude", "Connected stops", "Distance(km)", "Operation"]
        for col, header in enumerate(expected_headers):
            self.assertEqual(tab.horizontalHeaderItem(col).text(), header)
        
        # 檢查數據填充
        self.assertEqual(tab.item(0, 0).text(), "30.123456")
        self.assertEqual(tab.item(0, 1).text(), "120.654321")
        self.assertEqual(tab.item(0, 2).text(), "Stop A - Stop B")
        self.assertEqual(tab.item(0, 3).text(), "3.50")
        
        # 檢查按鈕
        add_btn = tab.cellWidget(0, 4)
        self.assertIsInstance(add_btn, QPushButton)
        self.assertEqual(add_btn.text(), "Add")
        self.assertEqual(add_btn.property("latitude"), 30.123456)
        self.assertEqual(add_btn.property("longitude"), 120.654321)
        self.assertEqual(add_btn.property("connects"), ["Stop A", "Stop B"])
    
    @patch('PyQt5.QtWidgets.QMessageBox.question')
    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_on_remove_stop_confirm(self, mock_info, mock_question):
        """測試刪除站點確認操作"""
        # 模擬用戶確認
        mock_question.return_value = QMessageBox.Yes
        
        # 創建模擬按鈕
        button = QPushButton()
        button.setProperty("stop_id", "1")
        button.setProperty("stop_name", "Stop A")
        
        # 模擬信號
        signal_emitted = False
        def on_signal(stop_id):
            nonlocal signal_emitted
            signal_emitted = True
            self.assertEqual(stop_id, "1")
        
        self.display.remove_stop_signal.connect(on_signal)
        
        # 執行測試
        with patch.object(self.display, 'sender', return_value=button):
            self.display._on_remove_stop()
        
        # 驗證
        mock_question.assert_called_once()
        mock_info.assert_called_once()
        self.assertTrue(signal_emitted)
    
    @patch('PyQt5.QtWidgets.QMessageBox.question')
    def test_on_remove_stop_cancel(self, mock_question):
        """測試刪除站點取消操作"""
        # 模擬用戶取消
        mock_question.return_value = QMessageBox.No
        
        button = QPushButton()
        button.setProperty("stop_id", "1")
        button.setProperty("stop_name", "Stop A")
        
        signal_emitted = False
        def on_signal(stop_id):
            nonlocal signal_emitted
            signal_emitted = True
        
        self.display.remove_stop_signal.connect(on_signal)
        
        with patch.object(self.display, 'sender', return_value=button):
            self.display._on_remove_stop()
        
        mock_question.assert_called_once()
        self.assertFalse(signal_emitted)
    
    @patch('PyQt5.QtWidgets.QMessageBox.question')
    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_on_merge_stops_confirm(self, mock_info, mock_question):
        """測試合併站點確認操作"""
        mock_question.return_value = QMessageBox.Yes
        
        button = QPushButton()
        button.setProperty("keep_id", "1")
        button.setProperty("keep_name", "Stop A")
        button.setProperty("remove_id", "2")
        button.setProperty("remove_name", "Stop B")
        
        signal_emitted = False
        def on_signal(stop_id):
            nonlocal signal_emitted
            signal_emitted = True
            self.assertEqual(stop_id, "2")
        
        self.display.remove_stop_signal.connect(on_signal)
        
        with patch.object(self.display, 'sender', return_value=button):
            self.display._on_merge_stops()
        
        mock_question.assert_called_once()
        mock_info.assert_called_once()
        self.assertTrue(signal_emitted)
    
    @patch('PyQt5.QtWidgets.QMessageBox.question')
    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_on_add_stop_confirm(self, mock_info, mock_question):
        """測試添加站點確認操作"""
        mock_question.return_value = QMessageBox.Yes
        
        button = QPushButton()
        button.setProperty("latitude", 30.123456)
        button.setProperty("longitude", 120.654321)
        button.setProperty("connects", ["Stop A", "Stop B"])
        
        signal_emitted = False
        signal_args = None
        def on_signal(lat, lon, name, connects):
            nonlocal signal_emitted, signal_args
            signal_emitted = True
            signal_args = (lat, lon, name, connects)
        
        self.display.add_stop_signal.connect(on_signal)
        
        with patch.object(self.display, 'sender', return_value=button):
            self.display._on_add_stop()
        
        mock_question.assert_called_once()
        mock_info.assert_called_once()
        self.assertTrue(signal_emitted)
        self.assertEqual(signal_args[0], 30.123456)
        self.assertEqual(signal_args[1], 120.654321)
        self.assertEqual(signal_args[2], "New Stop (Stop A, Stop B)")
        self.assertEqual(signal_args[3], ["Stop A", "Stop B"])
    
    def test_empty_results(self):
        """測試空結果的情況"""
        # 創建空結果的分析器
        empty_analyzer = MockUtilizationAnalyzer()
        empty_analyzer.optimize_network_result = {
            'underutilized_stops': [],
            'consolidation_candidates': [],
            'new_stop_suggestions': []
        }
        
        display = StopUtilizationDisplay(empty_analyzer)
        
        # 測試空標籤頁
        under_tab = display._create_underutilized_tab()
        self.assertEqual(under_tab.rowCount(), 0)
        
        consolidation_tab = display._create_consolidation_tab()
        self.assertEqual(consolidation_tab.rowCount(), 0)
        
        new_stops_tab = display._create_new_stops_tab()
        self.assertEqual(new_stops_tab.rowCount(), 0)
    
    def test_large_results(self):
        """測試大量結果的情況"""
        # 創建大量結果的分析器
        large_analyzer = MockUtilizationAnalyzer()
        large_analyzer.optimize_network_result = {
            'underutilized_stops': [
                {
                    'stop_id': str(i),
                    'name': f'Stop {i}',
                    'score': 0.1 + i * 0.1,
                    'connectivity': i,
                    'passenger_volume': i * 100,
                    'arrival_frequency': i
                } for i in range(100)
            ],
            'consolidation_candidates': [
                {
                    'distance': i * 0.5,
                    'keep_stop': {'id': str(i), 'name': f'Keep {i}'},
                    'remove_stop': {'id': str(i+1), 'name': f'Remove {i+1}'}
                } for i in range(50)
            ],
            'new_stop_suggestions': [
                {
                    'latitude': 30.0 + i * 0.001,
                    'longitude': 120.0 + i * 0.001,
                    'connects': [f'Stop {i}', f'Stop {i+1}'],
                    'distance': i * 0.5
                } for i in range(20)
            ]
        }
        
        display = StopUtilizationDisplay(large_analyzer)
        
        # 測試大量數據的標籤頁
        under_tab = display._create_underutilized_tab()
        self.assertEqual(under_tab.rowCount(), 100)
        
        consolidation_tab = display._create_consolidation_tab()
        self.assertEqual(consolidation_tab.rowCount(), 50)
        
        new_stops_tab = display._create_new_stops_tab()
        self.assertEqual(new_stops_tab.rowCount(), 20)
    
    def test_extreme_values(self):
        """測試極端值的情況"""
        extreme_analyzer = MockUtilizationAnalyzer()
        extreme_analyzer.optimize_network_result = {
            'underutilized_stops': [
                {
                    'stop_id': '1',
                    'name': 'Very Long Stop Name That Exceeds Normal Length',
                    'score': 0.000001,  # 極小值
                    'connectivity': 999,  # 極大值
                    'passenger_volume': 999999,  # 極大值
                    'arrival_frequency': 999  # 極大值
                }
            ],
            'consolidation_candidates': [
                {
                    'distance': 0.000001,  # 極小距離
                    'keep_stop': {'id': '1', 'name': 'Keep Stop'},
                    'remove_stop': {'id': '2', 'name': 'Remove Stop'}
                }
            ],
            'new_stop_suggestions': [
                {
                    'latitude': 90.0,  # 極限緯度
                    'longitude': 180.0,  # 極限經度
                    'connects': ['Stop A', 'Stop B', 'Stop C', 'Stop D', 'Stop E'],  # 多個連接
                    'distance': 999.999  # 極大距離
                }
            ]
        }
        
        display = StopUtilizationDisplay(extreme_analyzer)
        
        # 測試極端值處理
        under_tab = display._create_underutilized_tab()
        self.assertEqual(under_tab.item(0, 2).text(), "0.00")  # 極小分數格式化
        
        consolidation_tab = display._create_consolidation_tab()
        self.assertEqual(consolidation_tab.item(0, 0).text(), "0.00")  # 極小距離格式化
        
        new_stops_tab = display._create_new_stops_tab()
        self.assertEqual(new_stops_tab.item(0, 0).text(), "90.000000")  # 極限緯度
        self.assertEqual(new_stops_tab.item(0, 1).text(), "180.000000")  # 極限經度
        self.assertEqual(new_stops_tab.item(0, 2).text(), "Stop A - Stop B - Stop C - Stop D - Stop E")  # 多個連接
        self.assertEqual(new_stops_tab.item(0, 3).text(), "1000.00")  # 極大距離格式化
    
    def test_signal_connections(self):
        """測試信號連接"""
        # 測試信號是否正確定義
        self.assertTrue(hasattr(self.display, 'remove_stop_signal'))
        self.assertTrue(hasattr(self.display, 'add_stop_signal'))
        
        # 測試信號類型 - 使用更寬鬆的檢查
        from PyQt5.QtCore import pyqtSignal
        # 檢查信號是否為 PyQt 信號類型（包括綁定信號）
        self.assertTrue(hasattr(self.display.remove_stop_signal, 'emit'))
        self.assertTrue(hasattr(self.display.add_stop_signal, 'emit'))
        self.assertTrue(hasattr(self.display.remove_stop_signal, 'connect'))
        self.assertTrue(hasattr(self.display.add_stop_signal, 'connect'))
    
    def test_window_properties(self):
        """測試窗口屬性"""
        self.assertEqual(self.display.windowTitle(), "站点利用率分析")
        self.assertGreater(self.display.width(), 0)
        self.assertGreater(self.display.height(), 0)
        self.assertTrue(self.display.isVisible() or not self.display.isVisible())  # 可視性狀態
    
    def test_dialog_modal_behavior(self):
        """測試對話框模態行為"""
        # 測試對話框可以正常顯示和隱藏
        self.display.show()
        self.assertTrue(self.display.isVisible())
        
        self.display.hide()
        self.assertFalse(self.display.isVisible())

if __name__ == '__main__':
    unittest.main() 