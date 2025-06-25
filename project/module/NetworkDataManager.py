class NetworkDataManager:
    def __init__(self):
        self.stations = {}
        self.lines = {}
        self.distances = {}
        self.create_fixed_data()
    
    def create_fixed_data(self):
        coordinates = [
            (48.8588443, 2.3470599),  # 1 Chatelet
            (48.8433221, 2.3748736),  # 2 Gare de Lyon
            (48.853, 2.3691),         # 3 Bastille
            (48.8470364, 2.3955517),  # 4 Nation
            (48.87093, 2.3325),       # 5 Opera
            (48.867653, 2.363378),    # 6 Republique
            (48.84216, 2.321732),     # 7 Montparnasse
            (48.891342, 2.237151),    # 8 La Defense
            (48.87561, 2.325482)      # 9 Saint-Lazare
        ]
        station_info = {
            1: {"name": "Chatelet", "type": "Residential"},
            2: {"name": "Gare de Lyon", "type": "Commercial"},
            3: {"name": "Bastille", "type": "Industrial"},
            4: {"name": "Nation", "type": "Residential"},
            5: {"name": "Opera", "type": "Industrial"},
            6: {"name": "Republique", "type": "Commercial"},
            7: {"name": "Montparnasse", "type": "Residential"},
            8: {"name": "La Defense", "type": "Mixed"},
            9: {"name": "Saint-Lazare", "type": "Commercial"}
        }
        min_lat = min(lat for lat, lon in coordinates)
        max_lat = max(lat for lat, lon in coordinates)
        min_lon = min(lon for lat, lon in coordinates)
        max_lon = max(lon for lat, lon in coordinates)
        view_width = 1200
        view_height = 900
        padding = 80
        for i, (lat, lon) in enumerate(coordinates, start=1):
            norm_lat = (lat - min_lat) / (max_lat - min_lat)
            norm_lon = (lon - min_lon) / (max_lon - min_lon)
            x = padding + norm_lon * (view_width - 2*padding)
            y = padding + (1 - norm_lat) * (view_height - 2*padding)
            info = station_info[i]
            self.stations[i] = {
                "id": i,
                "name": info["name"],
                "lat": lat,
                "lon": lon,
                "x": x,
                "y": y,
                "type": info["type"],
                "wait_time": 5,
                "connections": []
            }
        connections = [
            (1, 2, 10.5), (2, 3, 8.3), (3, 4, 12.1), (4, 5, 9.4),
            (5, 6, 7.2), (6, 7, 11.6), (7, 8, 6.5), (8, 9, 8.9),
            (9, 1, 15.4), (1, 3, 7.8), (2, 5, 10.2), (3, 7, 14.3)
        ]
        for from_id, to_id, distance in connections:
            self.stations[from_id]["connections"].append(to_id)
            self.distances[(from_id, to_id)] = distance
        self.lines = {
            1: {"id": 1, "name": "线路1", "color": (0, 0, 255), "stations": [1, 2, 3, 4]},
            2: {"id": 2, "name": "线路2", "color": (0, 0, 255), "stations": [5, 6, 7, 8]},
            3: {"id": 3, "name": "线路3", "color": (0, 0, 255), "stations": [9, 1, 3, 7]}
        }

    def add_station(self, name, x, y, station_type="Residential", wait_time=5):
        new_id = max(self.stations.keys()) + 1 if self.stations else 1
        self.stations[new_id] = {
            "id": new_id,
            "name": name,
            "x": x,
            "y": y,
            "type": station_type,
            "wait_time": wait_time,
            "connections": []
        }

    def remove_station(self, station_id):
        if station_id in self.stations:
            del self.stations[station_id]
            for station in self.stations.values():
                if station_id in station["connections"]:
                    station["connections"].remove(station_id)
            for line in self.lines.values():
                if station_id in line["stations"]:
                    line["stations"].remove(station_id)
            to_remove = [(f, t) for (f, t) in self.distances if f == station_id or t == station_id]
            for key in to_remove:
                del self.distances[key]

    def update_station_type(self, station_id, new_type):
        if station_id in self.stations:
            self.stations[station_id]["type"] = new_type

    def add_connection(self, from_id, to_id, distance):
        self.stations[from_id]["connections"].append(to_id)
        self.distances[(from_id, to_id)] = distance

    def remove_connection(self, from_id, to_id):
        if from_id in self.stations and to_id in self.stations:
            if to_id in self.stations[from_id]["connections"]:
                self.stations[from_id]["connections"].remove(to_id)
            if (from_id, to_id) in self.distances:
                del self.distances[(from_id, to_id)]
    # 其余add/remove/update station/connection等方法后续补充 