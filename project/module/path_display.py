from PyQt5.QtCore import Qt

class PathDisplay:
    def __init__(self, main_window):
        self.main_window = main_window
        self.data_manager = main_window.data_manager
        self.path_analyzer = main_window.path_analyzer

    def update_path_info(self):
        if not self.main_window.selected_start or not self.main_window.selected_end:
            return
        self.main_window.all_paths = self.path_analyzer.find_all_paths(str(self.main_window.selected_start), str(self.main_window.selected_end))
        self.main_window.best_path = self.path_analyzer.find_best_path(str(self.main_window.selected_start), str(self.main_window.selected_end))
        self.main_window.show_only_best_path = True
        start_name = self.data_manager.stations.get(str(self.main_window.selected_start), {}).get("name", str(self.main_window.selected_start))
        end_name = self.data_manager.stations.get(str(self.main_window.selected_end), {}).get("name", str(self.main_window.selected_end))
        info_text = f"FROM {start_name} TO {end_name}<br>-----------<br>"
        if not self.main_window.all_paths:
            info_text += "No path found."
        else:
            info_text += "All reachable paths:"
        for idx, path in enumerate(self.main_window.all_paths):
            path = [str(station) for station in path]
            path_names = []
            for station_id in path:
                station = self.data_manager.stations.get(str(station_id), {})
                path_names.append(station.get("name", str(station_id)))
            total_dist = 0.0
            for j in range(len(path)-1):
                dist = self.data_manager.distances.get((str(path[j]), str(path[j+1])), 0)
                total_dist += dist
            path_str = " → ".join(path_names)
            info_text += f"{path_str} (distance: {total_dist:.2f}km)<br>-----------<br>"
        if self.main_window.best_path:
            info_text += "<br>"
            best_path = [str(station) for station in self.main_window.best_path]
            best_path_names = []
            for station_id in best_path:
                station = self.data_manager.stations.get(str(station_id), {})
                best_path_names.append(station.get("name", str(station_id)))
            best_dist = 0.0
            for j in range(len(best_path)-1):
                dist = self.data_manager.distances.get((str(best_path[j]), str(best_path[j+1])), 0)
                best_dist += dist
            best_path_str = " → ".join(best_path_names)
            info_text += f"<b>Recommended Path (Minimum Distance):</b><br>{best_path_str} (distance: {best_dist:.2f}km)"
        self.main_window.path_info.setText(info_text)
        self.main_window.path_info.setTextFormat(Qt.RichText)