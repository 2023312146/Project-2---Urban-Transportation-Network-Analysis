import unittest
import os
from project_name.network import TransportNetwork
from project_name.io import load_stops_from_csv, load_routes_from_csv

class TestIO(unittest.TestCase):

    def setUp(self):
        self.network = TransportNetwork()
        # Create dummy csv files for testing
        self.stops_file = 'test_stops.csv'
        with open(self.stops_file, 'w', newline='') as f:
            f.write("stop_id,name,latitude,longitude,zone_type\n")
            f.write("1,A,0,0,urban\n")
            f.write("2,B,1,1,suburban\n")

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
        self.assertEqual(self.network.stop_details[1]['name'], 'A')

    def test_load_routes(self):
        # Stops need to be loaded first for routes to be added correctly
        load_stops_from_csv(self.network, self.stops_file)
        load_routes_from_csv(self.network, self.routes_file)
        self.assertIn((2, 10), self.network.routes[1])

if __name__ == '__main__':
    unittest.main() 