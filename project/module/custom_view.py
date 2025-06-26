from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        pos = self.mapToScene(event.pos())
        self.parent.handle_station_hover(pos)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            self.parent.handle_station_click(pos)