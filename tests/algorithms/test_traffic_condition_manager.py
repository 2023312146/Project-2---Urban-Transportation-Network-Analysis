import unittest
from unittest.mock import MagicMock, patch
from project.algorithms.traffic_condition_manager import TrafficConditionManager

class TestTrafficConditionManager(unittest.TestCase):
    """TrafficConditionManager 類的全面測試"""
    
    def setUp(self):
        """測試前的設置"""
        self.traffic_manager = TrafficConditionManager()

    def test_init_default_values(self):
        """測試初始化默認值"""
        self.assertEqual(self.traffic_manager.period, TrafficConditionManager.NORMAL)
        self.assertEqual(self.traffic_manager.base_speed, 23)
        self.assertEqual(self.traffic_manager.congestion_wait_time, 2)
        self.assertEqual(self.traffic_manager.congestion_speed, 15)

    def test_set_period_valid_periods(self):
        """測試設置有效時段"""
        # 測試設置早高峰
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        self.assertEqual(self.traffic_manager.period, TrafficConditionManager.PEAK_MORNING)
        
        # 測試設置普通時段
        self.traffic_manager.set_period(TrafficConditionManager.NORMAL)
        self.assertEqual(self.traffic_manager.period, TrafficConditionManager.NORMAL)
        
        # 測試設置晚高峰
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_EVENING)
        self.assertEqual(self.traffic_manager.period, TrafficConditionManager.PEAK_EVENING)

    def test_set_period_invalid_period(self):
        """測試設置無效時段"""
        invalid_periods = [
            "invalid_period",
            "morning",
            "evening",
            "peak",
            "",
            None,
            123,
            []
        ]
        
        for invalid_period in invalid_periods:
            with self.assertRaises(ValueError) as context:
                self.traffic_manager.set_period(invalid_period)
            self.assertIn("无效的时段", str(context.exception))

    def test_set_period_case_sensitivity(self):
        """測試時段設置的大小寫敏感性"""
        # 測試大小寫不匹配
        with self.assertRaises(ValueError):
            self.traffic_manager.set_period("morning rush hour")
        
        with self.assertRaises(ValueError):
            self.traffic_manager.set_period("MORNING RUSH HOUR")
        
        with self.assertRaises(ValueError):
            self.traffic_manager.set_period("Morning Rush Hour")

    def test_get_area_congestion_normal_period(self):
        """測試普通時段的區域擁堵狀態"""
        self.traffic_manager.set_period(TrafficConditionManager.NORMAL)
        
        # 普通時段所有區域都不擁堵
        area_types = [
            TrafficConditionManager.RESIDENTIAL,
            TrafficConditionManager.COMMERCIAL,
            TrafficConditionManager.INDUSTRIAL,
            TrafficConditionManager.MIXED
        ]
        
        for area_type in area_types:
            self.assertFalse(self.traffic_manager.get_area_congestion(area_type))

    def test_get_area_congestion_morning_peak(self):
        """測試早高峰時段的區域擁堵狀態"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        
        # 早高峰只有住宅區擁堵
        self.assertTrue(self.traffic_manager.get_area_congestion(TrafficConditionManager.RESIDENTIAL))
        self.assertFalse(self.traffic_manager.get_area_congestion(TrafficConditionManager.COMMERCIAL))
        self.assertFalse(self.traffic_manager.get_area_congestion(TrafficConditionManager.INDUSTRIAL))
        self.assertFalse(self.traffic_manager.get_area_congestion(TrafficConditionManager.MIXED))

    def test_get_area_congestion_evening_peak(self):
        """測試晚高峰時段的區域擁堵狀態"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_EVENING)
        
        # 晚高峰商業區和工業區擁堵
        self.assertFalse(self.traffic_manager.get_area_congestion(TrafficConditionManager.RESIDENTIAL))
        self.assertTrue(self.traffic_manager.get_area_congestion(TrafficConditionManager.COMMERCIAL))
        self.assertTrue(self.traffic_manager.get_area_congestion(TrafficConditionManager.INDUSTRIAL))
        self.assertFalse(self.traffic_manager.get_area_congestion(TrafficConditionManager.MIXED))

    def test_get_area_congestion_case_insensitive(self):
        """測試區域類型的大小寫不敏感性"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        
        # 測試不同大小寫
        self.assertTrue(self.traffic_manager.get_area_congestion("RESIDENTIAL"))
        self.assertTrue(self.traffic_manager.get_area_congestion("Residential"))
        self.assertTrue(self.traffic_manager.get_area_congestion("residential"))
        self.assertTrue(self.traffic_manager.get_area_congestion("ResIdEnTiAl"))

    def test_get_area_congestion_invalid_area_types(self):
        """測試無效區域類型"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        
        # 測試無效字符串區域類型（應該返回 False）
        invalid_string_area_types = [
            "invalid_area",
            "suburban",
            "downtown",
            ""
        ]
        
        for invalid_area_type in invalid_string_area_types:
            # 無效區域類型應該返回 False
            self.assertFalse(self.traffic_manager.get_area_congestion(invalid_area_type))
        
        # 測試 None 和其他非字符串類型（應該拋出 AttributeError）
        invalid_non_string_types = [
            None,
            123,
            []
        ]
        
        for invalid_area_type in invalid_non_string_types:
            with self.assertRaises(AttributeError):
                self.traffic_manager.get_area_congestion(invalid_area_type)

    def test_get_wait_time_normal_period(self):
        """測試普通時段的等待時間"""
        self.traffic_manager.set_period(TrafficConditionManager.NORMAL)
        
        expected_wait_times = {
            TrafficConditionManager.RESIDENTIAL: 2,
            TrafficConditionManager.COMMERCIAL: 4,
            TrafficConditionManager.INDUSTRIAL: 3,
            TrafficConditionManager.MIXED: 3
        }
        
        for area_type, expected_time in expected_wait_times.items():
            actual_time = self.traffic_manager.get_wait_time(area_type)
            self.assertEqual(actual_time, expected_time)

    def test_get_wait_time_morning_peak(self):
        """測試早高峰時段的等待時間"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        
        expected_wait_times = {
            TrafficConditionManager.RESIDENTIAL: 4,
            TrafficConditionManager.COMMERCIAL: 4,
            TrafficConditionManager.INDUSTRIAL: 3,
            TrafficConditionManager.MIXED: 3
        }
        
        for area_type, expected_time in expected_wait_times.items():
            actual_time = self.traffic_manager.get_wait_time(area_type)
            self.assertEqual(actual_time, expected_time)

    def test_get_wait_time_evening_peak(self):
        """測試晚高峰時段的等待時間"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_EVENING)
        
        expected_wait_times = {
            TrafficConditionManager.RESIDENTIAL: 2,
            TrafficConditionManager.COMMERCIAL: 6,
            TrafficConditionManager.INDUSTRIAL: 5,
            TrafficConditionManager.MIXED: 3
        }
        
        for area_type, expected_time in expected_wait_times.items():
            actual_time = self.traffic_manager.get_wait_time(area_type)
            self.assertEqual(actual_time, expected_time)

    def test_get_wait_time_case_insensitive(self):
        """測試等待時間計算的大小寫不敏感性"""
        self.traffic_manager.set_period(TrafficConditionManager.NORMAL)
        
        # 測試不同大小寫應該返回相同的等待時間
        base_time = self.traffic_manager.get_wait_time("residential")
        self.assertEqual(self.traffic_manager.get_wait_time("RESIDENTIAL"), base_time)
        self.assertEqual(self.traffic_manager.get_wait_time("Residential"), base_time)
        self.assertEqual(self.traffic_manager.get_wait_time("ResIdEnTiAl"), base_time)

    def test_get_wait_time_invalid_area_types(self):
        """測試無效區域類型的等待時間"""
        self.traffic_manager.set_period(TrafficConditionManager.NORMAL)
        
        # 無效字符串區域類型應該返回混合區域的默認等待時間
        default_wait_time = self.traffic_manager.get_wait_time(TrafficConditionManager.MIXED)
        
        invalid_string_area_types = [
            "invalid_area",
            "suburban",
            "downtown",
            ""
        ]
        
        for invalid_area_type in invalid_string_area_types:
            actual_time = self.traffic_manager.get_wait_time(invalid_area_type)
            self.assertEqual(actual_time, default_wait_time)
        
        # 測試 None 和其他非字符串類型（應該拋出 AttributeError）
        invalid_non_string_types = [
            None,
            123,
            []
        ]
        
        for invalid_area_type in invalid_non_string_types:
            with self.assertRaises(AttributeError):
                self.traffic_manager.get_wait_time(invalid_area_type)

    def test_get_speed_normal_period(self):
        """測試普通時段的速度"""
        self.traffic_manager.set_period(TrafficConditionManager.NORMAL)
        
        # 普通時段無論是否進出高峰區域，速度都是正常速度
        area_types = [
            TrafficConditionManager.RESIDENTIAL,
            TrafficConditionManager.COMMERCIAL,
            TrafficConditionManager.INDUSTRIAL,
            TrafficConditionManager.MIXED
        ]
        
        for area_type in area_types:
            # 測試不進出高峰區域
            speed = self.traffic_manager.get_speed(area_type, False)
            self.assertEqual(speed, 23)
            
            # 測試進出高峰區域
            speed = self.traffic_manager.get_speed(area_type, True)
            self.assertEqual(speed, 23)

    def test_get_speed_peak_periods(self):
        """測試高峰時段的速度"""
        # 測試早高峰
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        
        area_types = [
            TrafficConditionManager.RESIDENTIAL,
            TrafficConditionManager.COMMERCIAL,
            TrafficConditionManager.INDUSTRIAL,
            TrafficConditionManager.MIXED
        ]
        
        for area_type in area_types:
            # 測試不進出高峰區域
            speed = self.traffic_manager.get_speed(area_type, False)
            self.assertEqual(speed, 23)
            
            # 測試進出高峰區域
            speed = self.traffic_manager.get_speed(area_type, True)
            self.assertEqual(speed, 15)
        
        # 測試晚高峰
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_EVENING)
        
        for area_type in area_types:
            # 測試不進出高峰區域
            speed = self.traffic_manager.get_speed(area_type, False)
            self.assertEqual(speed, 23)
            
            # 測試進出高峰區域
            speed = self.traffic_manager.get_speed(area_type, True)
            self.assertEqual(speed, 15)

    def test_get_speed_invalid_area_types(self):
        """測試無效區域類型的速度"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        
        invalid_area_types = [
            "invalid_area",
            "suburban",
            "downtown",
            "",
            None,
            123,
            []
        ]
        
        for invalid_area_type in invalid_area_types:
            # 無效區域類型應該返回正常速度
            speed = self.traffic_manager.get_speed(invalid_area_type, False)
            self.assertEqual(speed, 23)
            
            # 進出高峰區域時應該返回擁堵速度
            speed = self.traffic_manager.get_speed(invalid_area_type, True)
            self.assertEqual(speed, 15)

    def test_get_current_period(self):
        """測試獲取當前時段"""
        # 測試默認時段
        self.assertEqual(self.traffic_manager.get_current_period(), TrafficConditionManager.NORMAL)
        
        # 測試設置後的時段
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        self.assertEqual(self.traffic_manager.get_current_period(), TrafficConditionManager.PEAK_MORNING)
        
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_EVENING)
        self.assertEqual(self.traffic_manager.get_current_period(), TrafficConditionManager.PEAK_EVENING)

    def test_get_edge_speed_normal_period(self):
        """測試普通時段的邊速度"""
        self.traffic_manager.set_period(TrafficConditionManager.NORMAL)
        
        # 普通時段所有邊的速度都是正常速度
        area_types = [
            TrafficConditionManager.RESIDENTIAL,
            TrafficConditionManager.COMMERCIAL,
            TrafficConditionManager.INDUSTRIAL,
            TrafficConditionManager.MIXED
        ]
        
        for from_area in area_types:
            for to_area in area_types:
                speed = self.traffic_manager.get_edge_speed(from_area, to_area)
                self.assertEqual(speed, 23)

    def test_get_edge_speed_morning_peak(self):
        """測試早高峰時段的邊速度"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        
        # 早高峰住宅區擁堵
        # 從住宅區出發的邊
        speed = self.traffic_manager.get_edge_speed(TrafficConditionManager.RESIDENTIAL, TrafficConditionManager.COMMERCIAL)
        self.assertEqual(speed, 15)
        
        # 到住宅區的邊
        speed = self.traffic_manager.get_edge_speed(TrafficConditionManager.COMMERCIAL, TrafficConditionManager.RESIDENTIAL)
        self.assertEqual(speed, 15)
        
        # 住宅區到住宅區的邊
        speed = self.traffic_manager.get_edge_speed(TrafficConditionManager.RESIDENTIAL, TrafficConditionManager.RESIDENTIAL)
        self.assertEqual(speed, 15)
        
        # 非住宅區之間的邊
        speed = self.traffic_manager.get_edge_speed(TrafficConditionManager.COMMERCIAL, TrafficConditionManager.INDUSTRIAL)
        self.assertEqual(speed, 23)

    def test_get_edge_speed_evening_peak(self):
        """測試晚高峰時段的邊速度"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_EVENING)
        
        # 晚高峰商業區和工業區擁堵
        # 從商業區出發的邊
        speed = self.traffic_manager.get_edge_speed(TrafficConditionManager.COMMERCIAL, TrafficConditionManager.RESIDENTIAL)
        self.assertEqual(speed, 15)
        
        # 到工業區的邊
        speed = self.traffic_manager.get_edge_speed(TrafficConditionManager.RESIDENTIAL, TrafficConditionManager.INDUSTRIAL)
        self.assertEqual(speed, 15)
        
        # 商業區到工業區的邊
        speed = self.traffic_manager.get_edge_speed(TrafficConditionManager.COMMERCIAL, TrafficConditionManager.INDUSTRIAL)
        self.assertEqual(speed, 15)
        
        # 住宅區到住宅區的邊（都不擁堵）
        speed = self.traffic_manager.get_edge_speed(TrafficConditionManager.RESIDENTIAL, TrafficConditionManager.RESIDENTIAL)
        self.assertEqual(speed, 23)

    def test_get_edge_speed_case_insensitive(self):
        """測試邊速度計算的大小寫不敏感性"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        
        # 測試不同大小寫組合
        speed1 = self.traffic_manager.get_edge_speed("residential", "commercial")
        speed2 = self.traffic_manager.get_edge_speed("RESIDENTIAL", "COMMERCIAL")
        speed3 = self.traffic_manager.get_edge_speed("Residential", "Commercial")
        
        self.assertEqual(speed1, speed2)
        self.assertEqual(speed2, speed3)

    def test_get_edge_speed_invalid_area_types(self):
        """測試無效區域類型的邊速度"""
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        
        # 無效字符串區域類型應該返回正常速度
        invalid_string_area_types = [
            "invalid_area",
            "suburban",
            "downtown",
            ""
        ]
        
        for invalid_area in invalid_string_area_types:
            speed = self.traffic_manager.get_edge_speed(invalid_area, TrafficConditionManager.COMMERCIAL)
            self.assertEqual(speed, 23)
            
            speed = self.traffic_manager.get_edge_speed(TrafficConditionManager.COMMERCIAL, invalid_area)
            self.assertEqual(speed, 23)
        
        # 測試 None 和其他非字符串類型（應該拋出 AttributeError）
        invalid_non_string_types = [
            None,
            123,
            []
        ]
        
        for invalid_area in invalid_non_string_types:
            with self.assertRaises(AttributeError):
                self.traffic_manager.get_edge_speed(invalid_area, TrafficConditionManager.COMMERCIAL)
            
            with self.assertRaises(AttributeError):
                self.traffic_manager.get_edge_speed(TrafficConditionManager.COMMERCIAL, invalid_area)

    def test_constants_values(self):
        """測試常量的值"""
        # 測試時段常量
        self.assertEqual(TrafficConditionManager.PEAK_MORNING, "Morning rush hour")
        self.assertEqual(TrafficConditionManager.NORMAL, "Ordinary hours")
        self.assertEqual(TrafficConditionManager.PEAK_EVENING, "Evening rush hour")
        
        # 測試區域類型常量
        self.assertEqual(TrafficConditionManager.RESIDENTIAL, "residential")
        self.assertEqual(TrafficConditionManager.COMMERCIAL, "commercial")
        self.assertEqual(TrafficConditionManager.INDUSTRIAL, "industrial")
        self.assertEqual(TrafficConditionManager.MIXED, "mixed")

    def test_peak_wait_times_structure(self):
        """測試高峰期等待時間數據結構"""
        wait_times = TrafficConditionManager.PEAK_WAIT_TIMES
        
        # 驗證所有時段都存在
        self.assertIn(TrafficConditionManager.PEAK_MORNING, wait_times)
        self.assertIn(TrafficConditionManager.NORMAL, wait_times)
        self.assertIn(TrafficConditionManager.PEAK_EVENING, wait_times)
        
        # 驗證所有區域類型都存在
        area_types = [
            TrafficConditionManager.RESIDENTIAL,
            TrafficConditionManager.COMMERCIAL,
            TrafficConditionManager.INDUSTRIAL,
            TrafficConditionManager.MIXED
        ]
        
        for period in wait_times:
            for area_type in area_types:
                self.assertIn(area_type, wait_times[period])
                self.assertIsInstance(wait_times[period][area_type], int)
                self.assertGreaterEqual(wait_times[period][area_type], 0)

    def test_peak_speeds_structure(self):
        """測試高峰期速度數據結構"""
        speeds = TrafficConditionManager.PEAK_SPEEDS
        
        # 驗證所有時段都存在
        self.assertIn(TrafficConditionManager.PEAK_MORNING, speeds)
        self.assertIn(TrafficConditionManager.NORMAL, speeds)
        self.assertIn(TrafficConditionManager.PEAK_EVENING, speeds)
        
        # 驗證擁堵和正常速度都存在
        for period in speeds:
            self.assertIn("congested", speeds[period])
            self.assertIn("normal", speeds[period])
            self.assertIsInstance(speeds[period]["congested"], int)
            self.assertIsInstance(speeds[period]["normal"], int)
            self.assertGreaterEqual(speeds[period]["congested"], 0)
            self.assertGreaterEqual(speeds[period]["normal"], 0)

    def test_edge_cases_combined(self):
        """測試邊緣情況的組合"""
        # 測試時段切換後的狀態一致性
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        self.assertTrue(self.traffic_manager.get_area_congestion(TrafficConditionManager.RESIDENTIAL))
        
        self.traffic_manager.set_period(TrafficConditionManager.NORMAL)
        self.assertFalse(self.traffic_manager.get_area_congestion(TrafficConditionManager.RESIDENTIAL))
        
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_EVENING)
        self.assertFalse(self.traffic_manager.get_area_congestion(TrafficConditionManager.RESIDENTIAL))
        self.assertTrue(self.traffic_manager.get_area_congestion(TrafficConditionManager.COMMERCIAL))

    def test_performance_under_load(self):
        """測試在負載下的性能"""
        # 測試大量調用的性能
        self.traffic_manager.set_period(TrafficConditionManager.PEAK_MORNING)
        
        area_types = [
            TrafficConditionManager.RESIDENTIAL,
            TrafficConditionManager.COMMERCIAL,
            TrafficConditionManager.INDUSTRIAL,
            TrafficConditionManager.MIXED
        ]
        
        # 進行大量調用測試
        for _ in range(1000):
            for area_type in area_types:
                self.traffic_manager.get_area_congestion(area_type)
                self.traffic_manager.get_wait_time(area_type)
                self.traffic_manager.get_speed(area_type, False)
                self.traffic_manager.get_speed(area_type, True)
                
                for to_area in area_types:
                    self.traffic_manager.get_edge_speed(area_type, to_area)

if __name__ == '__main__':
    unittest.main() 