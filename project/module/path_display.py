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
        if self.main_window.best_path:
            info_text += "<br>"
            best_path = [str(station) for station in self.main_window.best_path]
            best_path_names = []
            for station_id in best_path:
                station = self.data_manager.stations.get(str(station_id), {})
                best_path_names.append(station.get("name", str(station_id)))
            # 获取最短路径效率
            compare_result = self.path_analyzer.compare_best_paths(
                str(self.main_window.selected_start),
                str(self.main_window.selected_end)
            )
            best_dist = 0.0
            best_eff = 0.0
            if compare_result:
                best_dist = compare_result['dijkstra_distance']
                # 重新计算最短路径的效率
                best_eff = 0.0
                if compare_result['dijkstra_path']:
                    # 复用RouteAnalyzer的效率计算逻辑
                    best_eff = self.path_analyzer._calculate_efficiency(
                        [self.path_analyzer._create_transport_network()[1][sid] for sid in compare_result['dijkstra_path']],
                        best_dist
                    )
            best_path_str = " → ".join(best_path_names)
            info_text += f"<b>Recommended Path (Minimum Distance):</b><br>{best_path_str} (distance: {best_dist:.2f}km, efficiency: {best_eff:.2f}km/h)"

            # 展示效率最高路径
            if compare_result:
                eff_path_ids = compare_result['efficiency_path']
                eff_path_names = []
                for station_id in eff_path_ids:
                    station = self.data_manager.stations.get(str(station_id), {})
                    eff_path_names.append(station.get("name", str(station_id)))
                eff_dist = compare_result['efficiency_distance']
                eff_value = compare_result['efficiency_value']
                eff_path_str = " → ".join(eff_path_names)
                info_text += f"<br><b>Recommended Path (Maximum Efficiency):</b><br>{eff_path_str} (distance: {eff_dist:.2f}km, efficiency: {eff_value:.2f}km/h)"
        self.main_window.path_info.setText(info_text)
        self.main_window.path_info.setTextFormat(Qt.RichText)