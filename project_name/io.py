import csv
from .network import TransportNetwork

def load_stops_from_csv(network, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            stop_id = int(row['stop_id'])
            details = {
                'name': row['name'],
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'zone_type': row['zone_type']
            }
            network.add_stop(stop_id, details)

def load_routes_from_csv(network, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, fieldnames=['start_stop_id', 'end_stop_id', 'distance'])
        next(reader)
        for row in reader:
            start = int(row['start_stop_id'])
            end = int(row['end_stop_id'])
            distance = float(row['distance'])
            network.add_route(start, end, distance) 