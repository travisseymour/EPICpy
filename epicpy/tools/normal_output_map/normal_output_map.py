# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections import Counter

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QColor, QFont, QGuiApplication, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from epicpy.widgets.mem_large_text_view import MemLargeTextView

from .nom_settings_dialog import NOMSettingsDialog
from .parser import (
    DEFAULT_RESPONSE_CLAUSE,
    DEFAULT_STIMULUS_ONSET_CLAUSE,
    DEFAULT_TRIAL_START_RULE,
    RESPONSE_MADE_LABEL,
    STIMULUS_ONSET_LABEL,
    TrialData,
    parse_normal_output_lines,
)

_HIGHLIGHT_BG = QColor(255, 255, 180)  # pale yellow for pseudo-events
_DUPLICATE_BG = QColor(210, 230, 255)  # light blue for repeated rules
_HIGHLIGHT_FG = QColor(0, 0, 0)  # black text for highlighted rows (readable in dark mode)

_MAX_COL_WIDTH = 460  # max default width in pixels for text-heavy columns

# column indices
_COL_TRIAL = 0
_COL_CYCLE = 1
_COL_DELAY = 2
_COL_POSTSTIM = 3
_COL_RULE = 4
_COL_ADD = 5
_COL_DELETE = 6
_COL_MOTOR = 7


class NormalOutputMapWindow(QMainWindow):
    """Window for visualizing EPIC rule flow from Normal Output traces."""

    def __init__(self, trace_widget: MemLargeTextView):
        super().__init__()

        self.trace_widget: MemLargeTextView = trace_widget
        self.trials: list[TrialData] = []
        self.current_idx = 0

        # Load parse parameters from settings
        self._settings = QSettings("EPICpy", "NormalOutputMap")
        self._trial_start_rule = self._settings.value("trial_start_rule", DEFAULT_TRIAL_START_RULE)
        self._stimulus_onset_clause = self._settings.value("stimulus_onset_clause", DEFAULT_STIMULUS_ONSET_CLAUSE)
        self._response_clause = self._settings.value("response_clause", DEFAULT_RESPONSE_CLAUSE)

        self.setWindowTitle("EPICpy: Normal Output Map")
        self.setMinimumSize(750, 520)

        # Restore saved geometry, fall back to default size
        geometry = self._settings.value("window/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        else:
            self.resize(1300, 1000)

        # Build menu bar
        self._build_menus()

        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)

        # --- prev button ---
        self.prev_btn = QPushButton("\u25C0")
        self.prev_btn.setFixedWidth(38)
        self.prev_btn.setToolTip("Previous trial")
        self.prev_btn.clicked.connect(self._prev)
        outer.addWidget(self.prev_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        # --- centre: header + table ---
        centre = QVBoxLayout()

        self.header = QLabel()
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hfont = self.header.font()
        hfont.setPointSize(hfont.pointSize() + 2)
        hfont.setBold(True)
        self.header.setFont(hfont)
        centre.addWidget(self.header)

        self.table = QTableWidget()
        table_font = self.table.font()
        table_font.setPointSize(table_font.pointSize() + 2)
        self.table.setFont(table_font)
        self.table.horizontalHeader().setFont(table_font)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["Trial", "Cycle", "Delay (ms)", "PostStim (ms)", "Rule Name", "Add", "Delete", "Motor"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Alternating colors applied manually in _refresh() so custom backgrounds take precedence
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Column-width persistence: restore saved widths or auto-size later
        self._user_resized_columns = False
        self._programmatic_resize = False
        saved_widths = self._settings.value("columns/widths")
        if saved_widths is not None and len(saved_widths) == self.table.columnCount():
            for col, width in enumerate(saved_widths):
                self.table.setColumnWidth(col, int(width))
            self._user_resized_columns = True
        header.sectionResized.connect(self._on_section_resized)

        centre.addWidget(self.table)

        outer.addLayout(centre, stretch=1)

        # --- next button ---
        self.next_btn = QPushButton("\u25B6")
        self.next_btn.setFixedWidth(38)
        self.next_btn.setToolTip("Next trial")
        self.next_btn.clicked.connect(self._next)
        outer.addWidget(self.next_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Keyboard shortcuts
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, activated=self._prev)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, activated=self._next)

        # Apply saved column visibility
        self._apply_column_visibility()

    def _build_menus(self) -> None:
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        export_action = QAction("&Export to CSV...", self)
        export_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        close_action = QAction("&Close", self)
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self._show_settings)
        edit_menu.addAction(settings_action)

        reparse_action = QAction("&Re-parse Output", self)
        reparse_action.setShortcut(QKeySequence.StandardKey.Refresh)
        reparse_action.triggered.connect(self.parse_and_display)
        edit_menu.addAction(reparse_action)

        # View menu (column visibility)
        view_menu = menubar.addMenu("&View")

        self._add_action = QAction("Show Add Column", self, checkable=True)
        self._add_action.setChecked(self._settings.value("columns/add", True, type=bool))
        self._add_action.toggled.connect(self._toggle_column_visibility)
        view_menu.addAction(self._add_action)

        self._delete_action = QAction("Show Delete Column", self, checkable=True)
        self._delete_action.setChecked(self._settings.value("columns/delete", True, type=bool))
        self._delete_action.toggled.connect(self._toggle_column_visibility)
        view_menu.addAction(self._delete_action)

        self._motor_action = QAction("Show Motor Column", self, checkable=True)
        self._motor_action.setChecked(self._settings.value("columns/motor", True, type=bool))
        self._motor_action.toggled.connect(self._toggle_column_visibility)
        view_menu.addAction(self._motor_action)

    def _on_section_resized(self) -> None:
        if not self._programmatic_resize:
            self._user_resized_columns = True

    def _toggle_column_visibility(self) -> None:
        self._apply_column_visibility()

    def _apply_column_visibility(self) -> None:
        self.table.setColumnHidden(_COL_ADD, not self._add_action.isChecked())
        self.table.setColumnHidden(_COL_DELETE, not self._delete_action.isChecked())
        self.table.setColumnHidden(_COL_MOTOR, not self._motor_action.isChecked())

    def _show_settings(self) -> None:
        """Show the settings dialog and re-parse if OK was clicked."""
        dialog = NOMSettingsDialog(self)
        dialog.setModal(True)
        dialog.exec()

        if dialog.ok:
            # Update stored parameters
            self._trial_start_rule = dialog.trial_start_rule
            self._stimulus_onset_clause = dialog.stimulus_onset_clause
            self._response_clause = dialog.response_clause
            # Re-parse with new settings
            self.parse_and_display()

    def _export_csv(self) -> None:
        """Export all trial data to a CSV file."""
        if not self.trials:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not filepath:
            return

        import csv

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Trial", "Cycle", "Delay (ms)", "PostStim (ms)", "Rule Name", "Add", "Delete", "Motor"])

            for trial in self.trials:
                for ev in trial.events:
                    motor_text = ", ".join(c.replace("Send_to_motor ", "") for c in ev.commands)
                    writer.writerow([
                        ev.trial,
                        ev.cycle,
                        ev.delay_ms,
                        ev.post_stim_ms if ev.post_stim_ms is not None else "-",
                        ev.rule_name,
                        ", ".join(ev.adds),
                        ", ".join(ev.deletes),
                        motor_text,
                    ])

    def closeEvent(self, event) -> None:
        self._settings.setValue("window/geometry", self.saveGeometry())
        self._settings.setValue("columns/add", self._add_action.isChecked())
        self._settings.setValue("columns/delete", self._delete_action.isChecked())
        self._settings.setValue("columns/motor", self._motor_action.isChecked())
        widths = [self.table.columnWidth(c) for c in range(self.table.columnCount())]
        self._settings.setValue("columns/widths", widths)
        self.trials = []
        super().closeEvent(event)

    # ---- navigation ----

    def _prev(self) -> None:
        if self.current_idx > 0:
            self.current_idx -= 1
            self._refresh()

    def _next(self) -> None:
        if self.current_idx < len(self.trials) - 1:
            self.current_idx += 1
            self._refresh()

    # ---- parsing and display ----

    def parse_and_display(self) -> None:
        """Parse the normal output from the trace widget and display results."""
        self.trials = parse_normal_output_lines(
            lines=self.trace_widget.lines,
            trial_start_rule=self._trial_start_rule,
            stimulus_onset_clause=self._stimulus_onset_clause,
            response_clause=self._response_clause,
        )
        self.current_idx = 0
        self._user_resized_columns = False
        self._refresh()

    def _refresh(self) -> None:
        if not self.trials:
            self.header.setText("No trials found")
            self.table.setRowCount(0)
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return

        trial = self.trials[self.current_idx]
        self.header.setText(f"Trial {trial.trial_number} of {len(self.trials)}")

        self.prev_btn.setEnabled(self.current_idx > 0)
        self.next_btn.setEnabled(self.current_idx < len(self.trials) - 1)

        events = trial.events
        self.table.setRowCount(len(events))

        bold_font = QFont(self.table.font())
        bold_font.setBold(True)

        # Get alternating row color from palette for manual application
        alt_base = self.table.palette().alternateBase().color()

        # Find rule names that appear more than once (excluding pseudo-events)
        rule_counts: Counter[str] = Counter()
        for ev in events:
            if ev.rule_name not in (STIMULUS_ONSET_LABEL, RESPONSE_MADE_LABEL):
                rule_counts[ev.rule_name] += 1
        duplicated_rules = {name for name, cnt in rule_counts.items() if cnt > 1}

        for row, ev in enumerate(events):
            is_pseudo = ev.rule_name in (STIMULUS_ONSET_LABEL, RESPONSE_MADE_LABEL)
            is_duplicate = ev.rule_name in duplicated_rules

            motor_text = ", ".join(c.replace("Send_to_motor ", "") for c in ev.commands)

            items = [
                QTableWidgetItem(str(ev.trial)),
                QTableWidgetItem(str(ev.cycle)),
                QTableWidgetItem(str(ev.delay_ms)),
                QTableWidgetItem(str(ev.post_stim_ms) if ev.post_stim_ms is not None else "-"),
                QTableWidgetItem(ev.rule_name),
                QTableWidgetItem(", ".join(ev.adds)),
                QTableWidgetItem(", ".join(ev.deletes)),
                QTableWidgetItem(motor_text),
            ]

            # Right-align numeric columns
            for i in (_COL_TRIAL, _COL_DELAY, _COL_POSTSTIM, _COL_CYCLE):
                items[i].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            if is_pseudo:
                for item in items:
                    item.setFont(bold_font)
                    item.setBackground(_HIGHLIGHT_BG)
                    item.setForeground(_HIGHLIGHT_FG)
            elif is_duplicate:
                for item in items:
                    item.setBackground(_DUPLICATE_BG)
                    item.setForeground(_HIGHLIGHT_FG)
            elif row % 2 == 1:
                # Manually apply alternating color only to non-highlighted rows
                for item in items:
                    item.setBackground(alt_base)

            for col, item in enumerate(items):
                self.table.setItem(row, col, item)

        if not self._user_resized_columns:
            self._programmatic_resize = True
            # Auto-size numeric columns
            for col in (_COL_TRIAL, _COL_CYCLE, _COL_DELAY, _COL_POSTSTIM):
                self.table.resizeColumnToContents(col)
            # For text-heavy columns: use fixed default if content exists, else auto-size to header
            has_adds = any(ev.adds for ev in events)
            has_deletes = any(ev.deletes for ev in events)
            has_motor = any(ev.commands for ev in events)
            col_has_content = {
                _COL_RULE: True,  # always has rule names
                _COL_ADD: has_adds,
                _COL_DELETE: has_deletes,
                _COL_MOTOR: has_motor,
            }
            for col in (_COL_RULE, _COL_ADD, _COL_DELETE, _COL_MOTOR):
                if col_has_content[col]:
                    self.table.setColumnWidth(col, _MAX_COL_WIDTH)
                else:
                    self.table.resizeColumnToContents(col)
            self._programmatic_resize = False

    def center_me(self):
        """Center window on the same screen as the parent application."""
        parent_window = self.trace_widget.window()
        if parent_window:
            screen = parent_window.screen()
        else:
            screen = QGuiApplication.screens()[0]
        center_point = screen.geometry().center()
        self.move(center_point - self.frameGeometry().center())

    def showEvent(self, event):
        super().showEvent(event)
        self.center_me()
        self.activateWindow()
        self.raise_()
