from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QGridLayout
from PyQt5.QtCore import Qt
from ui.draggable_graph_frame import DraggableGraphFrame

class PlaygroundArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.container.setMinimumSize(2000, 1500)  # Arbitrary large size to scroll around

        self.scroll_area.setWidget(self.container)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

        self.graph_count = 0

    def add_widget(self, widget):
        frame = DraggableGraphFrame(widget)
        frame.move(50 + self.graph_count * 30, 50 + self.graph_count * 30)  # Stagger placement
        frame.setParent(self.container)
        frame.show()
        self.graph_count += 1