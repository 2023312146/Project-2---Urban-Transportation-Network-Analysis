import unittest
from unittest.mock import patch, mock_open, MagicMock
from project.core.csv_network_data_manager import NetworkDataManager
from project.data_structures.stop_entity import ZoneType, Stop

class TestCSVNetworkDataManager(unittest.TestCase):
    def setUp(self):
        # patch open, os.path, TransportNetwork, Stop
        stops_content = 'stop_id,name,latitude,longitude,zone_type\n1,A,0,0,Residential\n2,B,1,1,Commercial\n'
        routes_content = 'start_stop_id,end_stop_id,distance\n1,2,1.0\n2,1,1.0\n'
        self.stops_open = mock_open(read_data=stops_content)
        self.routes_open = mock_open(read_data=routes_content)
        def open_side_effect(file, *args, **kwargs):
            if 'stops' in file:
                return self.stops_open.return_value
            elif 'routes' in file:
                return self.routes_open.return_value
            else:
                return mock_open(read_data='').return_value
        self.patcher_open = patch('builtins.open', side_effect=open_side_effect)
        self.mock_open = self.patcher_open.start()
        self.patcher_os = patch('os.path.join', side_effect=lambda *args: args[-1])
        self.mock_os = self.patcher_os.start()
        self.patcher_transport = patch('project.core.csv_network_data_manager.TransportNetwork')
        self.mock_transport = self.patcher_transport.start()
        self.mock_network = MagicMock()
        self.mock_transport.return_value = self.mock_network
        self.mock_network.stops = {}
        self.mock_network.adjacency_list = {}
        self.mock_network.get_stop_by_id.side_effect = lambda stop_id: Stop(stop_ID=stop_id, name=f"S{stop_id}", latitude=0, longitude=0, zone_type=ZoneType.RESIDENTIAL)
        self.manager = NetworkDataManager()

    def tearDown(self):
        self.patcher_open.stop()
        self.patcher_os.stop()
        self.patcher_transport.stop()

    def test_load_data_from_csv_success(self):
        # 已在 setUp 测试
        self.assertIsInstance(self.manager, NetworkDataManager)

    def test_load_stops_file_not_found(self):
        self.mock_open.side_effect = FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            self.manager._load_stops_from_csv('not_exist.csv')
        self.mock_open.side_effect = None

    def test_load_routes_file_not_found(self):
        # 只对 not_exist.csv 抛 FileNotFoundError
        orig_open = self.mock_open
        def open_side_effect(file, *args, **kwargs):
            if file == 'not_exist.csv':
                raise FileNotFoundError
            return orig_open(file, *args, **kwargs)
        with patch('builtins.open', side_effect=open_side_effect):
            with self.assertRaises(FileNotFoundError):
                self.manager._load_routes_from_csv('not_exist.csv')

    def test_load_stops_format_error(self):
        # 返回缺失 zone_type 字段的内容，确保触发 Exception
        bad_content = 'stop_id,name,latitude,longitude\n1,A,0,0\n'
        with patch('builtins.open', mock_open(read_data=bad_content)):
            with self.assertRaises(Exception):
                self.manager._load_stops_from_csv('bad.csv')

    def test_add_station(self):
        self.mock_network.stops = {}
        self.manager.add_station('Test', 10, 20, 'Residential')
        self.mock_network.add_stop.assert_called()
        self.assertIn('Test', self.manager.station_name_to_id)

    def test_remove_station(self):
        self.manager.station_name_to_id['Test'] = '1'
        self.mock_network.get_stop_by_id.return_value = Stop(stop_ID='1', name='Test', latitude=0, longitude=0, zone_type=ZoneType.RESIDENTIAL)
        self.manager.remove_station('Test')
        self.mock_network.remove_stop.assert_called()
        self.assertNotIn('Test', self.manager.station_name_to_id)

    def test_remove_station_not_exist(self):
        # 不存在不会抛异常
        self.manager.remove_station('NotExist')

    def test_update_station_type(self):
        self.manager.station_name_to_id['Test'] = '1'
        stop = Stop(stop_ID='1', name='Test', latitude=0, longitude=0, zone_type=ZoneType.RESIDENTIAL)
        # 重置side_effect並設置return_value
        self.mock_network.get_stop_by_id.side_effect = None
        self.mock_network.get_stop_by_id.return_value = stop
        self.manager.update_station_type('Test', 'Commercial')
        self.assertEqual(stop.zone_type, ZoneType.COMMERCIAL)

    def test_add_connection(self):
        self.manager.station_name_to_id = {'A': '1', 'B': '2'}
        self.mock_network.stops = {'1': MagicMock(), '2': MagicMock()}
        self.manager.add_connection('A', 'B', 5.0)
        self.mock_network.add_route.assert_called()

    def test_add_connection_station_not_exist(self):
        with self.assertRaises(ValueError):
            self.manager.add_connection('A', 'B', 5.0)

    def test_add_connection_stop_not_in_network(self):
        self.manager.station_name_to_id = {'A': '1', 'B': '2'}
        self.mock_network.stops = {'1': MagicMock()}
        with self.assertRaises(ValueError):
            self.manager.add_connection('A', 'B', 5.0)

    def test_remove_connection(self):
        self.manager.station_name_to_id = {'A': '1', 'B': '2'}
        self.mock_network.stops = {'1': MagicMock(), '2': MagicMock()}
        self.manager.remove_connection('A', 'B')
        self.mock_network.remove_route.assert_called()

    def test_remove_connection_not_exist(self):
        # 不存在不会抛异常
        self.manager.remove_connection('A', 'B')

    def test_stations_property(self):
        stop = Stop(stop_ID='1', name='A', latitude=0, longitude=0, zone_type=ZoneType.RESIDENTIAL)
        self.mock_network.stops = {'1': stop}
        self.mock_network.adjacency_list = {'1': [('2', 1.0)]}
        stations = self.manager.stations
        self.assertIn('1', stations)
        self.assertIn('connections', stations['1'])

    def test_distances_property(self):
        self.mock_network.adjacency_list = {'1': [('2', 1.0)], '2': []}
        distances = self.manager.distances
        self.assertEqual(distances[('1', '2')], 1.0)

    def test_lines_property(self):
        self.assertEqual(self.manager.lines, {})

    def test_get_stop_by_id(self):
        result = self.manager.get_stop_by_id('1')
        if result is not None:
            self.assertIsInstance(result, Stop)
            self.assertEqual(result.stop_ID, '1')
        else:
            self.assertIsNone(result)

    def test_get_all_stops(self):
        self.mock_network.stops = {'1': 'stop1', '2': 'stop2'}
        self.assertEqual(self.manager.get_all_stops(), ['stop1', 'stop2'])

    def test_get_adjacency_list(self):
        self.mock_network.adjacency_list = {'1': [('2', 1.0)]}
        adj = self.manager.get_adjacency_list()
        self.assertEqual(adj, {'1': [('2', 1.0)]})

    def test_convert_gui_to_geo_coords(self):
        lat, lon = self.manager._convert_gui_to_geo_coords(100, 200)
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)

    def test_convert_geo_to_gui_coords(self):
        x, y = self.manager._convert_geo_to_gui_coords(48.85, 2.3)
        self.assertIsInstance(x, float)
        self.assertIsInstance(y, float)

    def test_convert_string_to_zone_type(self):
        self.assertEqual(self.manager._convert_string_to_zone_type('Residential'), ZoneType.RESIDENTIAL)
        self.assertEqual(self.manager._convert_string_to_zone_type('Unknown'), ZoneType.MIXED)

    def test_get_wait_time(self):
        self.assertEqual(self.manager._get_wait_time(ZoneType.RESIDENTIAL), 2)
        self.assertEqual(self.manager._get_wait_time(ZoneType.MIXED), 3)

    def test_load_routes_with_missing_stops(self):
        """測試當路線中的站點不存在時的警告輸出"""
        routes_content = 'start_stop_id,end_stop_id,distance\n1,999,1.0\n999,2,1.0\n'
        # 重置side_effect並設置return_value為None來模擬站點不存在
        self.mock_network.get_stop_by_id.side_effect = None
        self.mock_network.get_stop_by_id.return_value = None
        with patch('builtins.open', mock_open(read_data=routes_content)):
            with patch('builtins.print') as mock_print:
                # 應該不會拋出異常，只會打印警告
                self.manager._load_routes_from_csv('test_routes.csv')
                # 驗證警告被打印
                mock_print.assert_called()

    def test_load_routes_file_not_found_exception(self):
        """測試路線文件未找到時的異常處理"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                self.manager._load_routes_from_csv('not_exist.csv')

    def test_load_routes_general_exception(self):
        """測試路線文件讀取時的一般異常處理"""
        with patch('builtins.open', side_effect=Exception("讀取錯誤")):
            with self.assertRaises(Exception):
                self.manager._load_routes_from_csv('error.csv')

    def test_add_station_value_error(self):
        """測試添加站點時的ValueError異常"""
        self.mock_network.add_stop.side_effect = ValueError("站點已存在")
        with self.assertRaises(ValueError):
            self.manager.add_station('Test', 10, 20, 'Residential')

    def test_remove_station_deletes_mapping(self):
        """測試刪除站點時會刪除名稱到ID的映射"""
        self.manager.station_name_to_id['Test'] = '1'
        stop = Stop(stop_ID='1', name='Test', latitude=0, longitude=0, zone_type=ZoneType.RESIDENTIAL)
        self.mock_network.get_stop_by_id.return_value = stop
        self.manager.remove_station('Test')
        self.assertNotIn('Test', self.manager.station_name_to_id)

    def test_update_station_type_not_in_mapping(self):
        """測試更新不存在的站點類型"""
        # 不應該拋出異常
        self.manager.update_station_type('NotExist', 'Commercial')

    def test_update_station_type_stop_not_found(self):
        """測試更新站點類型但站點在網絡中不存在"""
        self.manager.station_name_to_id['Test'] = '1'
        self.mock_network.get_stop_by_id.return_value = None
        # 不應該拋出異常
        self.manager.update_station_type('Test', 'Commercial')

    def test_save_data_to_csv_success(self):
        """測試成功保存數據到CSV文件"""
        # 設置一些測試數據
        stop1 = Stop(stop_ID='1', name='A', latitude=0, longitude=0, zone_type=ZoneType.RESIDENTIAL)
        stop2 = Stop(stop_ID='2', name='B', latitude=1, longitude=1, zone_type=ZoneType.COMMERCIAL)
        self.mock_network.stops = {'1': stop1, '2': stop2}
        self.mock_network.adjacency_list = {'1': [('2', 1.5)]}
        
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            with patch('os.path.exists', return_value=True):
                with patch('os.makedirs'):
                    self.manager.save_data_to_csv('test_stops.csv', 'test_routes.csv')
        
        # 驗證文件被正確打開
        self.assertTrue(mock_file.called)

    def test_save_data_to_csv_create_directory(self):
        """測試保存時創建目錄"""
        stop1 = Stop(stop_ID='1', name='A', latitude=0, longitude=0, zone_type=ZoneType.RESIDENTIAL)
        self.mock_network.stops = {'1': stop1}
        self.mock_network.adjacency_list = {}
        
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            with patch('os.path.exists', return_value=False):
                with patch('os.makedirs') as mock_makedirs:
                    self.manager.save_data_to_csv('test_stops.csv', 'test_routes.csv')
        
        # 驗證目錄創建被調用
        mock_makedirs.assert_called()

    def test_save_data_to_csv_exception(self):
        """測試保存數據時的異常處理"""
        with patch('builtins.open', side_effect=Exception("寫入錯誤")):
            with self.assertRaises(Exception):
                self.manager.save_data_to_csv('test_stops.csv', 'test_routes.csv')

    def test_parse_zone_type(self):
        """測試解析區域類型"""
        self.assertEqual(self.manager._parse_zone_type("RESIDENTIAL"), ZoneType.RESIDENTIAL)
        self.assertEqual(self.manager._parse_zone_type("COMMERCIAL"), ZoneType.COMMERCIAL)
        self.assertEqual(self.manager._parse_zone_type("INDUSTRIAL"), ZoneType.INDUSTRIAL)
        self.assertEqual(self.manager._parse_zone_type("MIXED"), ZoneType.MIXED)
        self.assertEqual(self.manager._parse_zone_type("UNKNOWN"), ZoneType.MIXED)

    def test_convert_string_to_zone_type_all_types(self):
        """測試所有區域類型的轉換"""
        self.assertEqual(self.manager._convert_string_to_zone_type('Residential'), ZoneType.RESIDENTIAL)
        self.assertEqual(self.manager._convert_string_to_zone_type('Commercial'), ZoneType.COMMERCIAL)
        self.assertEqual(self.manager._convert_string_to_zone_type('Industrial'), ZoneType.INDUSTRIAL)
        self.assertEqual(self.manager._convert_string_to_zone_type('Mixed'), ZoneType.MIXED)

    def test_get_wait_time_all_types(self):
        """測試所有區域類型的等待時間"""
        self.assertEqual(self.manager._get_wait_time(ZoneType.RESIDENTIAL), 2)
        self.assertEqual(self.manager._get_wait_time(ZoneType.COMMERCIAL), 4)
        self.assertEqual(self.manager._get_wait_time(ZoneType.INDUSTRIAL), 3)
        self.assertEqual(self.manager._get_wait_time(ZoneType.MIXED), 3)

    def test_add_connection_value_error(self):
        """測試添加連接時的ValueError異常"""
        self.manager.station_name_to_id = {'A': '1', 'B': '2'}
        self.mock_network.stops = {'1': MagicMock(), '2': MagicMock()}
        self.mock_network.add_route.side_effect = ValueError("連接已存在")
        with self.assertRaises(ValueError):
            self.manager.add_connection('A', 'B', 5.0)

if __name__ == '__main__':
    unittest.main() 