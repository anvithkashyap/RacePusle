from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QPoint, QSize

class DraggableGraphFrame(QFrame):
    def __init__(self, inner_widget, parent=None):
        super().__init__(parent)
        self.inner_widget = inner_widget
        self.init_ui()
        self.setMouseTracking(True)
        self.resize(600, 400)
        self.dragging = False
        self.resizing = False

    def init_ui(self):
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("background-color: white; border: 2px solid #666;")

        # --- Header with Close Button ---
        header = QHBoxLayout()
        self.title = QPushButton("✦")
        self.title.setEnabled(False)
        self.title.setFlat(True)
        self.title.setStyleSheet("font-weight: bold; background: none;")

        close_btn = QPushButton("❌")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.deleteLater)

        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(close_btn)

        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.addLayout(header)
        wrapper_layout.addWidget(self.inner_widget)

        self.setLayout(wrapper_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.cursor().shape() == Qt.SizeFDiagCursor:
                self.resizing = True
            else:
                self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.resizing:
            diff = event.pos() - self.offset
            new_size = self.size() + QSize(diff.x(), diff.y())
            self.resize(new_size)
            self.offset = event.pos()
        elif self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))
        else:
            margin = 10
            if event.x() > self.width() - margin and event.y() > self.height() - margin:
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False