import unittest
import os
import sys

# 将项目根目录添加到sys.path，以便导入模块
# D:/360MoveData/Users/DELL/Desktop/Project/efrei2025
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from show_paths import get_all_paths_and_print

class TestShowPaths(unittest.TestCase):

    def setUp(self):
        """为测试设置路径。"""
        # 修正为直接使用数据目录下的文件
        self.stops_file = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_stops.csv"
        self.routes_file = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_routes.csv"

    def test_find_all_paths(self):
        """测试查找所有路径的功能。"""
        start_stop_id = 1
        end_stop_id = 5

        all_paths = get_all_paths_and_print(self.stops_file, self.routes_file, start_stop_id, end_stop_id)

        self.assertIsNotNone(all_paths)
        self.assertEqual(len(all_paths), 3)  # 根据实际数据调整为3条路径

        path_results = []
        for path, dist in all_paths:
            path_ids = [stop.stop_ID for stop in path]
            path_results.append((path_ids, dist))

        # 更新预期结果以匹配实际数据
        expected_paths = [
            ([1, 2, 5], 20.7),
            ([1, 3, 4, 5], 29.3),
            ([1, 2, 3, 4, 5], 40.3)
        ]

        # 使用近似比较处理浮点数精度问题
        for (actual_path, actual_dist), (expected_path, expected_dist) in zip(
            sorted(path_results, key=lambda x: x[1]),
            sorted(expected_paths, key=lambda x: x[1])
        ):
            self.assertEqual(tuple(actual_path), tuple(expected_path))
            self.assertAlmostEqual(actual_dist, expected_dist, places=1)

        # 检查最短路径
        min_distance = min(dist for _, dist in all_paths)
        self.assertAlmostEqual(min_distance, 20.7, places=1)

if __name__ == '__main__':
    unittest.main()