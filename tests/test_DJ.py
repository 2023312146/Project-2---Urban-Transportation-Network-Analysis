# tests/test_DJ.py

import unittest
from project_name.DJ import TransportNetwork
import os
import tempfile

class TestTransportNetwork(unittest.TestCase):
    def setUp(self):
        self.network = TransportNetwork()
        for stop_id in [1, 2, 3]:
            self.network.add_stop(stop_id)
        self.network.add_route(1, 2, 5)
        self.network.add_route(2, 3, 10)
        self.network.add_route(1, 3, 20)

    def test_add_stop(self):
        self.network.add_stop(4)
        self.assertIn(4, self.network.stops)

    def test_add_route(self):
        self.network.add_route(3, 1, 15)
        self.assertIn((1, 15), self.network.routes[3])

    def test_dijkstra(self):
        path, distance = self.network.dijkstra(1, 3)
        self.assertEqual(path, [1, 2, 3])
        self.assertEqual(distance, 15)
        path2, distance2 = self.network.dijkstra(1, 2)
        self.assertEqual(path2, [1, 2])
        self.assertEqual(distance2, 5)

    def test_print_all_paths_with_shortest(self):
        import io
        import sys
        captured_output = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured_output
        self.network.print_all_paths_with_shortest(1, 3)
        sys.stdout = sys_stdout
        output = captured_output.getvalue()
        # 检查所有路径和最短路径标注
        self.assertIn("Path: [1, 2, 3], Distance: 15 <--- shortest", output)
        self.assertIn("Path: [1, 3], Distance: 20", output)

    def test_load_stops_from_csv(self):
        # 创建临时CSV文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("stop_id,name,latitude,longitude,zone_type\n")
            f.write("4,Stop 4,48.8566,2.3522,urban\n")
            f.write("5,Stop 5,48.8534,2.3488,suburban\n")
            temp_path = f.name
        
        try:
            self.network.load_stops_from_csv(temp_path)
            self.assertIn(4, self.network.stops)
            self.assertIn(5, self.network.stops)
            self.assertEqual(self.network.stop_details[4]['name'], "Stop 4")
            self.assertEqual(self.network.stop_details[5]['zone_type'], "suburban")
        finally:
            os.unlink(temp_path)

    def test_load_routes_from_csv(self):
        # 创建临时CSV文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("start_stop_id,end_stop_id,distance\n")
            f.write("3,4,8.5\n")
            f.write("4,5,12.3\n")
            temp_path = f.name
        
        try:
            self.network.load_routes_from_csv(temp_path)
            self.assertIn((4, 8.5), self.network.routes[3])
            self.assertIn((5, 12.3), self.network.routes[4])
        finally:
            os.unlink(temp_path)

    def test_find_all_paths(self):
        paths = self.network.find_all_paths(1, 3)
        expected_paths = [
            ([1, 2, 3], 15),
            ([1, 3], 20)
        ]
        self.assertEqual(len(paths), len(expected_paths))
        for path in expected_paths:
            self.assertIn(path, paths)

if __name__ == '__main__':
    unittest.main()
