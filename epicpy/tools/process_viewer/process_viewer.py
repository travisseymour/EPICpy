"""
This file is part of the EPICpy source code. EPICpy is a tool for simulating
human performance tasks using the EPIC computational cognitive architecture
(David Kieras and David Meyer 1997a) using the Python programming language.
Copyright (C) 2022-2026 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
Process Viewer - Timeline visualization of EPIC processor activities.

Reads trace output and produces a timeline graph showing processor
activities based on parsing rules.
"""

import timeit
from datetime import datetime

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from epicpy.tools.process_viewer import parse_rules
from epicpy.tools.process_viewer.scheduler import Scheduler
from epicpy.utils.resource_utils import get_resource
from epicpy.widgets.mem_large_text_view import MemLargeTextView

# Color palette for processors
COLORS = [
    (31, 119, 180),  # blue
    (255, 127, 14),  # orange
    (44, 160, 44),  # green
    (214, 39, 40),  # red
    (148, 103, 189),  # purple
    (140, 86, 75),  # brown
    (227, 119, 194),  # pink
    (127, 127, 127),  # gray
    (188, 189, 34),  # olive
    (23, 190, 207),  # cyan
    (255, 187, 120),  # light orange
    (152, 223, 138),  # light green
]


def timestamp_to_ms(ts: str) -> float:
    """Convert timestamp string to milliseconds from midnight."""
    # Format: "1977-01-01 HH:MM:SS.mmm"
    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f")
    return (dt.hour * 3600 + dt.minute * 60 + dt.second) * 1000 + dt.microsecond / 1000


def _load_and_translate_rules() -> list[tuple] | None:
    """Load and translate parsing rules from the resources folder."""
    parse_rule_file = get_resource("other", "process_parsing_rules.txt")

    if not parse_rule_file.is_file():
        return None

    rules = parse_rules.load_parse_rules(parse_rule_file)
    translated = parse_rules.translate(rules)
    return translated


class ProcessViewerWindow(QMainWindow):
    """
    Window displaying a timeline graph of processor activities.

    Reads trace output from a MemLargeTextView and visualizes processor
    activity periods as horizontal bars on a time axis.
    """

    def __init__(self, trace_widget: MemLargeTextView):
        super(ProcessViewerWindow, self).__init__()

        self.trace_widget: MemLargeTextView = trace_widget

        self.setGeometry(100, 100, 1360, 940)
        self.setWindowTitle("EPICpy Process Viewer")

        # Load parsing rules
        self.rules = _load_and_translate_rules()
        if not self.rules:
            QMessageBox.critical(
                self,
                "Configuration Error",
                "Unable to load process parsing rules.\nPlease ensure process_parsing_rules.txt exists in resources/other/",
            )
            return

        # Create central widget with layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(5, 5, 5, 5)

        # Info label
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 14px; padding: 5px;")
        layout.addWidget(self.info_label)

        # PyQtGraph plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(self.plot_widget)

        # Setup scheduler and process data
        self.scheduler = Scheduler(self.rules, time_scale=1.0, flash_delay_ms=100)
        self.process_time = self._process_trace_data()

        # Build the graph
        self.update_graph()
        self.center_me()

    def _process_trace_data(self) -> float:
        """Process all lines from the trace widget."""
        start = timeit.default_timer()
        self.scheduler.process_lines(self.trace_widget.lines)
        elapsed = timeit.default_timer() - start
        return elapsed

    def center_me(self):
        """Center the window on the screen."""
        center_point = QGuiApplication.screens()[0].geometry().center()
        self.move(center_point - self.frameGeometry().center())

    def update_graph(self):
        """Update the timeline graph with processed data."""
        df = self.scheduler.processes

        if df.empty:
            self.info_label.setText("No process data found in trace output")
            return

        self.info_label.setText(f"Processed in: {self.process_time:.3f}s  |  Process events: {self.scheduler.process_count}")

        # Get unique processors and assign y-positions and colors
        processors = df["Processor"].unique().tolist()
        processor_to_y = {p: i for i, p in enumerate(processors)}
        processor_to_color = {p: COLORS[i % len(COLORS)] for i, p in enumerate(processors)}

        # Clear previous items
        self.plot_widget.clear()

        # Create bars for each event
        bar_height = 0.8
        for _, row in df.iterrows():
            processor = str(row["Processor"])
            start_ms = timestamp_to_ms(str(row["Start"]))
            end_ms = timestamp_to_ms(str(row["Finish"]))
            duration = end_ms - start_ms

            y = processor_to_y[processor]
            color = processor_to_color[processor]

            # Create a bar item
            bar = pg.BarGraphItem(
                x=[start_ms + duration / 2],  # center position
                height=[bar_height],
                width=[duration],
                y=[y],
                brush=pg.mkBrush(color),
                pen=pg.mkPen(color, width=1),
            )
            self.plot_widget.addItem(bar)

        # Configure axes
        y_axis = self.plot_widget.getAxis("left")
        y_axis.setTicks([[(i, p) for p, i in processor_to_y.items()]])

        x_axis = self.plot_widget.getAxis("bottom")
        x_axis.setLabel("Time (ms)")

        # Set axis ranges
        self.plot_widget.setYRange(-0.5, len(processors) - 0.5)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self.center_me()
        self.activateWindow()
        self.raise_()
