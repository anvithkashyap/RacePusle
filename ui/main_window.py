from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import fastf1
import mplcursors

from .settings_dialog import ComparisonSettingsDialog
from logic.telemetry_loader import load_session_data, get_driver_laps
from logic.plotter import plot_lap_telemetry, plot_comparison_telemetry
from ui.playground_area import PlaygroundArea
from ui.graph_widget import GraphWidget

fastf1.Cache.enable_cache('./resources/cache')


class RacePulseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RacePulse - Motorsport Telemetry")
        self.setGeometry(100, 100, 1200, 700)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.session = None
        self.comparison_drivers = []
        self.event_schedule = {}

        self.init_ui()
        self.init_plot()

    def init_ui(self):
        self.top_bar = QHBoxLayout()

        # Mode
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Single Driver", "Comparison Mode", "Playground"])
        self.mode_dropdown.currentIndexChanged.connect(self.on_mode_changed)
        self.top_bar.addWidget(QLabel("Mode:"))
        self.top_bar.addWidget(self.mode_dropdown)

        # Other dropdowns (hidden in Playground)
        self.year_dropdown = QComboBox()
        self.year_dropdown.addItems(["2021", "2022", "2023", "2024"])
        self.year_dropdown.currentIndexChanged.connect(self.load_event_schedule)

        self.race_dropdown = QComboBox()
        self.race_dropdown.currentIndexChanged.connect(self.update_circuit_info)

        self.session_dropdown = QComboBox()
        self.session_dropdown.addItems(["Q", "R", "FP1", "FP2"])

        self.driver_dropdown = QComboBox()
        self.driver_dropdown.currentIndexChanged.connect(self.populate_lap_dropdown)

        self.lap_dropdown = QComboBox()
        self.lap_dropdown.currentIndexChanged.connect(self.on_lap_selected)

        self.load_button = QPushButton("Load Telemetry")
        self.load_button.clicked.connect(self.on_load_clicked)

        self.settings_button = QPushButton("⚙️ Comparison Settings")
        self.settings_button.clicked.connect(self.open_comparison_settings)

        self.add_graph_button = QPushButton("➕ Add Graph")
        self.add_graph_button.clicked.connect(self.add_graph_to_playground)

        self.circuit_info_label = QLabel("Circuit Info:")

        for w in [
            QLabel("Year:"), self.year_dropdown,
            QLabel("GP:"), self.race_dropdown,
            QLabel("Session:"), self.session_dropdown,
            QLabel("Driver:"), self.driver_dropdown,
            QLabel("Lap:"), self.lap_dropdown,
            self.load_button,
            self.settings_button,
            self.add_graph_button,
            self.circuit_info_label
        ]:
            self.top_bar.addWidget(w)

        self.layout.addLayout(self.top_bar)

        self.podium_label = QLabel("")
        self.podium_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.layout.addWidget(self.podium_label)

        self.playground_area = PlaygroundArea()
        self.layout.addWidget(self.playground_area)
        self.playground_area.setVisible(False)

    def init_plot(self):
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.speed_canvas = self.create_plot_canvas("Speed")
        self.throttle_canvas = self.create_plot_canvas("Throttle")
        self.brake_canvas = self.create_plot_canvas("Brake")
        self.gear_canvas = self.create_plot_canvas("Gear")

        self.tabs.addTab(self.speed_canvas, "Speed")
        self.tabs.addTab(self.throttle_canvas, "Throttle")
        self.tabs.addTab(self.brake_canvas, "Brake")
        self.tabs.addTab(self.gear_canvas, "Gear")

    def create_plot_canvas(self, title):
        fig = Figure(figsize=(6, 4), tight_layout=True)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.set_title(title)
        canvas.ax = ax
        canvas.setFocusPolicy(Qt.ClickFocus)
        canvas.setFocus()
        mplcursors.cursor(ax, hover=True)

        def zoom(event):
            if event.inaxes is None:
                return
            base_scale = 1.2
            ax = event.inaxes
            x_min, x_max = ax.get_xlim()
            y_min, y_max = ax.get_ylim()
            x_range = x_max - x_min
            y_range = y_max - y_min

            scale_factor = 1 / base_scale if event.button == 'up' else base_scale
            new_width = x_range * scale_factor
            new_height = y_range * scale_factor
            relx = (event.xdata - x_min) / x_range
            rely = (event.ydata - y_min) / y_range

            ax.set_xlim([
                event.xdata - new_width * relx,
                event.xdata + new_width * (1 - relx)
            ])
            ax.set_ylim([
                event.ydata - new_height * rely,
                event.ydata + new_height * (1 - rely)
            ])
            canvas.draw()

        def pan_start(event):
            if event.button == 1 and event.inaxes:
                canvas._pan_start = event

        def pan_move(event):
            if event.button == 1 and hasattr(canvas, "_pan_start"):
                dx = canvas._pan_start.xdata - event.xdata
                dy = canvas._pan_start.ydata - event.ydata
                ax = canvas._pan_start.inaxes
                ax.set_xlim(ax.get_xlim()[0] + dx, ax.get_xlim()[1] + dx)
                ax.set_ylim(ax.get_ylim()[0] + dy, ax.get_ylim()[1] + dy)
                canvas.draw()

        fig.canvas.mpl_connect('scroll_event', zoom)
        fig.canvas.mpl_connect('button_press_event', pan_start)
        fig.canvas.mpl_connect('motion_notify_event', pan_move)

        return canvas

    def load_event_schedule(self):
        year = int(self.year_dropdown.currentText())
        try:
            schedule = fastf1.get_event_schedule(year)
            self.event_schedule.clear()
            self.race_dropdown.clear()

            for _, event in schedule.iterrows():
                name = event['EventName']
                self.race_dropdown.addItem(name)
                self.event_schedule[name] = {
                    'round': event['RoundNumber'],
                    'circuit': event['Location'],
                    'country': event['Country'],
                    'date': event['EventDate']
                }

        except Exception as e:
            self.race_dropdown.clear()
            self.race_dropdown.addItem("Error loading")
            print(f"[Schedule ERROR]: {e}")

    def update_circuit_info(self):
        event = self.event_schedule.get(self.race_dropdown.currentText())
        if event:
            self.circuit_info_label.setText(
                f"Circuit Info: {event['circuit']}, {event['country']} ({event['date'].date()})"
            )

    def on_mode_changed(self):
        mode = self.mode_dropdown.currentText()
        playground = mode == "Playground"
        comparison = mode == "Comparison Mode"

        # Toggle visibility
        for widget in [
            self.year_dropdown, self.race_dropdown,
            self.session_dropdown, self.driver_dropdown,
            self.lap_dropdown, self.load_button,
            self.settings_button, self.circuit_info_label,
            self.podium_label, self.tabs
        ]:
            widget.setVisible(not playground)

        self.add_graph_button.setVisible(playground)
        self.playground_area.setVisible(playground)

    def on_load_clicked(self):
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
            self.display_session_highlights(session_type)

        except Exception as e:
            QMessageBox.critical(self, "Session Load Failed", str(e))

        finally:
            self.load_button.setEnabled(True)
            self.load_button.setText("Load Telemetry")

    def display_session_highlights(self, session_type):
        podium_text = ""
        try:
            if session_type == "R":
                res = self.session.results.head(3)
                podium_text = f"<pre>\n🥇 {res.iloc[0]['Abbreviation']}   🥈 {res.iloc[1]['Abbreviation']}   🥉 {res.iloc[2]['Abbreviation']}\n</pre>"
            elif session_type == "Q":
                pole = str(self.session.results.iloc[0]['Abbreviation'])
                podium_text = f"<b>🏁 Pole:</b> {pole}"
            else:
                podium_text = "📊 No podium data for this session."

            self.podium_label.setText(podium_text)
        except Exception as e:
            self.podium_label.setText(f"<i>Error loading podium data: {e}</i>")

    def populate_lap_dropdown(self):
        driver = self.driver_dropdown.currentText()
        if not driver or not self.session:
            return

        try:
            laps = get_driver_laps(self.session, driver)
            self.lap_dropdown.clear()

            for _, lap in laps.iterlaps():
                lap_num = lap['LapNumber']
                time = str(lap['LapTime']).split('.')[0]
                self.lap_dropdown.addItem(f"Lap {lap_num} - {time}", userData=lap_num)

            if laps:
                self.plot_lap(laps.pick_fastest())

        except Exception as e:
            print(f"[Lap Error]: {e}")

    def on_lap_selected(self):
        if not self.session:
            return
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
            QMessageBox.information(self, "Load First", "Load a session first.")
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

    def add_graph_to_playground(self):
        widget = GraphWidget()  # New widgets can be initialized without session
        self.playground_area.add_widget(widget)