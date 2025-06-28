import unittest
import os
from project.module.network import TransportNetwork
from project.module.stop import Stop, ZoneType  

class TestIO(unittest.TestCase):
    """Test cases for CSV file input/output operations"""
    """CSV文件输入输出操作的测试用例"""
    def setUp(self):

        self.network = TransportNetwork()
        self.stops_file = 'test_stops.csv'
        with open(self.stops_file, 'w', newline='') as f:
            f.write("stop_id,name,latitude,longitude,zone_type\n")
            f.write("1,A,0,0,URBAN\n")
            f.write("2,B,1,1,RESIDENTIAL\n")

        self.routes_file = 'test_routes.csv'
        with open(self.routes_file, 'w', newline='') as f:
            f.write("start_stop_id,end_stop_id,distance\n")
            f.write("1,2,10\n")

    def tearDown(self):
        os.remove(self.stops_file)
        os.remove(self.routes_file)

    def test_load_stops(self):

        network = TransportNetwork.load_stops_from_csv(self.stops_file)
        self.assertEqual(len(network.stops), 2)
        self.assertIn(1, network.stops)
        self.assertIn(2, network.stops)
        self.assertEqual(network.stops[1].name, 'A')

    def test_load_routes(self):
 
        network = TransportNetwork.load_stops_from_csv(self.stops_file)
        network.load_routes_from_csv(self.routes_file)
        stop1 = network.stops[1]
        stop2 = network.stops[2]
        self.assertIn((stop2, 10.0), network.adjacency_list[stop1])

if __name__ == '__main__':
    unittest.main()