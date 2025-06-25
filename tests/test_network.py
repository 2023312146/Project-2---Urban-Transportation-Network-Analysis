import unittest
from project.module.network import TransportNetwork
from project.module.stop import Stop, ZoneType

class TestTransportNetwork(unittest.TestCase):
    def setUp(self):
        self.network = TransportNetwork()
        self.stop1 = Stop(1, "Stop 1", 0.0, 0.0, ZoneType.RESIDENTIAL)
        self.stop2 = Stop(2, "Stop 2", 1.0, 1.0, ZoneType.COMMERCIAL)
        
    def test_add_stop(self):
        self.network.add_stop(self.stop1)
        self.assertIn(self.stop1, self.network.adjacency_list)
        
        with self.assertRaises(TypeError):
            self.network.add_stop("invalid_stop")
    
    def test_add_route(self):
        self.network.add_stop(self.stop1)
        self.network.add_stop(self.stop2)
        self.network.add_route(self.stop1, self.stop2, 10.5)
        
        routes = self.network.adjacency_list[self.stop1]
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0], (self.stop2, 10.5))
        
        with self.assertRaises(ValueError):
            self.network.add_route(self.stop1, Stop(3, "Not added", 0, 0, ZoneType.INDUSTRIAL), 5.0)
    
    def test_load_from_csv(self):
        stops_path = "d:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_stops.csv"
        routes_path = "d:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_routes.csv"
        
        # 测试加载站点
        network = TransportNetwork.load_stops_from_csv(stops_path)
        self.assertEqual(len(network.adjacency_list), 9)  # 更新为9个站点
        
        # 验证具体站点
        chatelet = network.get_stop_by_id(1)
        self.assertEqual(chatelet.name, "Chatelet")
        self.assertEqual(chatelet.zone_type, ZoneType.RESIDENTIAL)
        
        gare_de_lyon = network.get_stop_by_id(2)
        self.assertEqual(gare_de_lyon.name, "Gare de Lyon")
        
        # 测试加载路线
        network.load_routes_from_csv(routes_path)
        total_routes = sum(len(v) for v in network.adjacency_list.values())
        self.assertEqual(total_routes, 12)  # 更新为12条路线
        
        # 验证具体路线
        chatelet_routes = network.adjacency_list[chatelet]
        self.assertEqual(len(chatelet_routes), 2)  # Chatelet有2条出发路线
        self.assertEqual(chatelet_routes[0][1], 10.5)  # 第一条路线距离
        
    def test_stop_details(self):
        stops_path = "d:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_stops.csv"
        network = TransportNetwork.load_stops_from_csv(stops_path)
        
        # 验证所有站点
        stops = network.adjacency_list.keys()
        stop_names = {stop.name for stop in stops}
        expected_names = {
            "Chatelet", "Gare de Lyon", "Bastille", "Nation",
            "Opera", "Republique", "Montparnasse", "La Defense", "Saint-Lazare"
        }
        self.assertSetEqual(stop_names, expected_names)
        
    def test_route_details(self):
        stops_path = "d:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_stops.csv"
        routes_path = "d:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_routes.csv"
        
        network = TransportNetwork.load_stops_from_csv(stops_path)
        network.load_routes_from_csv(routes_path)
        
        # 验证路线连接
        chatelet = network.get_stop_by_id(1)
        gare_de_lyon = network.get_stop_by_id(2)
        bastille = network.get_stop_by_id(3)
        
        # 检查Chatelet的路线连接
        connected_stops = {route[0].name for route in network.adjacency_list[chatelet]}
        self.assertSetEqual(connected_stops, {"Gare de Lyon", "Bastille"})
        
        # 检查Gare de Lyon的路线连接
        connected_stops = {route[0].name for route in network.adjacency_list[gare_de_lyon]}
        self.assertSetEqual(connected_stops, {"Bastille", "Opera"})

if __name__ == '__main__':
    unittest.main()