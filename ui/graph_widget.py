from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors
import fastf1
import matplotlib.pyplot as plt
from matplotlib import style

from logic.telemetry_loader import load_session_data, get_driver_laps
from logic.plotter import plot_lap_telemetry, plot_comparison_telemetry
from ui.settings_dialog import ComparisonSettingsDialog

fastf1.Cache.enable_cache('./resources/cache')

class GraphWidget(QWidget):
    def __init__(self, parent=None, session=None):
        super().__init__(parent)
        self.session = session
        self.comparison_drivers = []
        self.event_schedule = {}
        
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                font-family: Arial;
            }
            QComboBox, QPushButton {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 80px;
                color: #ffffff;
            }
            QComboBox:hover, QPushButton:hover {
                background-color: #4d4d4d;
            }
            QComboBox QAbstractItemView {
                background-color: #3d3d3d;
                color: #ffffff;
                selection-background-color: #4d4d4d;
            }
            QLabel {
                color: #000000;
                background: transparent;
            }
            QTabBar::tab {
                background: #3d3d3d;
                color: #ffffff;
                padding: 8px 16px;
                border: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #1e90ff;
                color: white;
            }
            QTabBar::tab:!selected {
                background: #3d3d3d;
            }
        """)
        
        self.setup_ui()
        self.init_plot()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        self.setLayout(main_layout)

        # === TOP BAR 1 ===
        top_row = QHBoxLayout()
        top_row.setSpacing(4)
        top_row.setContentsMargins(8, 8, 8, 0)

        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Single Driver", "Comparison Mode"])
        self.mode_dropdown.currentIndexChanged.connect(self.on_mode_changed)
        top_row.addWidget(QLabel("Mode:"))
        top_row.addWidget(self.mode_dropdown)

        self.year_dropdown = QComboBox()
        self.year_dropdown.addItems(["2021", "2022", "2023", "2024"])
        self.year_dropdown.currentIndexChanged.connect(self.load_event_schedule)
        top_row.addWidget(QLabel("Year:"))
        top_row.addWidget(self.year_dropdown)

        self.race_dropdown = QComboBox()
        self.race_dropdown.currentIndexChanged.connect(self.update_circuit_info)
        top_row.addWidget(QLabel("GP:"))
        top_row.addWidget(self.race_dropdown)

        self.session_dropdown = QComboBox()
        self.session_dropdown.addItems(["Q", "R", "FP1", "FP2"])
        top_row.addWidget(QLabel("Session:"))
        top_row.addWidget(self.session_dropdown)

        main_layout.addLayout(top_row)

        # === TOP BAR 2 ===
        second_row = QHBoxLayout()
        second_row.setSpacing(4)
        second_row.setContentsMargins(8, 0, 8, 0)

        self.driver_dropdown = QComboBox()
        second_row.addWidget(QLabel("Driver:"))
        second_row.addWidget(self.driver_dropdown)
        self.driver_dropdown.currentIndexChanged.connect(self.populate_lap_dropdown)

        self.lap_dropdown = QComboBox()
        second_row.addWidget(QLabel("Lap:"))
        second_row.addWidget(self.lap_dropdown)
        self.lap_dropdown.currentIndexChanged.connect(self.on_lap_selected)

        self.load_button = QPushButton("Load Telemetry")
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #1e90ff;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1a7fdd;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
                color: #888888;
            }
        """)
        self.load_button.clicked.connect(self.load_session)
        second_row.addWidget(self.load_button)

        self.settings_button = QPushButton("⚙️")
        self.settings_button.setVisible(False)
        self.settings_button.clicked.connect(self.open_comparison_settings)
        second_row.addWidget(self.settings_button)

        main_layout.addLayout(second_row)

        # === Circuit Info ===
        # Circuit info with minimal styling and no background
        self.circuit_info_label = QLabel("Circuit Info: ")
        self.circuit_info_label.setStyleSheet("""
            padding: 4px 8px;
            font-weight: bold;
            background: transparent;
            color: #000000;
        """)
        main_layout.addWidget(self.circuit_info_label)

    def init_plot(self):
        self.tabs = QTabWidget()
        self.speed_canvas = self.create_plot_canvas("Speed")
        self.throttle_canvas = self.create_plot_canvas("Throttle")
        self.brake_canvas = self.create_plot_canvas("Brake")
        self.gear_canvas = self.create_plot_canvas("Gear")

        self.tabs.addTab(self.speed_canvas, "Speed")
        self.tabs.addTab(self.throttle_canvas, "Throttle")
        self.tabs.addTab(self.brake_canvas, "Brake")
        self.tabs.addTab(self.gear_canvas, "Gear")

        self.layout().addWidget(self.tabs)

    def create_plot_canvas(self, title):
        # Set dark theme for matplotlib
        plt.style.use('dark_background')
        
        fig = Figure(figsize=(8, 4), tight_layout=True)
        fig.set_facecolor('#2d2d2d')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Style the plot - remove borders and adjust colors
        ax.set_facecolor('#2d2d2d')
        ax.grid(True, color='#4d4d4d', linestyle='--', alpha=0.5)
        
        # Remove the border (spines)
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.tick_params(axis='x', colors='#ffffff')
        ax.tick_params(axis='y', colors='#ffffff')
        ax.xaxis.label.set_color('#ffffff')
        ax.yaxis.label.set_color('#ffffff')
        ax.title.set_color('#ffffff')
        
        # Set title with better styling
        ax.set_title(title, color='#ffffff', pad=10, fontsize=11, fontweight='bold')
        
        canvas.ax = ax
        mplcursors.cursor(ax, hover=True)
        return canvas

    def on_mode_changed(self):
        is_comparison = self.mode_dropdown.currentText() == "Comparison Mode"
        self.driver_dropdown.setVisible(not is_comparison)
        self.lap_dropdown.setVisible(not is_comparison)
        self.settings_button.setVisible(is_comparison)

    def load_event_schedule(self):
        year = int(self.year_dropdown.currentText())
        try:
            schedule = fastf1.get_event_schedule(year)
            self.event_schedule.clear()
            self.race_dropdown.clear()
            for _, event in schedule.iterrows():
                self.race_dropdown.addItem(event['EventName'])
                self.event_schedule[event['EventName']] = {
                    'round': event['RoundNumber'],
                    'circuit': event['Location'],
                    'country': event['Country'],
                    'date': event['EventDate']
                }
        except Exception as e:
            self.race_dropdown.clear()
            self.race_dropdown.addItem("Error loading")
            print(f"[ERROR] {e}")

    def update_circuit_info(self):
        event = self.event_schedule.get(self.race_dropdown.currentText())
        if event:
            self.circuit_info_label.setText(
                f"Circuit Info: {event['circuit']}, {event['country']} ({event['date'].date()})"
            )

    def load_session(self):
        year = int(self.year_dropdown.currentText())
        race = self.race_dropdown.currentText()
        session_type = self.session_dropdown.currentText()
        event = self.event_schedule.get(race)

        if not event:
            QMessageBox.warning(self, "Error", "Invalid race selection.")
            return

        self.load_button.setEnabled(False)
        self.load_button.setText("Loading...")

        try:
            self.session = load_session_data(year, event['round'], session_type)
            drivers = sorted(self.session.laps['Driver'].unique())

            self.driver_dropdown.clear()
            self.driver_dropdown.addItems(drivers)
            self.populate_lap_dropdown()
            self.update_circuit_info()

        except Exception as e:
            QMessageBox.critical(self, "Load Failed", str(e))
        finally:
            self.load_button.setEnabled(True)
            self.load_button.setText("Load Telemetry")

    def populate_lap_dropdown(self):
        driver = self.driver_dropdown.currentText()
        if not driver or not self.session:
            return
        try:
            laps = get_driver_laps(self.session, driver)
            self.lap_dropdown.clear()
            for _, lap in laps.iterlaps():
                lap_num = lap['LapNumber']
                lap_time = str(lap['LapTime']).split('.')[0]
                self.lap_dropdown.addItem(f"Lap {lap_num} - {lap_time}", userData=lap_num)
            if not laps.empty:
                self.plot_lap(laps.pick_fastest())
        except Exception as e:
            print(f"[ERROR] Lap populate: {e}")

    def on_lap_selected(self):
        driver = self.driver_dropdown.currentText()
        lap_number = self.lap_dropdown.currentData()
        laps = get_driver_laps(self.session, driver)
        lap = laps[laps['LapNumber'] == lap_number]
        if not lap.empty:
            self.plot_lap(lap.iloc[0])

    def plot_lap(self, lap):
        plot_lap_telemetry(lap, self.speed_canvas, self.throttle_canvas,
                           self.brake_canvas, self.gear_canvas)

    def open_comparison_settings(self):
        if not self.session:
            QMessageBox.information(self, "No Session", "Load a session first.")
            return

        drivers = sorted(self.session.laps['Driver'].unique())
        dialog = ComparisonSettingsDialog(drivers, self.comparison_drivers, self)
        if dialog.exec_():
            self.comparison_drivers = dialog.get_selected_drivers()
            self.plot_comparison()

    def plot_comparison(self):
        plot_comparison_telemetry(self.session, self.comparison_drivers,
                                  self.speed_canvas, self.throttle_canvas,
                                  self.brake_canvas, self.gear_canvas)
