from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QTableWidget, QTableWidgetItem, QPushButton, 
                           QLabel, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal

class StopUtilizationDisplay(QDialog):
    """
    显示站点利用率分析结果的对话框
    """
    # 定义信号
    remove_stop_signal = pyqtSignal(str)  # 移除站点信号，参数为站点ID
    add_stop_signal = pyqtSignal(float, float, str, list)  # 添加站点信号，参数为(纬度,经度,名称,连接站点名称列表)
    
    def __init__(self, utilization_analyzer, parent=None):
        """
        初始化站点利用率分析结果显示对话框
        
        Args:
            utilization_analyzer: 站点利用率分析器实例
            parent: 父窗口
        """
        super().__init__(parent)
        self.analyzer = utilization_analyzer
        self.results = utilization_analyzer.optimize_network()
        
        self.setWindowTitle("站点利用率分析")
        self.resize(800, 600)
        
        self._init_ui()
    
    def _init_ui(self):
        """
        初始化用户界面
        """
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        tabs = QTabWidget()
        
        # 低利用率站点标签页
        underutilized_tab = self._create_underutilized_tab()
        tabs.addTab(underutilized_tab, "Low utilization stops")
        
        # 可合并站点标签页
        consolidation_tab = self._create_consolidation_tab()
        tabs.addTab(consolidation_tab, "Stops can be merged")
        
        # 新站点建议标签页
        new_stops_tab = self._create_new_stops_tab()
        tabs.addTab(new_stops_tab, "New stop recommendations")
        
        main_layout.addWidget(tabs)
    
    def _create_underutilized_tab(self):
        """
        创建低利用率站点标签页
        """
        tab = QTableWidget()
        tab.setRowCount(len(self.results['underutilized_stops']))
        tab.setColumnCount(6)
        
        # 设置表头
        tab.setHorizontalHeaderLabels([
            "Stop_ID", "Name", "Efficiency score", "Connectivity", "Passenger volume", "Operation"
        ])
        
        # 填充数据
        for row, stop in enumerate(self.results['underutilized_stops']):
            tab.setItem(row, 0, QTableWidgetItem(str(stop['stop_id'])))
            tab.setItem(row, 1, QTableWidgetItem(stop['name']))
            tab.setItem(row, 2, QTableWidgetItem(f"{stop['score']:.2f}"))
            tab.setItem(row, 3, QTableWidgetItem(str(stop['connectivity'])))
            tab.setItem(row, 4, QTableWidgetItem(str(stop['passenger_volume'])))
            
            # 添加删除按钮
            remove_btn = QPushButton("Delete")
            remove_btn.setProperty("stop_id", str(stop['stop_id']))
            remove_btn.setProperty("stop_name", stop['name'])
            remove_btn.clicked.connect(self._on_remove_stop)
            tab.setCellWidget(row, 5, remove_btn)
        
        # 调整列宽
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        return tab
    
    def _create_consolidation_tab(self):
        """
        创建可合并站点标签页
        """
        tab = QTableWidget()
        tab.setRowCount(len(self.results['consolidation_candidates']))
        tab.setColumnCount(4)
        
        # 设置表头
        tab.setHorizontalHeaderLabels([
            "Distance(km)", "Keep stop", "Remove stop", "Operation"
        ])
        
        # 填充数据
        for row, pair in enumerate(self.results['consolidation_candidates']):
            tab.setItem(row, 0, QTableWidgetItem(f"{pair['distance']:.2f}"))
            tab.setItem(row, 1, QTableWidgetItem(pair['keep_stop']['name']))
            tab.setItem(row, 2, QTableWidgetItem(pair['remove_stop']['name']))
            
            # 添加合并按钮
            merge_btn = QPushButton("Merge")
            merge_btn.setProperty("keep_id", pair['keep_stop']['id'])
            merge_btn.setProperty("keep_name", pair['keep_stop']['name'])
            merge_btn.setProperty("remove_id", pair['remove_stop']['id'])
            merge_btn.setProperty("remove_name", pair['remove_stop']['name'])
            merge_btn.clicked.connect(self._on_merge_stops)
            tab.setCellWidget(row, 3, merge_btn)
        
        # 调整列宽
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        return tab
    
    def _create_new_stops_tab(self):
        """
        创建新站点建议标签页
        """
        tab = QTableWidget()
        tab.setRowCount(len(self.results['new_stop_suggestions']))
        tab.setColumnCount(5)
        
        # 设置表头
        tab.setHorizontalHeaderLabels([
            "Latitude", "Longitude", "Connected stops", "Distance(km)", "Operation"
        ])
        
        # 填充数据
        for row, suggestion in enumerate(self.results['new_stop_suggestions']):
            tab.setItem(row, 0, QTableWidgetItem(f"{suggestion['latitude']:.6f}"))
            tab.setItem(row, 1, QTableWidgetItem(f"{suggestion['longitude']:.6f}"))
            tab.setItem(row, 2, QTableWidgetItem(" - ".join(suggestion['connects'])))
            tab.setItem(row, 3, QTableWidgetItem(f"{suggestion['distance']:.2f}"))
            
            # 添加添加按钮
            add_btn = QPushButton("Add")
            add_btn.setProperty("latitude", suggestion['latitude'])
            add_btn.setProperty("longitude", suggestion['longitude'])
            add_btn.setProperty("connects", suggestion['connects'])
            add_btn.clicked.connect(self._on_add_stop)
            tab.setCellWidget(row, 4, add_btn)
        
        # 调整列宽
        tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        return tab
    
    def _on_remove_stop(self):
        """
        处理删除站点按钮点击事件
        """
        sender = self.sender()
        stop_id = sender.property("stop_id")
        stop_name = sender.property("stop_name")
        
        reply = QMessageBox.question(
            self, 
            'Confirm deletion', 
            f'Are you sure you want to delete stop {stop_name} (ID: {stop_id})?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 发出信号
            self.remove_stop_signal.emit(stop_id)
            QMessageBox.information(self, "Success", f"Stop {stop_name} has been marked for deletion")
    
    def _on_merge_stops(self):
        """
        处理合并站点按钮点击事件
        """
        sender = self.sender()
        keep_id = sender.property("keep_id")
        keep_name = sender.property("keep_name")
        remove_id = sender.property("remove_id")
        remove_name = sender.property("remove_name")
        
        reply = QMessageBox.question(
            self, 
            'Confirm merge', 
            f'Are you sure you want to merge stops?\nKeep: {keep_name}\nRemove: {remove_name}',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 发出信号
            self.remove_stop_signal.emit(remove_id)
            QMessageBox.information(
                self, 
                "Success", 
                f"Stops have been merged: {remove_name} merged into {keep_name}"
            )
    
    def _on_add_stop(self):
        """
        处理添加站点按钮点击事件
        """
        sender = self.sender()
        latitude = sender.property("latitude")
        longitude = sender.property("longitude")
        connects = sender.property("connects")
        
        # 生成新站点名称
        new_name = f"New Stop ({', '.join(connects)})"
        
        # 构建提示信息，包括将创建的连接
        connection_info = "\n".join([f"- {connect}" for connect in connects])
        
        reply = QMessageBox.question(
            self, 
            'Confirm addition', 
            f'Are you sure you want to add a new stop at the following location?\n'
            f'Latitude: {latitude:.6f}\n'
            f'Longitude: {longitude:.6f}\n'
            f'Name: {new_name}\n\n'
            f'The following connections will be created:\n{connection_info}',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 发出信号，包含连接站点信息
            self.add_stop_signal.emit(latitude, longitude, new_name, connects)
            QMessageBox.information(
                self, 
                "Success", 
                f"New stop {new_name} has been added with connections to {' and '.join(connects)}"
            ) 