import unittest
from project_name.network import TransportNetwork
from project_name.data_structures import Stop, ZoneType

class TestNetwork(unittest.TestCase):
    def setUp(self):
        self.network = TransportNetwork()
        self.stop1 = Stop("S1", "A", 1, 1, ZoneType.RESIDENTIAL)
        self.stop2 = Stop("S2", "B", 2, 2, ZoneType.COMMERCIAL)
        self.stop3 = Stop("S3", "C", 3, 3, ZoneType.INDUSTRIAL)
        self.network.add_stop(self.stop1)
        self.network.add_stop(self.stop2)
        self.network.add_stop(self.stop3)

    def test_add_stop(self):
        self.assertIn(self.stop3, self.network.adjacency_list)

    def test_add_route(self):
        self.network.add_route(self.stop1, self.stop2, 10)
        self.assertIn((self.stop2, 10), self.network.adjacency_list[self.stop1])

if __name__ == '__main__':
    unittest.main()