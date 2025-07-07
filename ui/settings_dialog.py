from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QMessageBox
)
from .draggable_list import DraggableList

class ComparisonSettingsDialog(QDialog):
    def __init__(self, drivers, selected=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comparison Mode Setup")
        self.setGeometry(300, 200, 600, 400)
        self.selected_drivers = selected if selected else []

        layout = QHBoxLayout()

        self.available_list = DraggableList()
        self.available_list.setSelectionMode(self.available_list.SingleSelection)
        self.available_list.setDragDropMode(self.available_list.DragDrop)
        for d in drivers:
            if d not in self.selected_drivers:
                self.available_list.addItem(d)

        self.selected_list = DraggableList()
        for d in self.selected_drivers:
            self.selected_list.addItem(d)

        layout.addWidget(QLabel("Available Drivers"))
        layout.addWidget(self.available_list)
        layout.addWidget(QLabel("Compare These"))
        layout.addWidget(self.selected_list)

        btn_layout = QVBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_selection)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def save_selection(self):
        items = [self.selected_list.item(i).text() for i in range(self.selected_list.count())]
        if len(items) > 5:
            QMessageBox.warning(self, "Too Many", "Please select a maximum of 5 drivers.")
            return
        self.selected_drivers = items
        self.accept()

    def get_selected_drivers(self):
        return self.selected_drivers
