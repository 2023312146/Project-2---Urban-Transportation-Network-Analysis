from project.module.stop import ZoneType  

class NetworkDataManager:
    def __init__(self):
        self.stations = {}
        self.station_name_to_id = {}
        self.lines = {}
        self.distances = {}
        self.create_fixed_data()
    
    def create_fixed_data(self):
        coordinates = [
            (48.8588443, 2.3470599),  # Chatelet
            (48.8433221, 2.3748736),  # Gare de Lyon
            (48.853, 2.3691),         # Bastille
            (48.8470364, 2.3955517),  # Nation
            (48.87093, 2.3325),       # Opera
            (48.867653, 2.363378),    # Republique
            (48.84216, 2.321732),     # Montparnasse
            (48.891342, 2.237151),    # La Defense
            (48.87561, 2.325482)      # Saint-Lazare
        ]
        station_names = [
            "Chatelet", "Gare de Lyon", "Bastille", "Nation", 
            "Opera", "Republique", "Montparnasse", "La Defense", "Saint-Lazare"
        ]
        station_types = [
            "Residential", "Commercial", "Industrial", "Residential",
            "Industrial", "Commercial", "Residential", "Mixed", "Commercial"
        ]
        
        min_lat = min(lat for lat, lon in coordinates)
        max_lat = max(lat for lat, lon in coordinates)
        min_lon = min(lon for lat, lon in coordinates)
        max_lon = max(lon for lat, lon in coordinates)
        view_width = 1200
        view_height = 900
        padding = 80
        
        zone_type_wait_map = {
            "Residential": 2,
            "Commercial": 4,
            "Industrial": 3,
            "Mixed": 3
        }
        
        for i, (name, (lat, lon), stype) in enumerate(zip(station_names, coordinates, station_types), start=1):
            station_id = str(i)
            norm_lat = (lat - min_lat) / (max_lat - min_lat)
            norm_lon = (lon - min_lon) / (max_lon - min_lon)
            x = padding + norm_lon * (view_width - 2*padding)
            y = padding + (1 - norm_lat) * (view_height - 2*padding)
            wait_time = zone_type_wait_map.get(stype, 3)
            self.stations[station_id] = {
                "id": station_id,
                "name": name,
                "lat": lat,
                "lon": lon,
                "x": x,
                "y": y,
                "type": stype,
                "wait_time": wait_time,
                "connections": []
            }
            self.station_name_to_id[name] = station_id
        
        connections = [
            ("Chatelet", "Gare de Lyon", 10.5),
            ("Gare de Lyon", "Bastille", 8.3),
            ("Bastille", "Nation", 12.1),
            ("Nation", "Opera", 9.4),
            ("Opera", "Republique", 7.2),
            ("Republique", "Montparnasse", 11.6),
            ("Montparnasse", "La Defense", 6.5),
            ("La Defense", "Saint-Lazare", 8.9),
            ("Saint-Lazare", "Chatelet", 15.4),
            ("Chatelet", "Bastille", 7.8),
            ("Gare de Lyon", "Opera", 10.2),
            ("Bastille", "Montparnasse", 14.3)
        ]
        
        for from_name, to_name, distance in connections:
            from_id = self.station_name_to_id[from_name]
            to_id = self.station_name_to_id[to_name]
            self.stations[from_id]["connections"].append(to_id)
            self.distances[(from_id, to_id)] = distance
            
        self.lines = {
            1: {"id": 1, "name": "线路1", "color": (0, 0, 255), "stations": [self.station_name_to_id[name] for name in ["Chatelet", "Gare de Lyon", "Bastille", "Nation"]]},
            2: {"id": 2, "name": "线路2", "color": (0, 0, 255), "stations": [self.station_name_to_id[name] for name in ["Opera", "Republique", "Montparnasse", "La Defense"]]},
            3: {"id": 3, "name": "线路3", "color": (0, 0, 255), "stations": [self.station_name_to_id[name] for name in ["Saint-Lazare", "Chatelet", "Bastille", "Montparnasse"]]}
        }

    def add_station(self, name, x, y, station_type, wait_time=None):
        if name in self.station_name_to_id:
            raise ValueError(f"Station {name} already exists")
        new_id = str(max([int(id) for id in self.stations.keys()] + [0]) + 1)
        zone_type_wait_map = {
            "Residential": 2,
            "Commercial": 4,
            "Industrial": 3,
            "Mixed": 3
        }
        if wait_time is None:
            wait_time = zone_type_wait_map.get(station_type, 3)
        self.stations[new_id] = {
            "id": new_id,
            "name": name,
            "x": x,
            "y": y,
            "type": station_type,
            "wait_time": wait_time,
            "connections": []
        }
        self.station_name_to_id[name] = new_id

    def remove_station(self, name):
        if name in self.station_name_to_id:
            station_id = self.station_name_to_id[name]
            del self.stations[station_id]
            del self.station_name_to_id[name]
            
            for station in self.stations.values():
                if station_id in station["connections"]:
                    station["connections"].remove(station_id)
            for line in self.lines.values():
                if station_id in line["stations"]:
                    line["stations"].remove(station_id)
            to_remove = [(f, t) for (f, t) in self.distances if f == station_id or t == station_id]
            for key in to_remove:
                del self.distances[key]

    def update_station_type(self, name, new_type):
        if name in self.station_name_to_id:
            station_id = self.station_name_to_id[name]
            self.stations[station_id]["type"] = new_type

    def add_connection(self, from_name, to_name, distance):
        if from_name not in self.station_name_to_id or to_name not in self.station_name_to_id:
            raise ValueError("One or both stations do not exist")
        
        from_id = self.station_name_to_id[from_name]
        to_id = self.station_name_to_id[to_name]
        
        if (from_id, to_id) in self.distances:
            raise ValueError("Connection already exists")
        self.distances[(from_id, to_id)] = distance
        self.stations[from_id]["connections"].append(to_id)

    def remove_connection(self, from_name, to_name):
        if from_name in self.station_name_to_id and to_name in self.station_name_to_id:
            from_id = self.station_name_to_id[from_name]
            to_id = self.station_name_to_id[to_name]
            if (from_id, to_id) in self.distances:
                del self.distances[(from_id, to_id)]
                if to_id in self.stations[from_id]["connections"]:
                    self.stations[from_id]["connections"].remove(to_id)