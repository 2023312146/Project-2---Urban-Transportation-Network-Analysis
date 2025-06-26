from PyQt5.QtWidgets import QInputDialog, QMessageBox

class DataDialogs:
    def __init__(self, main_window):
        self.main_window = main_window
        self.data_manager = main_window.data_manager
        self.path_analyzer = main_window.path_analyzer

    def add_station_dialog(self):
        name, ok = QInputDialog.getText(self.main_window, "Add Station", "Station name:")
        if ok:
            x, ok = QInputDialog.getInt(self.main_window, "Add Station", "X coordinate:", 500, 0, 1000)
            if ok:
                y, ok = QInputDialog.getInt(self.main_window, "Add Station", "Y coordinate:", 350, 0, 700)
                if ok:
                    station_type, ok = QInputDialog.getItem(self.main_window, "Add Station", "Station type:", ["Residential", "Commercial", "Mixed", "Industrial"])
                    if ok:
                        wait_time, ok = QInputDialog.getInt(self.main_window, "Add Station", "Wait time (minutes):", 5, 0, 60)
                        if ok:
                            self.data_manager.add_station(name, x, y, station_type, wait_time)
                            self.main_window.draw_network()

    def remove_station_dialog(self):
        if not self.data_manager.stations:
            msg = QMessageBox()
            msg.setStyleSheet(self.get_messagebox_style())
            msg.warning(self.main_window, "Warning", "No stops can be removed!")
            return
        station_names = {v['name']: k for k, v in self.data_manager.stations.items()}
        station_name, ok = QInputDialog.getItem(self.main_window, "Remove station", "Select a stop:", list(station_names.keys()))
        if ok and station_name:
            self.data_manager.remove_station(station_name)
            self.main_window.clear_selection()
            self.main_window.draw_network()

    def update_station_type_dialog(self):
        if not self.data_manager.stations:
            QMessageBox.warning(self.main_window, "Warning", "No stops can be updated!")
            return
        station_names = {v['name']: k for k, v in self.data_manager.stations.items()}
        station_name, ok = QInputDialog.getItem(self.main_window, "Update station type", "Select a stop:", list(station_names.keys()))
        if ok and station_name:
            station_type, ok = QInputDialog.getItem(self.main_window, "Update station type", "Stop type:", ["Residential", "Commercial", "Mixed", "Industrial"])
            if ok:
                self.data_manager.update_station_type(station_name, station_type)
                self.main_window.draw_network()

    def add_connection_dialog(self):
        if len(self.data_manager.stations) < 2:
            QMessageBox.warning(self.main_window, "warning", "You'll need at least two stops to add a connection!")
            return
        station_names = list(self.data_manager.station_name_to_id.keys())
        from_name, ok = QInputDialog.getItem(self.main_window, "Add connection", "Start stop:", station_names)
        if not ok:
            return
        to_name, ok = QInputDialog.getItem(self.main_window, "Add connection", "Target stop:", [n for n in station_names if n != from_name])
        if not ok:
            return

        from_id = self.data_manager.station_name_to_id.get(from_name)
        to_id = self.data_manager.station_name_to_id.get(to_name)

        if from_id is None or to_id is None:
            QMessageBox.warning(self.main_window, "Error", "Selected station not found.")
            return

        if (from_id, to_id) in self.data_manager.distances:
            QMessageBox.warning(self.main_window, "Warning", "The connection already exists!")
            return
        distance, ok = QInputDialog.getDouble(self.main_window, "Add connection", "distance(km):", 10.0, 0.1, 100.0)
        if ok:
            self.data_manager.add_connection(from_name, to_name, distance)
            self.main_window.draw_network()

    def remove_connection_dialog(self):
        if len(self.data_manager.distances) == 0:
            QMessageBox.warning(self.main_window, "Warning", "No connection can be removed!")
            return
        station_names = list(self.data_manager.station_name_to_id.keys())
        from_name, ok = QInputDialog.getItem(self.main_window, "Remove connection", "Start stop:", station_names)
        if not ok:
            return
        
        from_id = self.data_manager.station_name_to_id.get(from_name)
        if not from_id:
            return

        connections = []
        for f_id, t_id in self.data_manager.distances.keys():
            if f_id == from_id:
                to_station_name = self.data_manager.stations.get(t_id, {}).get('name')
                if to_station_name:
                    connections.append(to_station_name)

        if not connections:
            QMessageBox.warning(self.main_window, "Warning", "There is no exit connection at this stop!")
            return
        to_name, ok = QInputDialog.getItem(self.main_window, "Remove connection", "target stop:", connections)
        if ok:
            self.data_manager.remove_connection(from_name, to_name)
            self.main_window.draw_network()

    def find_highest_degree_station_dialog(self):
        highest_degree_station_id = self.path_analyzer.find_highest_degree_station()
        msg = QMessageBox()
        msg.setStyleSheet(self.get_messagebox_style())
        if highest_degree_station_id:
            station = self.data_manager.stations[highest_degree_station_id]
            msg.setWindowTitle("Highest Degree Station")
            msg.setText(f"<b>{station['name']}</b><br>Connections: {len(station['connections'])}")
        else:
            msg.setWindowTitle("Highest Degree Station")
            msg.setText("No stations available")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def get_messagebox_style(self):
        return """
            QMessageBox {
                font-size: 14px;
            }
            QLabel {
                font-size: 16px;
                min-width: 300px;
            }
            QPushButton {
                min-width: 80px;
                font-size: 14px;
                padding: 5px;
            }
        """