class NetworkDataManager:
    def __init__(self):
        self.stations = {}
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
        
        for i, (name, (lat, lon), stype) in enumerate(zip(station_names, coordinates, station_types), start=1):
            norm_lat = (lat - min_lat) / (max_lat - min_lat)
            norm_lon = (lon - min_lon) / (max_lon - min_lon)
            x = padding + norm_lon * (view_width - 2*padding)
            y = padding + (1 - norm_lat) * (view_height - 2*padding)
            
            self.stations[name] = {
                "id": i,
                "name": name,
                "lat": lat,
                "lon": lon,
                "x": x,
                "y": y,
                "type": stype,
                "wait_time": 5,
                "connections": []
            }
        
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
            self.stations[from_name]["connections"].append(to_name)
            self.distances[(from_name, to_name)] = distance
            
        self.lines = {
            1: {"id": 1, "name": "线路1", "color": (0, 0, 255), "stations": ["Chatelet", "Gare de Lyon", "Bastille", "Nation"]},
            2: {"id": 2, "name": "线路2", "color": (0, 0, 255), "stations": ["Opera", "Republique", "Montparnasse", "La Defense"]},
            3: {"id": 3, "name": "线路3", "color": (0, 0, 255), "stations": ["Saint-Lazare", "Chatelet", "Bastille", "Montparnasse"]}
        }

    def add_station(self, name, x, y, station_type, wait_time=5):
        if name in self.stations:
            raise ValueError(f"Station {name} already exists")
        self.stations[name] = {
            "name": name,
            "x": x,
            "y": y,
            "type": station_type,
            "wait_time": wait_time,
            "connections": []
        }

    def remove_station(self, name):
        if name in self.stations:
            del self.stations[name]
            for station in self.stations.values():
                if name in station["connections"]:
                    station["connections"].remove(name)
            for line in self.lines.values():
                if name in line["stations"]:
                    line["stations"].remove(name)
            to_remove = [(f, t) for (f, t) in self.distances if f == name or t == name]
            for key in to_remove:
                del self.distances[key]

    def update_station_type(self, name, new_type):
        if name in self.stations:
            self.stations[name]["type"] = new_type

    def add_connection(self, from_name, to_name, distance):
        if from_name not in self.stations or to_name not in self.stations:
            raise ValueError("One or both stations do not exist")
        if (from_name, to_name) in self.distances:
            raise ValueError("Connection already exists")
        self.distances[(from_name, to_name)] = distance
        self.stations[from_name]["connections"].append(to_name)

    def remove_connection(self, from_name, to_name):
        if (from_name, to_name) in self.distances:
            del self.distances[(from_name, to_name)]
            if to_name in self.stations[from_name]["connections"]:
                self.stations[from_name]["connections"].remove(to_name)