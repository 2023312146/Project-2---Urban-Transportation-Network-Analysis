from project.algorithms.algorithms import dijkstra, find_all_paths as find_all_paths_algo
from project.module.network import TransportNetwork
from project.module.stop import Stop, ZoneType

class PathAnalyzer:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def _create_transport_network(self):
        network = TransportNetwork()
        zone_type_map = {
            "Residential": ZoneType.RESIDENTIAL,
            "Commercial": ZoneType.COMMERCIAL,
            "Industrial": ZoneType.INDUSTRIAL,
            "Mixed": ZoneType.MIXED,
        }
        stops = {}
        for station_id, station_data in self.data_manager.stations.items():
            zone_type_str = station_data['type']
            zone_type = zone_type_map.get(zone_type_str, ZoneType.MIXED)
            stop = Stop(
                stop_ID=station_data['id'],
                name=station_data['name'],
                latitude=station_data.get('lat', 0),
                longitude=station_data.get('lon', 0),
                zone_type=zone_type
            )
            stops[station_id] = stop
        for stop in stops.values():
            network.add_stop(stop)
        for (from_id, to_id), distance in self.data_manager.distances.items():
            from_stop = stops.get(from_id)
            to_stop = stops.get(to_id)
            if from_stop and to_stop:
                network.add_route(from_stop, to_stop, distance)
        return network, stops

    def find_all_paths(self, start, end):
        network, stops_map = self._create_transport_network()
        start_stop = stops_map.get(start)
        end_stop = stops_map.get(end)
        if not start_stop or not end_stop:
            return []
        all_paths_result = find_all_paths_algo(network, start_stop, end_stop)
        return [[stop.stop_ID for stop in path] for path, _ in all_paths_result]

    def find_best_path(self, start, end):
        network, stops_map = self._create_transport_network()
        start_stop = stops_map.get(start)
        end_stop = stops_map.get(end)
        if not start_stop or not end_stop:
            return []
        best_path_stops, _ = dijkstra(network, start_stop, end_stop)
        if best_path_stops:
            return [s.stop_ID for s in best_path_stops]
        else:
            return []

    def find_highest_degree_station(self):
        max_degree = 0
        highest_degree_station = None
        for station_id, station in self.data_manager.stations.items():
            degree = len(station["connections"])
            if degree > max_degree:
                max_degree = degree
                highest_degree_station = station_id
        return highest_degree_station