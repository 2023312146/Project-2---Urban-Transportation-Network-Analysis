from PyQt5.QtCore import Qt

class PathDisplay:
    def __init__(self, main_window):
        self.main_window = main_window
        self.data_manager = main_window.data_manager
        self.path_analyzer = main_window.path_analyzer

    def update_path_info(self):
        if not self.main_window.selected_start or not self.main_window.selected_end:
            return
        self.main_window.all_paths = self.path_analyzer.find_all_paths(
            str(self.main_window.selected_start),
            str(self.main_window.selected_end),
            include_efficiency=True
        )
        self.main_window.best_path = self.path_analyzer.find_best_path(str(self.main_window.selected_start), str(self.main_window.selected_end))
        
        # 获取路径比较结果，包含最短路径和最高效路径
        compare_result = self.path_analyzer.compare_best_paths(
            str(self.main_window.selected_start),
            str(self.main_window.selected_end)
        )
        
        # 存储路径信息到主窗口
        if compare_result:
            self.main_window.shortest_path = compare_result['dijkstra_path']  # 最短路径
            self.main_window.efficiency_path = compare_result['efficiency_path']  # 最高效路径
            self.main_window.shortest_distance = compare_result['dijkstra_distance']
            self.main_window.efficiency_distance = compare_result['efficiency_distance']
            self.main_window.efficiency_value = compare_result['efficiency_value']
            self.main_window.paths_are_same = compare_result['is_same']
        else:
            self.main_window.shortest_path = []
            self.main_window.efficiency_path = []
            self.main_window.shortest_distance = 0.0
            self.main_window.efficiency_distance = 0.0
            self.main_window.efficiency_value = 0.0
            self.main_window.paths_are_same = False
        
        self.main_window.show_only_best_path = True
        start_name = self.data_manager.stations.get(str(self.main_window.selected_start), {}).get("name", str(self.main_window.selected_start))
        end_name = self.data_manager.stations.get(str(self.main_window.selected_end), {}).get("name", str(self.main_window.selected_end))
        info_text = f"FROM {start_name} TO {end_name}<br>-----------<br>"
        if not self.main_window.all_paths:
            info_text += "No path found."
        else:
            info_text += "All reachable paths:"
        for idx, path_info in enumerate(self.main_window.all_paths):
            path = [str(station) for station in path_info['path']]
            path_names = []
            for station_id in path:
                station = self.data_manager.stations.get(str(station_id), {})
                path_names.append(station.get("name", str(station_id)))
            total_dist = path_info.get('distance', 0.0)
            efficiency = path_info.get('efficiency', 0.0)
            path_str = " → ".join(path_names)
            info_text += f"{path_str} (distance: {total_dist:.2f}km, efficiency: {efficiency:.2f}km/h)<br>-----------<br>"
        
        # 显示最短路径信息
        if self.main_window.shortest_path:
            info_text += "<br>"
            shortest_path_names = []
            for station_id in self.main_window.shortest_path:
                station = self.data_manager.stations.get(str(station_id), {})
                shortest_path_names.append(station.get("name", str(station_id)))
            shortest_path_str = " → ".join(shortest_path_names)
            info_text += f"<b>Shortest Path (Red):</b><br>{shortest_path_str} (distance: {self.main_window.shortest_distance:.2f}km)<br>"

        # 显示最高效路径信息
        if self.main_window.efficiency_path:
            efficiency_path_names = []
            for station_id in self.main_window.efficiency_path:
                station = self.data_manager.stations.get(str(station_id), {})
                efficiency_path_names.append(station.get("name", str(station_id)))
            efficiency_path_str = " → ".join(efficiency_path_names)
            info_text += f"<b>Most Efficient Path (Green):</b><br>{efficiency_path_str} (distance: {self.main_window.efficiency_distance:.2f}km, efficiency: {self.main_window.efficiency_value:.2f}km/h)<br>"
        
        self.main_window.path_info.setText(info_text)
        self.main_window.path_info.setTextFormat(Qt.RichText)