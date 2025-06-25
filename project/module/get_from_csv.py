import csv
from project.module.network import TransportNetwork, Stop
from project.module.stop import ZoneType  # 新增导入ZoneType

def load_stops_from_csv(network, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # 将zone_type字符串转换为ZoneType枚举
            zone_type = ZoneType[row['zone_type'].upper()]  # 假设ZoneType使用大写枚举值
            stop = Stop(
                stop_ID=int(row['stop_id']),
                name=row['name'],
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                zone_type=zone_type  # 使用转换后的ZoneType实例
            )
            network.add_stop(stop)  # 传入Stop对象

def load_routes_from_csv(network, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, fieldnames=['start_stop_id', 'end_stop_id', 'distance'])
        next(reader)
        for row in reader:
            start = int(row['start_stop_id'])
            end = int(row['end_stop_id'])
            distance = float(row['distance'])
            network.add_route(start, end, distance)