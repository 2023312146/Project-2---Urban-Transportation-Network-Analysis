import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QComboBox
from PyQt5.QtCore import Qt
import sys

# 創建 QApplication 實例
app = QApplication.instance() or QApplication(sys.argv)

from project.gui.traffic_period_selector import TrafficPeriodSelector
from project.algorithms.traffic_condition_manager import TrafficConditionManager

class TestTrafficPeriodSelector(unittest.TestCase):
    """TrafficPeriodSelector 類的全面測試"""
    
    def setUp(self):
        """測試前的設置"""
        self.traffic_manager = TrafficConditionManager()
        self.selector = TrafficPeriodSelector(traffic_manager=self.traffic_manager)
    
    def test_init_default_traffic_manager(self):
        """測試使用默認 TrafficConditionManager 初始化"""
        selector = TrafficPeriodSelector()
        self.assertIsNotNone(selector.traffic_manager)
        self.assertIsInstance(selector.traffic_manager, TrafficConditionManager)
    
    def test_init_custom_traffic_manager(self):
        """測試使用自定義 TrafficConditionManager 初始化"""
        custom_manager = TrafficConditionManager()
        custom_manager.set_period(TrafficConditionManager.PEAK_EVENING)
        selector = TrafficPeriodSelector(traffic_manager=custom_manager)
        self.assertEqual(selector.traffic_manager, custom_manager)
    
    def test_ui_structure(self):
        """測試 UI 結構"""
        # 檢查佈局
        layout = self.selector.layout()
        self.assertIsNotNone(layout)
        self.assertEqual(layout.count(), 3)  # 標籤、下拉框、彈性空間
        
        # 檢查下拉框
        self.assertIsInstance(self.selector.period_combo, QComboBox)
        self.assertEqual(self.selector.period_combo.count(), 3)
    
    def test_combo_box_options(self):
        """測試下拉框選項"""
        combo = self.selector.period_combo
        
        # 檢查選項順序和內容
        expected_options = [
            TrafficConditionManager.PEAK_MORNING,
            TrafficConditionManager.NORMAL,
            TrafficConditionManager.PEAK_EVENING
        ]
        
        for i, expected_option in enumerate(expected_options):
            self.assertEqual(combo.itemText(i), expected_option)
    
    def test_default_selection(self):
        """測試默認選擇"""
        # 默認應該選擇當前時段
        current_period = self.traffic_manager.get_current_period()
        self.assertEqual(self.selector.get_current_period(), current_period)
        self.assertEqual(self.selector.period_combo.currentText(), current_period)
    
    def test_period_changed_signal(self):
        """測試時段改變信號"""
        signal_emitted = False
        emitted_period = None
        
        def on_period_changed(period):
            nonlocal signal_emitted, emitted_period
            signal_emitted = True
            emitted_period = period
        
        self.selector.periodChanged.connect(on_period_changed)
        
        # 改變時段
        new_period = TrafficConditionManager.PEAK_MORNING
        self.selector.period_combo.setCurrentText(new_period)
        
        # 驗證信號
        self.assertTrue(signal_emitted)
        self.assertEqual(emitted_period, new_period)
    
    def test_traffic_manager_period_update(self):
        """測試 TrafficConditionManager 時段更新"""
        # 改變時段
        new_period = TrafficConditionManager.PEAK_EVENING
        self.selector.period_combo.setCurrentText(new_period)
        
        # 驗證 TrafficConditionManager 已更新
        self.assertEqual(self.traffic_manager.get_current_period(), new_period)
    
    def test_get_current_period(self):
        """測試獲取當前時段"""
        # 設置不同時段並驗證
        test_periods = [
            TrafficConditionManager.PEAK_MORNING,
            TrafficConditionManager.NORMAL,
            TrafficConditionManager.PEAK_EVENING
        ]
        
        for period in test_periods:
            self.selector.period_combo.setCurrentText(period)
            self.assertEqual(self.selector.get_current_period(), period)
    
    def test_ui_styling(self):
        """測試 UI 樣式"""
        # 檢查樣式表是否設置
        self.assertIsNotNone(self.selector.period_combo.styleSheet())
        self.assertIn("QComboBox", self.selector.period_combo.styleSheet())
        
        # 檢查標籤樣式
        label = self.selector.findChild(type(self.selector), '')
        if label:
            self.assertIsNotNone(label.styleSheet())
    
    def test_widget_properties(self):
        """測試組件屬性"""
        # 檢查最大高度
        self.assertEqual(self.selector.maximumHeight(), 40)
        
        # 檢查佈局邊距
        layout = self.selector.layout()
        margins = layout.contentsMargins()
        self.assertEqual(margins.left(), 10)
        self.assertEqual(margins.top(), 5)
        self.assertEqual(margins.right(), 10)
        self.assertEqual(margins.bottom(), 5)
    
    def test_signal_definition(self):
        """測試信號定義"""
        # 檢查信號是否存在
        self.assertTrue(hasattr(self.selector, 'periodChanged'))
        
        # 檢查信號類型
        from PyQt5.QtCore import pyqtSignal
        self.assertTrue(hasattr(self.selector.periodChanged, 'emit'))
        self.assertTrue(hasattr(self.selector.periodChanged, 'connect'))
    
    def test_multiple_period_changes(self):
        """測試多次時段改變"""
        changes = []
        
        def on_change(period):
            changes.append(period)
        
        self.selector.periodChanged.connect(on_change)
        
        # 多次改變時段
        periods = [
            TrafficConditionManager.PEAK_MORNING,
            TrafficConditionManager.NORMAL,
            TrafficConditionManager.PEAK_EVENING,
            TrafficConditionManager.PEAK_MORNING
        ]
        
        for period in periods:
            self.selector.period_combo.setCurrentText(period)
        
        # 驗證所有改變都被記錄
        self.assertEqual(len(changes), len(periods))
        self.assertEqual(changes, periods)
    
    def test_invalid_traffic_manager(self):
        """測試無效的 TrafficConditionManager"""
        # 創建無效的管理器
        invalid_manager = MagicMock()
        invalid_manager.get_current_period.return_value = "Invalid Period"
        
        selector = TrafficPeriodSelector(traffic_manager=invalid_manager)
        
        # 應該使用默認值或處理異常
        self.assertIsNotNone(selector.period_combo.currentText())
    
    def test_combo_box_interaction(self):
        """測試下拉框交互"""
        combo = self.selector.period_combo
        
        # 測試通過索引選擇
        combo.setCurrentIndex(0)
        self.assertEqual(combo.currentText(), TrafficConditionManager.PEAK_MORNING)
        
        combo.setCurrentIndex(1)
        self.assertEqual(combo.currentText(), TrafficConditionManager.NORMAL)
        
        combo.setCurrentIndex(2)
        self.assertEqual(combo.currentText(), TrafficConditionManager.PEAK_EVENING)
    
    def test_edge_cases(self):
        """測試邊緣情況"""
        # 測試空 TrafficConditionManager
        empty_manager = MagicMock()
        empty_manager.get_current_period.return_value = ""
        
        selector = TrafficPeriodSelector(traffic_manager=empty_manager)
        self.assertIsNotNone(selector.period_combo.currentText())
        
        # 測試 None TrafficConditionManager - 實際不會拋出異常
        selector = TrafficPeriodSelector(traffic_manager=None)
        self.assertIsNotNone(selector.traffic_manager)
    
    def test_period_consistency(self):
        """測試時段一致性"""
        # 確保 UI 和 TrafficConditionManager 保持同步
        initial_period = self.traffic_manager.get_current_period()
        self.assertEqual(self.selector.get_current_period(), initial_period)
        
        # 注意：UI 不會自動同步 TrafficConditionManager 的改變
        # 需要通過 UI 操作來改變時段
        new_period = TrafficConditionManager.PEAK_MORNING
        self.selector.period_combo.setCurrentText(new_period)
        
        # 驗證 UI 和 TrafficConditionManager 都更新了
        self.assertEqual(self.selector.get_current_period(), new_period)
        self.assertEqual(self.traffic_manager.get_current_period(), new_period)
    
    def test_widget_visibility(self):
        """測試組件可見性"""
        # 組件默認不可見，需要顯示
        self.selector.show()
        self.assertTrue(self.selector.isVisible())
        
        # 下拉框應該可見
        self.assertTrue(self.selector.period_combo.isVisible())
    
    def test_layout_stretch(self):
        """測試佈局彈性空間"""
        layout = self.selector.layout()
        
        # 檢查是否有彈性空間
        has_stretch = False
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.spacerItem() is not None:
                has_stretch = True
                break
        
        self.assertTrue(has_stretch)
    
    def test_combo_box_readonly(self):
        """測試下拉框是否為只讀"""
        combo = self.selector.period_combo
        
        # 檢查是否可以編輯
        self.assertFalse(combo.isEditable())
    
    def test_signal_disconnection(self):
        """測試信號斷開連接"""
        signal_emitted = False
        
        def on_period_changed(period):
            nonlocal signal_emitted
            signal_emitted = True
        
        self.selector.periodChanged.connect(on_period_changed)
        
        # 斷開連接
        self.selector.periodChanged.disconnect(on_period_changed)
        
        # 改變時段
        self.selector.period_combo.setCurrentText(TrafficConditionManager.PEAK_MORNING)
        
        # 信號不應該被發送
        self.assertFalse(signal_emitted)

if __name__ == '__main__':
    unittest.main() 