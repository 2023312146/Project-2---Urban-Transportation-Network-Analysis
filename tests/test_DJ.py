# tests/test_DJ.py

import unittest
from project_name.DJ import TransportNetwork

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

if __name__ == '__main__':
    unittest.main()
