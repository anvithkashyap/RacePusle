from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag

class DraggableList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QListWidget.DragDrop)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
        mime = QMimeData()
        mime.setText(item.text())

        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            text = event.mimeData().text()

            if not self.findItems(text, Qt.MatchExactly):
                self.addItem(text)

            source = event.source()
            if source and source != self:
                items = source.findItems(text, Qt.MatchExactly)
                for item in items:
                    row = source.row(item)
                    source.takeItem(row)

            event.acceptProposedAction()
        else:
            event.ignore()
