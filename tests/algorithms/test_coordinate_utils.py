import unittest
import math
from unittest.mock import MagicMock, patch
from project.algorithms.coordinate_utils import CoordinateUtils

class TestCoordinateUtils(unittest.TestCase):
    """CoordinateUtils 類的全面測試"""
    
    def setUp(self):
        """測試前的設置"""
        # 巴黎市區的測試坐標
        self.paris_lat1, self.paris_lon1 = 48.8566, 2.3522  # 巴黎市中心
        self.paris_lat2, self.paris_lon2 = 48.8584, 2.2945  # 埃菲爾鐵塔
        self.paris_lat3, self.paris_lon3 = 48.8606, 2.3376  # 盧浮宮
        
        # 極端坐標測試
        self.north_pole_lat, self.north_pole_lon = 90.0, 0.0
        self.south_pole_lat, self.south_pole_lon = -90.0, 0.0
        self.antimeridian_lat, self.antimeridian_lon = 0.0, 180.0
        
        # 相同坐標測試
        self.same_lat, self.same_lon = 48.8566, 2.3522
        
        # 測試站點數據
        self.test_stop1 = {'lat': 48.8566, 'lon': 2.3522, 'name': 'Paris Center'}
        self.test_stop2 = {'lat': 48.8584, 'lon': 2.2945, 'name': 'Eiffel Tower'}
        self.test_stop3 = {'lat': 48.8606, 'lon': 2.3376, 'name': 'Louvre'}
        
        # 模擬數據管理器
        self.mock_data_manager = MagicMock()
        self.mock_data_manager.stations = {
            '1': self.test_stop1,
            '2': self.test_stop2,
            '3': self.test_stop3
        }

    def test_calculate_haversine_distance_basic(self):
        """測試基本的 Haversine 距離計算"""
        distance = CoordinateUtils.calculate_haversine_distance(
            self.paris_lat1, self.paris_lon1,
            self.paris_lat2, self.paris_lon2
        )
        
        # 驗證距離是正數且在合理範圍內（巴黎市中心到埃菲爾鐵塔約4.5公里）
        self.assertGreater(distance, 0)
        self.assertLess(distance, 10)  # 應該小於10公里
        self.assertIsInstance(distance, float)

    def test_calculate_haversine_distance_same_point(self):
        """測試相同點的距離計算"""
        distance = CoordinateUtils.calculate_haversine_distance(
            self.same_lat, self.same_lon,
            self.same_lat, self.same_lon
        )
        
        # 相同點的距離應該接近0
        self.assertAlmostEqual(distance, 0.0, places=6)

    def test_calculate_haversine_distance_poles(self):
        """測試極點之間的距離計算"""
        distance = CoordinateUtils.calculate_haversine_distance(
            self.north_pole_lat, self.north_pole_lon,
            self.south_pole_lat, self.south_pole_lon
        )
        
        # 南北極之間的距離應該約為地球直徑的一半
        expected_distance = 20015  # 約20000公里
        self.assertGreater(distance, expected_distance * 0.9)
        self.assertLess(distance, expected_distance * 1.1)

    def test_calculate_haversine_distance_antimeridian(self):
        """測試跨越180度經線的距離計算"""
        distance = CoordinateUtils.calculate_haversine_distance(
            0.0, 179.0,  # 接近180度經線
            0.0, -179.0  # 180度經線另一側
        )
        
        # 跨越180度經線的距離應該很小（在赤道上）
        self.assertGreater(distance, 0)
        self.assertLess(distance, 500)  # 應該小於500公里

    def test_calculate_haversine_distance_edge_cases(self):
        """測試邊緣情況"""
        # 測試極限緯度
        distance = CoordinateUtils.calculate_haversine_distance(
            89.999, 0.0,  # 接近北極
            89.999, 180.0  # 接近北極，對面經度
        )
        self.assertGreater(distance, 0)
        
        # 測試極限經度
        distance = CoordinateUtils.calculate_haversine_distance(
            0.0, 179.999,  # 接近180度
            0.0, -179.999  # 接近-180度
        )
        self.assertGreater(distance, 0)

    def test_calculate_haversine_distance_invalid_inputs(self):
        """測試無效輸入（實際方法會接受任何數值並計算）"""
        # 測試超出範圍的緯度 - 實際方法會接受並計算
        distance = CoordinateUtils.calculate_haversine_distance(91.0, 0.0, 0.0, 0.0)
        self.assertIsInstance(distance, float)
        self.assertGreaterEqual(distance, 0)
        
        distance = CoordinateUtils.calculate_haversine_distance(-91.0, 0.0, 0.0, 0.0)
        self.assertIsInstance(distance, float)
        self.assertGreaterEqual(distance, 0)
        
        # 測試超出範圍的經度 - 實際方法會接受並計算
        distance = CoordinateUtils.calculate_haversine_distance(0.0, 181.0, 0.0, 0.0)
        self.assertIsInstance(distance, float)
        self.assertGreaterEqual(distance, 0)
        
        distance = CoordinateUtils.calculate_haversine_distance(0.0, -181.0, 0.0, 0.0)
        self.assertIsInstance(distance, float)
        self.assertGreaterEqual(distance, 0)

    def test_calculate_distance_between_stops_basic(self):
        """測試基本站點距離計算"""
        distance = CoordinateUtils.calculate_distance_between_stops(
            self.test_stop1, self.test_stop2
        )
        
        self.assertGreater(distance, 0)
        self.assertIsInstance(distance, float)

    def test_calculate_distance_between_stops_same_stop(self):
        """測試相同站點的距離計算"""
        distance = CoordinateUtils.calculate_distance_between_stops(
            self.test_stop1, self.test_stop1
        )
        
        self.assertAlmostEqual(distance, 0.0, places=6)

    def test_calculate_distance_between_stops_missing_coordinates(self):
        """測試缺少坐標的站點"""
        incomplete_stop1 = {'name': 'Incomplete Stop'}
        incomplete_stop2 = {'lat': 48.8566}  # 缺少 lon
        
        # 測試缺少 lat
        with self.assertRaises(KeyError):
            CoordinateUtils.calculate_distance_between_stops(
                incomplete_stop1, self.test_stop1
            )
        
        # 測試缺少 lon
        with self.assertRaises(KeyError):
            CoordinateUtils.calculate_distance_between_stops(
                incomplete_stop2, self.test_stop1
            )

    def test_calculate_distance_between_stops_by_id_basic(self):
        """測試通過ID計算站點距離的基本功能"""
        distance = CoordinateUtils.calculate_distance_between_stops_by_id(
            self.mock_data_manager, '1', '2'
        )
        
        self.assertGreater(distance, 0)
        self.assertIsInstance(distance, float)

    def test_calculate_distance_between_stops_by_id_same_stop(self):
        """測試通過ID計算相同站點的距離"""
        distance = CoordinateUtils.calculate_distance_between_stops_by_id(
            self.mock_data_manager, '1', '1'
        )
        
        self.assertAlmostEqual(distance, 0.0, places=6)

    def test_calculate_distance_between_stops_by_id_nonexistent_stops(self):
        """測試不存在的站點ID"""
        # 測試第一個站點不存在
        distance = CoordinateUtils.calculate_distance_between_stops_by_id(
            self.mock_data_manager, '999', '1'
        )
        self.assertEqual(distance, 0)
        
        # 測試第二個站點不存在
        distance = CoordinateUtils.calculate_distance_between_stops_by_id(
            self.mock_data_manager, '1', '999'
        )
        self.assertEqual(distance, 0)
        
        # 測試兩個站點都不存在
        distance = CoordinateUtils.calculate_distance_between_stops_by_id(
            self.mock_data_manager, '999', '998'
        )
        self.assertEqual(distance, 0)

    def test_calculate_distance_between_stops_by_id_empty_data_manager(self):
        """測試空數據管理器的情況"""
        empty_data_manager = MagicMock()
        empty_data_manager.stations = {}
        
        distance = CoordinateUtils.calculate_distance_between_stops_by_id(
            empty_data_manager, '1', '2'
        )
        self.assertEqual(distance, 0)

    def test_convert_gui_to_geo_coords_basic(self):
        """測試基本的GUI到地理坐標轉換"""
        # 測試中心點
        lat, lon = CoordinateUtils.convert_gui_to_geo_coords(600, 450)
        
        # 驗證結果在合理範圍內
        self.assertGreaterEqual(lat, CoordinateUtils.DEFAULT_MIN_LAT)
        self.assertLessEqual(lat, CoordinateUtils.DEFAULT_MAX_LAT)
        self.assertGreaterEqual(lon, CoordinateUtils.DEFAULT_MIN_LON)
        self.assertLessEqual(lon, CoordinateUtils.DEFAULT_MAX_LON)

    def test_convert_gui_to_geo_coords_corners(self):
        """測試角落點的轉換"""
        # 左上角
        lat, lon = CoordinateUtils.convert_gui_to_geo_coords(80, 80)
        self.assertAlmostEqual(lat, CoordinateUtils.DEFAULT_MAX_LAT, places=6)
        self.assertAlmostEqual(lon, CoordinateUtils.DEFAULT_MIN_LON, places=6)
        
        # 右下角
        lat, lon = CoordinateUtils.convert_gui_to_geo_coords(1120, 820)
        self.assertAlmostEqual(lat, CoordinateUtils.DEFAULT_MIN_LAT, places=6)
        self.assertAlmostEqual(lon, CoordinateUtils.DEFAULT_MAX_LON, places=6)

    def test_convert_gui_to_geo_coords_custom_parameters(self):
        """測試自定義參數的轉換"""
        custom_min_lat, custom_max_lat = 0.0, 1.0
        custom_min_lon, custom_max_lon = 0.0, 1.0
        custom_view_width, custom_view_height = 1000, 800
        custom_padding = 50
        
        lat, lon = CoordinateUtils.convert_gui_to_geo_coords(
            500, 400,  # 中心點
            custom_min_lat, custom_max_lat,
            custom_min_lon, custom_max_lon,
            custom_view_width, custom_view_height,
            custom_padding
        )
        
        # 驗證結果在自定義範圍內
        self.assertGreaterEqual(lat, custom_min_lat)
        self.assertLessEqual(lat, custom_max_lat)
        self.assertGreaterEqual(lon, custom_min_lon)
        self.assertLessEqual(lon, custom_max_lon)

    def test_convert_gui_to_geo_coords_edge_cases(self):
        """測試邊緣情況的轉換"""
        # 測試邊界值
        lat, lon = CoordinateUtils.convert_gui_to_geo_coords(0, 0)
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)
        
        # 測試極大值
        lat, lon = CoordinateUtils.convert_gui_to_geo_coords(9999, 9999)
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)

    def test_convert_geo_to_gui_coords_basic(self):
        """測試基本的地理到GUI坐標轉換"""
        # 測試中心點
        x, y = CoordinateUtils.convert_geo_to_gui_coords(
            (CoordinateUtils.DEFAULT_MIN_LAT + CoordinateUtils.DEFAULT_MAX_LAT) / 2,
            (CoordinateUtils.DEFAULT_MIN_LON + CoordinateUtils.DEFAULT_MAX_LON) / 2
        )
        
        # 驗證結果在合理範圍內
        self.assertGreaterEqual(x, CoordinateUtils.DEFAULT_PADDING)
        self.assertLessEqual(x, CoordinateUtils.DEFAULT_VIEW_WIDTH - CoordinateUtils.DEFAULT_PADDING)
        self.assertGreaterEqual(y, CoordinateUtils.DEFAULT_PADDING)
        self.assertLessEqual(y, CoordinateUtils.DEFAULT_VIEW_HEIGHT - CoordinateUtils.DEFAULT_PADDING)

    def test_convert_geo_to_gui_coords_corners(self):
        """測試角落點的轉換"""
        # 左上角
        x, y = CoordinateUtils.convert_geo_to_gui_coords(
            CoordinateUtils.DEFAULT_MAX_LAT,
            CoordinateUtils.DEFAULT_MIN_LON
        )
        self.assertAlmostEqual(x, CoordinateUtils.DEFAULT_PADDING, places=6)
        self.assertAlmostEqual(y, CoordinateUtils.DEFAULT_PADDING, places=6)
        
        # 右下角
        x, y = CoordinateUtils.convert_geo_to_gui_coords(
            CoordinateUtils.DEFAULT_MIN_LAT,
            CoordinateUtils.DEFAULT_MAX_LON
        )
        self.assertAlmostEqual(x, CoordinateUtils.DEFAULT_VIEW_WIDTH - CoordinateUtils.DEFAULT_PADDING, places=6)
        self.assertAlmostEqual(y, CoordinateUtils.DEFAULT_VIEW_HEIGHT - CoordinateUtils.DEFAULT_PADDING, places=6)

    def test_convert_geo_to_gui_coords_custom_parameters(self):
        """測試自定義參數的轉換"""
        custom_min_lat, custom_max_lat = 0.0, 1.0
        custom_min_lon, custom_max_lon = 0.0, 1.0
        custom_view_width, custom_view_height = 1000, 800
        custom_padding = 50
        
        x, y = CoordinateUtils.convert_geo_to_gui_coords(
            0.5, 0.5,  # 中心點
            custom_min_lat, custom_max_lat,
            custom_min_lon, custom_max_lon,
            custom_view_width, custom_view_height,
            custom_padding
        )
        
        # 驗證結果在自定義範圍內
        self.assertGreaterEqual(x, custom_padding)
        self.assertLessEqual(x, custom_view_width - custom_padding)
        self.assertGreaterEqual(y, custom_padding)
        self.assertLessEqual(y, custom_view_height - custom_padding)

    def test_coordinate_conversion_round_trip(self):
        """測試坐標轉換的往返一致性"""
        # 原始GUI坐標
        original_x, original_y = 600, 450
        
        # GUI -> 地理 -> GUI
        lat, lon = CoordinateUtils.convert_gui_to_geo_coords(original_x, original_y)
        converted_x, converted_y = CoordinateUtils.convert_geo_to_gui_coords(lat, lon)
        
        # 驗證往返轉換的一致性（允許小的浮點誤差）
        self.assertAlmostEqual(original_x, converted_x, places=6)
        self.assertAlmostEqual(original_y, converted_y, places=6)

    def test_coordinate_conversion_edge_cases(self):
        """測試坐標轉換的邊緣情況"""
        # 測試極限值
        lat, lon = CoordinateUtils.convert_gui_to_geo_coords(-1000, -1000)
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)
        
        x, y = CoordinateUtils.convert_geo_to_gui_coords(-90, -180)
        self.assertIsInstance(x, float)
        self.assertIsInstance(y, float)

    def test_default_constants(self):
        """測試默認常量的合理性"""
        # 驗證巴黎市區坐標邊界的合理性
        self.assertLess(CoordinateUtils.DEFAULT_MIN_LAT, CoordinateUtils.DEFAULT_MAX_LAT)
        self.assertLess(CoordinateUtils.DEFAULT_MIN_LON, CoordinateUtils.DEFAULT_MAX_LON)
        
        # 驗證視圖尺寸的合理性
        self.assertGreater(CoordinateUtils.DEFAULT_VIEW_WIDTH, 0)
        self.assertGreater(CoordinateUtils.DEFAULT_VIEW_HEIGHT, 0)
        self.assertGreater(CoordinateUtils.DEFAULT_PADDING, 0)
        self.assertLess(CoordinateUtils.DEFAULT_PADDING * 2, CoordinateUtils.DEFAULT_VIEW_WIDTH)
        self.assertLess(CoordinateUtils.DEFAULT_PADDING * 2, CoordinateUtils.DEFAULT_VIEW_HEIGHT)

    def test_math_accuracy(self):
        """測試數學計算的準確性"""
        # 測試已知距離的準確性
        # 巴黎市中心到埃菲爾鐵塔的實際距離約為4.5公里
        distance = CoordinateUtils.calculate_haversine_distance(
            48.8566, 2.3522,  # 巴黎市中心
            48.8584, 2.2945   # 埃菲爾鐵塔
        )
        
        # 允許10%的誤差
        expected_distance = 4.5
        self.assertGreater(distance, expected_distance * 0.9)
        self.assertLess(distance, expected_distance * 1.1)

    def test_method_types(self):
        """測試方法的類型"""
        # 驗證所有方法都是靜態方法或類方法
        # 靜態方法沒有 __self__ 屬性，類方法有
        import types
        
        # 檢查是否為靜態方法（沒有 __self__ 屬性）
        self.assertFalse(hasattr(CoordinateUtils.calculate_haversine_distance, '__self__'))
        self.assertFalse(hasattr(CoordinateUtils.calculate_distance_between_stops, '__self__'))
        self.assertFalse(hasattr(CoordinateUtils.calculate_distance_between_stops_by_id, '__self__'))
        
        # 檢查是否為類方法（有 __self__ 屬性）
        self.assertTrue(hasattr(CoordinateUtils.convert_gui_to_geo_coords, '__self__'))
        self.assertTrue(hasattr(CoordinateUtils.convert_geo_to_gui_coords, '__self__'))
        
        # 驗證方法可以被調用
        self.assertTrue(callable(CoordinateUtils.calculate_haversine_distance))
        self.assertTrue(callable(CoordinateUtils.calculate_distance_between_stops))
        self.assertTrue(callable(CoordinateUtils.calculate_distance_between_stops_by_id))
        self.assertTrue(callable(CoordinateUtils.convert_gui_to_geo_coords))
        self.assertTrue(callable(CoordinateUtils.convert_geo_to_gui_coords))

if __name__ == '__main__':
    unittest.main() 