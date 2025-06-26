from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QGraphicsEllipseItem

class InteractionHandler:
    def __init__(self, main_window):
        self.main_window = main_window  # 主窗口引用
        self.data_manager = main_window.data_manager  # 数据管理器

    def handle_station_hover(self, pos: QPointF):
        items = self.main_window.scene.items(pos)
        for item in items:
            if isinstance(item, QGraphicsEllipseItem):
                station_id = item.data(0)
                if station_id and station_id != self.main_window.hovered_station:
                    self.main_window.hovered_station = station_id
                    station = self.data_manager.stations[station_id]
                    conn_info = []
                    for conn_id in station["connections"]:
                        conn_station = self.data_manager.stations[conn_id]
                        distance = self.data_manager.distances.get((station_id, conn_id), 0)
                        conn_info.append(f"{conn_station['name']}: {distance:.2f}km")
                    info = (f"Station: {station['name']}\n"
                            f"Type: {station['type']}\n"
                            f"Wait time: {station['wait_time']} minutes\n"
                            f"Connections:\n  " + "\n  ".join(conn_info))
                    self.main_window.info_label.setText(info)
                    break
        else:
            if self.main_window.hovered_station:
                self.main_window.hovered_station = None

    def handle_station_click(self, pos: QPointF):
        items = self.main_window.scene.items(pos)
        for item in items:
            if isinstance(item, QGraphicsEllipseItem):
                station_id = item.data(0)
                if station_id:
                    station_name = self.data_manager.stations[station_id]['name']
                    if self.main_window.selected_start is None:
                        self.main_window.selected_start = station_id
                        self.main_window.info_label.setText(f"Start point selected: {station_name}\nPlease click to select end point")
                    elif self.main_window.selected_end is None and station_id != self.main_window.selected_start:
                        self.main_window.selected_end = station_id
                        self.main_window.update_path_info()
                    else:
                        self.main_window.selected_start = station_id
                        self.main_window.selected_end = None
                        self.main_window.info_label.setText(f"Start point selected: {station_name}\nPlease click to select end point")
                        self.main_window.path_info.setText("")
                    self.main_window.draw_network()
                    break