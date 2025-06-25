import csv
from project.module.network import TransportNetwork, Stop
from project.module.stop import ZoneType  # 新增导入ZoneType

def load_stops_from_csv(network, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            stop = Stop(
                stop_ID=int(row['stop_id']),
                name=row['name'],
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                zone_type=ZoneType[row['zone_type'].upper()]
            )
            network.add_stop(stop)  # 传入Stop对象

def load_routes_from_csv(network, file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                start_id = int(row['start_stop_id'])
                end_id = int(row['end_stop_id'])
                distance = float(row['distance'])
                
                # 获取Stop对象
                start_stop = network.stops.get(start_id)
                end_stop = network.stops.get(end_id)
                
                if start_stop and end_stop:
                    network.add_route(start_stop, end_stop, distance)
                else:
                    print(f"警告：找不到站点ID {start_id} 或 {end_id}，跳过此路线")
            except (ValueError, KeyError) as e:
                print(f"跳过格式错误的路线行：{row}，错误：{e}")