import unittest
from project.module.network import TransportNetwork
from project.module.stop import Stop, ZoneType

class TestTransportNetwork(unittest.TestCase):
    """Test cases for transport network functionality"""
    """交通网络功能的测试用例"""
    def setUp(self):
        """Set up test environment with transport network and sample stops"""
        """设置测试环境，包含交通网络和示例站点"""
        self.network = TransportNetwork()
        self.stop1 = Stop(1, "Stop 1", 0.0, 0.0, ZoneType.RESIDENTIAL)
        self.stop2 = Stop(2, "Stop 2", 1.0, 1.0, ZoneType.COMMERCIAL)
        
    def test_add_stop(self):
        """Test adding stops to the network"""
        """测试向网络添加站点"""
        self.network.add_stop(self.stop1)
        self.assertIn(self.stop1, self.network.adjacency_list)
        
        with self.assertRaises(TypeError):
            self.network.add_stop("invalid_stop")
    
    def test_add_route(self):
        """Test adding routes between stops"""
        """测试在站点之间添加路线"""
        self.network.add_stop(self.stop1)
        self.network.add_stop(self.stop2)
        self.network.add_route(self.stop1, self.stop2, 10.5)
        
        routes = self.network.adjacency_list[self.stop1]
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0], (self.stop2, 10.5))
        
        with self.assertRaises(ValueError):
            self.network.add_route(self.stop1, Stop(3, "Not added", 0, 0, ZoneType.INDUSTRIAL), 5.0)
    
    def test_load_from_csv(self):
        """Test loading network data from CSV files"""
        """测试从CSV文件加载网络数据"""
        stops_path = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_stops.csv"
        routes_path = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_routes.csv"
        
        """Test loading stops"""
        """测试加载站点"""
        network = TransportNetwork.load_stops_from_csv(stops_path)
        self.assertEqual(len(network.adjacency_list), 9)
        
        """Verify specific stations"""
        """验证具体站点"""
        chatelet = network.get_stop_by_id(1)
        self.assertEqual(chatelet.name, "Chatelet")
        self.assertEqual(chatelet.zone_type, ZoneType.RESIDENTIAL)
        
        gare_de_lyon = network.get_stop_by_id(2)
        self.assertEqual(gare_de_lyon.name, "Gare de Lyon")
        
        """Test loading routes"""
        """测试加载路线"""
        network.load_routes_from_csv(routes_path)
        total_routes = sum(len(v) for v in network.adjacency_list.values())
        self.assertEqual(total_routes, 12)
        
        """Verify specific routes"""
        """验证具体路线"""
        chatelet_routes = network.adjacency_list[chatelet]
        self.assertEqual(len(chatelet_routes), 2)
        self.assertEqual(chatelet_routes[0][1], 10.5)
        
    def test_stop_details(self):
        """Test stop details and names from CSV data"""
        """测试CSV数据中的站点详情和名称"""
        stops_path = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_stops.csv"
        network = TransportNetwork.load_stops_from_csv(stops_path)
        
        """Verify all stations"""
        """验证所有站点"""
        stops = network.adjacency_list.keys()
        stop_names = {stop.name for stop in stops}
        expected_names = {
            "Chatelet", "Gare de Lyon", "Bastille", "Nation",
            "Opera", "Republique", "Montparnasse", "La Defense", "Saint-Lazare"
        }
        self.assertSetEqual(stop_names, expected_names)
        
    def test_route_details(self):
        """Test route connection details from CSV data"""
        """测试CSV数据中的路线连接详情"""
        stops_path = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_stops.csv"
        routes_path = "D:\\360MoveData\\Users\\DELL\\Desktop\\Project\\efrei2025\\data\\urban_transport_network_routes.csv"
        
        network = TransportNetwork.load_stops_from_csv(stops_path)
        network.load_routes_from_csv(routes_path)
        chatelet = network.get_stop_by_id(1)
        gare_de_lyon = network.get_stop_by_id(2)
        bastille = network.get_stop_by_id(3)
        
        """Check Chatelet route connections"""
        """检查Chatelet的路线连接"""
        connected_stops = {route[0].name for route in network.adjacency_list[chatelet]}
        self.assertSetEqual(connected_stops, {"Gare de Lyon", "Bastille"})
        
        """Check Gare de Lyon route connections"""
        """检查Gare de Lyon的路线连接"""
        connected_stops = {route[0].name for route in network.adjacency_list[gare_de_lyon]}
        self.assertSetEqual(connected_stops, {"Bastille", "Opera"})

if __name__ == '__main__':
    unittest.main()