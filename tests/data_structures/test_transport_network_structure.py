import unittest
from project.data_structures.transport_network_structure import TransportNetwork
from project.data_structures.stop_entity import Stop, ZoneType
from unittest.mock import patch, mock_open

class TestTransportNetworkStructure(unittest.TestCase):
    def setUp(self):
        self.network = TransportNetwork()
        self.stopA = Stop(1, 'A', 0, 0, ZoneType.RESIDENTIAL)
        self.stopB = Stop(2, 'B', 1, 1, ZoneType.COMMERCIAL)
        self.stopC = Stop(3, 'C', 2, 2, ZoneType.INDUSTRIAL)

    def test_add_stop_and_duplicate(self):
        self.network.add_stop(self.stopA)
        self.assertIn(1, self.network.stops)
        with self.assertRaises(ValueError):
            self.network.add_stop(self.stopA)
        with self.assertRaises(TypeError):
            self.network.add_stop('not_a_stop')

    def test_add_route_and_duplicate_and_errors(self):
        self.network.add_stop(self.stopA)
        self.network.add_stop(self.stopB)
        self.network.add_route(self.stopA, self.stopB, 5.0)
        self.assertIn((2, 5.0), self.network.adjacency_list[1])
        self.assertIn((1, 5.0), self.network.reverse_adjacency[2])
        with self.assertRaises(ValueError):
            self.network.add_route(self.stopA, self.stopB, 5.0)
        with self.assertRaises(ValueError):
            self.network.add_route(self.stopA, self.stopB, -1)
        with self.assertRaises(ValueError):
            self.network.add_route(self.stopA, self.stopC, 1)

    def test_remove_stop_and_nonexistent(self):
        self.network.add_stop(self.stopA)
        self.network.add_stop(self.stopB)
        self.network.add_route(self.stopA, self.stopB, 1)
        self.network.remove_stop(self.stopA)
        self.assertNotIn(1, self.network.stops)
        self.network.remove_stop(self.stopA)  # 不存在不会报错

    def test_remove_route_and_nonexistent(self):
        self.network.add_stop(self.stopA)
        self.network.add_stop(self.stopB)
        self.network.add_route(self.stopA, self.stopB, 1)
        self.network.remove_route(self.stopA, self.stopB)
        self.assertEqual(self.network.adjacency_list[1], [])
        self.network.remove_route(self.stopA, self.stopB)  # 不存在不会报错

    def test_get_stop_by_id(self):
        self.network.add_stop(self.stopA)
        self.assertEqual(self.network.get_stop_by_id(1), self.stopA)
        self.assertIsNone(self.network.get_stop_by_id(999))

    def test_load_stops_from_csv(self):
        csv_content = 'stop_id,name,latitude,longitude,zone_type\n1,A,0,0,Residential\n2,B,1,1,Commercial\n'
        with patch('builtins.open', mock_open(read_data=csv_content)):
            net = TransportNetwork.load_stops_from_csv('dummy.csv')
            self.assertIn(1, net.stops)
            self.assertIn(2, net.stops)

    def test_load_routes_from_csv(self):
        self.network.add_stop(self.stopA)
        self.network.add_stop(self.stopB)
        csv_content = 'start_stop_id,end_stop_id,distance\n1,2,1.0\n2,1,1.0\n'
        with patch('builtins.open', mock_open(read_data=csv_content)):
            self.network.load_routes_from_csv('dummy.csv')
            self.assertIn((2, 1.0), self.network.adjacency_list[1])
            self.assertIn((1, 1.0), self.network.adjacency_list[2])

    def test_load_routes_from_csv_with_errors(self):
        self.network.add_stop(self.stopA)
        csv_content = 'start_stop_id,end_stop_id,distance\n1,999,1.0\n1,2,abc\n'
        with patch('builtins.open', mock_open(read_data=csv_content)):
            self.network.load_routes_from_csv('dummy.csv')  # 不会抛异常，只会打印警告

if __name__ == '__main__':
    unittest.main() 