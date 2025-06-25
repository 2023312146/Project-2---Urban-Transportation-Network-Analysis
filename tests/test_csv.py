import unittest
import os
from project.module.network import TransportNetwork
from project.module.stop import Stop, ZoneType  
from project.module.get_from_csv import load_stops_from_csv, load_routes_from_csv    

class TestIO(unittest.TestCase):

    def setUp(self):
        self.network = TransportNetwork()
        # Create dummy csv files for testing
        self.stops_file = 'test_stops.csv'
        with open(self.stops_file, 'w', newline='') as f:
            f.write("stop_id,name,latitude,longitude,zone_type\n")
            f.write("1,A,0,0,URBAN\n")  # 改为大写URBAN
            f.write("2,B,1,1,RESIDENTIAL\n")  # 改为RESIDENTIAL

        self.routes_file = 'test_routes.csv'
        with open(self.routes_file, 'w', newline='') as f:
            f.write("start_stop_id,end_stop_id,distance\n")
            f.write("1,2,10\n")

    def tearDown(self):
        os.remove(self.stops_file)
        os.remove(self.routes_file)

    def test_load_stops(self):
        load_stops_from_csv(self.network, self.stops_file)
        self.assertEqual(len(self.network.stops), 2)
        self.assertIn(1, self.network.stops)
        self.assertIn(2, self.network.stops)
        # 修改为直接访问Stop对象的属性
        self.assertEqual(self.network.stops[1].name, 'A')

    def test_load_routes(self):
        # Stops need to be loaded first for routes to be added correctly
        load_stops_from_csv(self.network, self.stops_file)
        load_routes_from_csv(self.network, self.routes_file)
        # 修改为检查邻接表中的连接
        stop1 = self.network.stops[1]
        stop2 = self.network.stops[2]
        self.assertIn((stop2, 10.0), self.network.adjacency_list[stop1])

if __name__ == '__main__':
    unittest.main()