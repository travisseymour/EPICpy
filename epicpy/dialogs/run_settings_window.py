# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Callable, List

from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
)

from epicpy.epic.run_info import ParameterGridItem
from epicpy.uifiles.run_settings_ui import Ui_DialogRunSettings
from epicpy.utils import config
from epicpy.utils.app_utils import clear_font


class RunSettingsWin(QDialog):
    def __init__(
        self,
        default_device_params: str,
        data_delete_func: Callable | None = None,
        data_info_func: Callable | None = None,
        simulation=None,
    ):
        super(RunSettingsWin, self).__init__()
        self.data_delete_func = data_delete_func
        self.data_info_func = data_info_func
        self.default_device_params = default_device_params
        self.simulation = simulation
        self.ok = False
        self.ui = Ui_DialogRunSettings()
        self.ui.setupUi(self)

        # replace designed font with application-wide font
        clear_font(self)

        if isinstance(self.data_info_func, Callable):
            self.ui.dataInfoLabel.setText(self.data_info_func())

        self.ui.pushButtonClearParams.clicked.connect(self.reset_device_params)

        self.run_group = QButtonGroup(self)
        self.refresh_group = QButtonGroup(self)
        self.refresh_text_group = QButtonGroup(self)

        for rb in (
            self.ui.radioButtonRunUntilDone,
            self.ui.radioButtonRunForCycles,
            self.ui.radioButtonRunUntilSim,
            self.ui.radioButtonRunForSecs,
        ):
            self.run_group.addButton(rb)
        for rb in (
            self.ui.radioButtonRefreshEachCycle,
            self.ui.radioButtonRefreshEachSecs,
            self.ui.radioButtonRefreshNone,
        ):
            self.refresh_group.addButton(rb)
        for rb in (
            self.ui.radioButtonRefreshContinuouslyText,
            self.ui.radioButtonRefreshEachCycleText,
            self.ui.radioButtonRefreshNoneText,
        ):
            self.refresh_text_group.addButton(rb)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)
        self.ui.pushButtonRunContinuously.clicked.connect(self.clicked_continuous_button)
        self.ui.pushButtonDeleteData.clicked.connect(self.delete_device_data)

        self.ui.pushButtonDeleteData.setVisible(self.data_delete_func is not None)

        # Parameter grid support
        self.grid_mode: bool = False
        self.parameter_grid: List[ParameterGridItem] = []

        # Grid radio button and control signals
        # Connect both radio buttons to ensure grid_mode is properly set regardless of which is clicked
        self.ui.radioButtonMultipleParams.toggled.connect(self.toggle_grid_mode)
        self.ui.radioButtonSingleParam.toggled.connect(lambda checked: self.toggle_grid_mode(False) if checked else None)
        self.ui.pushButtonAddRow.clicked.connect(self.add_grid_row)
        self.ui.pushButtonDeleteRow.clicked.connect(self.delete_selected_rows)
        self.ui.pushButtonClearGrid.clicked.connect(self.clear_grid)
        self.ui.tableWidgetParameterGrid.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.ui.tableWidgetParameterGrid.itemChanged.connect(self.on_grid_item_changed)

        if "runsettingswindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["runsettingswindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        # self.setLayout(self.ui.verticalLayout_5)

    def showEvent(self, event: QShowEvent):
        try:
            self.ui.lineEditDeviceParameters.setToolTip(self.simulation.device.condition_hint)
        except Exception:
            ...

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["runsettingswindow"] = [self.width(), self.height()]
        super(RunSettingsWin, self).resizeEvent(event)

    def setup_options(self):
        self.ui.spinBoxRunRealSecs.setValue(config.device_cfg.setting_run_for_real_secs)
        self.ui.spinBoxRunSimMsecs.setValue(config.device_cfg.setting_run_until_msecs)
        self.ui.spinBoxRunSimCycles.setValue(config.device_cfg.setting_run_cycles)
        self.ui.doubleSpinBoxRefreshSecs.setValue(config.device_cfg.setting_refresh_secs)
        self.ui.spinBoxRefreshSteps.setValue(config.device_cfg.setting_refresh_steps)

        if config.device_cfg.run_command == "run_for":
            self.ui.radioButtonRunForSecs.setChecked(True)
            self.ui.spinBoxRunRealSecs.setValue(config.device_cfg.run_command_value)
        elif config.device_cfg.run_command == "run_until":
            self.ui.radioButtonRunUntilSim.setChecked(True)
            self.ui.spinBoxRunSimMsecs.setValue(config.device_cfg.run_command_value)
        elif config.device_cfg.run_command == "run_for_cycles":
            self.ui.radioButtonRunForCycles.setChecked(True)
            self.ui.spinBoxRunSimCycles.setValue(config.device_cfg.run_command_value)
        else:
            self.ui.radioButtonRunUntilDone.setChecked(True)

        if config.device_cfg.display_refresh == "after_each_step":
            self.ui.radioButtonRefreshEachCycle.setChecked(True)
        elif config.device_cfg.display_refresh == "after_every_sec":
            self.ui.radioButtonRefreshEachSecs.setChecked(True)
            self.ui.doubleSpinBoxRefreshSecs.setValue(config.device_cfg.setting_refresh_secs)
        else:
            self.ui.radioButtonRefreshNone.setChecked(True)

        # Enable the "After Every X sec" widgets
        self.ui.radioButtonRefreshEachSecs.setEnabled(True)
        self.ui.doubleSpinBoxRefreshSecs.setEnabled(True)

        # Disable text refresh options that are not currently supported
        dep_msg = "This option is not currently supported."
        self.ui.radioButtonRefreshEachCycleText.setEnabled(False)
        self.ui.radioButtonRefreshEachCycleText.setToolTip(dep_msg)
        self.ui.spinBoxTextRefreshSteps.setEnabled(False)
        self.ui.spinBoxTextRefreshSteps.setToolTip(dep_msg)
        self.ui.radioButtonRefreshContinuouslyText.setText("Continuously")

        if config.device_cfg.text_refresh == "continuously":
            self.ui.radioButtonRefreshContinuouslyText.setChecked(True)
        else:
            self.ui.radioButtonRefreshNoneText.setChecked(True)

        self.ui.spinBoxTextRefreshSteps.setValue(int(config.device_cfg.text_refresh_value))

        self.ui.spinBoxTimeDelay.setValue(int(config.device_cfg.step_time_delay))

        if config.device_cfg.device_params.strip():
            self.ui.lineEditDeviceParameters.setText(config.device_cfg.device_params.strip())
        else:
            self.reset_device_params()

        # Setup parameter grid
        self.setup_grid_table()
        self.load_grid_from_config()
        # Block signals while setting initial radio button state to avoid redundant toggle_grid_mode calls
        self.ui.radioButtonMultipleParams.blockSignals(True)
        self.ui.radioButtonSingleParam.blockSignals(True)
        self.ui.radioButtonMultipleParams.setChecked(config.device_cfg.use_parameter_grid)
        self.ui.radioButtonSingleParam.setChecked(not config.device_cfg.use_parameter_grid)
        self.ui.radioButtonMultipleParams.blockSignals(False)
        self.ui.radioButtonSingleParam.blockSignals(False)
        # Now explicitly set grid_mode to match config
        self.toggle_grid_mode(config.device_cfg.use_parameter_grid)

    def reset_device_params(self):
        self.ui.lineEditDeviceParameters.setText(self.default_device_params)
        config.device_cfg.device_params = self.default_device_params

    def delete_device_data(self):
        if not isinstance(self.data_delete_func, Callable):
            QMessageBox.information(
                self,
                "Notice",
                "The current device does not appear to provide a"
                " function called delete_data_file() which is"
                " required to allow EPICpy to delete its current datafile.",
            )
        else:
            ret = QMessageBox.question(
                self,
                "Confirm Action",
                "Really DELETE the current data file?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )

            if ret == QMessageBox.StandardButton.Yes:
                self.data_delete_func()
                if isinstance(self.data_info_func, Callable):
                    self.ui.dataInfoLabel.setText(self.data_info_func())

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True

        # ======= essential stuff

        if self.ui.radioButtonRunForSecs.isChecked():
            config.device_cfg.run_command = "run_for"
            config.device_cfg.run_command_value = self.ui.spinBoxRunRealSecs.value()
        elif self.ui.radioButtonRunUntilSim.isChecked():
            config.device_cfg.run_command = "run_until"
            config.device_cfg.run_command_value = self.ui.spinBoxRunSimMsecs.value()
        elif self.ui.radioButtonRunForCycles.isChecked():
            config.device_cfg.run_command = "run_for_cycles"
            config.device_cfg.run_command_value = self.ui.spinBoxRunSimCycles.value()
        else:
            config.device_cfg.run_command = "run_until_done"
            config.device_cfg.run_command_value = 1

        if self.ui.radioButtonRefreshEachCycle.isChecked():
            config.device_cfg.display_refresh = "after_each_step"
            config.device_cfg.display_refresh_value = self.ui.spinBoxRefreshSteps.value()
            config.device_cfg.setting_refresh_steps = self.ui.spinBoxRefreshSteps.value()
        elif self.ui.radioButtonRefreshEachSecs.isChecked():
            config.device_cfg.display_refresh = "after_every_sec"
            config.device_cfg.display_refresh_value = self.ui.doubleSpinBoxRefreshSecs.value()
            config.device_cfg.setting_refresh_secs = self.ui.doubleSpinBoxRefreshSecs.value()
        else:
            config.device_cfg.display_refresh = "none_during_run"
            config.device_cfg.display_refresh_value = 1

        if self.ui.radioButtonRefreshContinuouslyText.isChecked():
            config.device_cfg.text_refresh = "continuously"
        else:
            config.device_cfg.text_refresh = "none_during_run"

        config.device_cfg.text_refresh_value = self.ui.spinBoxTextRefreshSteps.value()

        config.device_cfg.step_time_delay = self.ui.spinBoxTimeDelay.value()

        # ====== helpful stuff

        config.device_cfg.setting_run_for_real_secs = self.ui.spinBoxRunRealSecs.value()
        config.device_cfg.setting_run_until_msecs = self.ui.spinBoxRunSimMsecs.value()
        config.device_cfg.setting_run_cycles = self.ui.spinBoxRunSimCycles.value()
        config.device_cfg.setting_refresh_secs = self.ui.doubleSpinBoxRefreshSecs.value()
        config.device_cfg.setting_refresh_steps = self.ui.spinBoxRefreshSteps.value()

        # Save parameter grid state
        if self.grid_mode:
            self.save_grid_to_config()
        else:
            config.device_cfg.device_params = self.ui.lineEditDeviceParameters.text()
            config.device_cfg.use_parameter_grid = False

        self.hide()

    def clicked_continuous_button(self):
        self.ui.radioButtonRunUntilDone.setChecked(True)
        self.ui.radioButtonRefreshNone.setChecked(True)
        self.ui.radioButtonRefreshNoneText.setChecked(True)
        self.ui.spinBoxTimeDelay.setValue(0)

    # =========================================================================
    # Parameter Grid Methods
    # =========================================================================

    def toggle_grid_mode(self, enabled: bool):
        """Toggle between single parameter string mode and grid mode."""
        self.grid_mode = enabled

        # Toggle single param field
        self.ui.lineEditDeviceParameters.setEnabled(not enabled)
        self.ui.pushButtonClearParams.setEnabled(not enabled)

        # Toggle grid controls
        self.ui.pushButtonAddRow.setEnabled(enabled)
        self.ui.pushButtonDeleteRow.setEnabled(enabled)
        self.ui.pushButtonClearGrid.setEnabled(enabled)
        self.ui.tableWidgetParameterGrid.setEnabled(enabled)

        # Move focus to the active input
        if enabled:
            self.ui.tableWidgetParameterGrid.setFocus()
        else:
            self.ui.lineEditDeviceParameters.setFocus()

    def setup_grid_table(self):
        """Initialize the parameter grid table."""
        table = self.ui.tableWidgetParameterGrid
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Rule", "Parameter String", "Enabled"])

        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Rule
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Parameter String
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Enabled
        table.setColumnWidth(0, 180)
        table.setColumnWidth(2, 85)

    def load_grid_from_config(self):
        """Load parameter grid from device config."""
        self.parameter_grid = [
            ParameterGridItem.from_dict(item) for item in config.device_cfg.parameter_grid
        ]
        self.refresh_grid_table()

    def save_grid_to_config(self):
        """Save parameter grid to device config."""
        config.device_cfg.use_parameter_grid = self.grid_mode
        config.device_cfg.parameter_grid = [item.to_dict() for item in self.parameter_grid]

    def refresh_grid_table(self):
        """Refresh table display from internal data model."""
        table = self.ui.tableWidgetParameterGrid
        table.blockSignals(True)
        table.setRowCount(len(self.parameter_grid))

        for row, item in enumerate(self.parameter_grid):
            # Rule column - show just filename stub (no path, no .prs extension)
            if item.rule_file == "*":
                rule_display = "*"
            else:
                rule_display = Path(item.rule_file).stem

            rule_item = QTableWidgetItem(rule_display)
            rule_item.setData(Qt.ItemDataRole.UserRole, item.rule_file)  # Store full path
            rule_item.setFlags(rule_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Not directly editable
            table.setItem(row, 0, rule_item)

            # Parameter String column - editable
            param_item = QTableWidgetItem(item.parameter_string)
            table.setItem(row, 1, param_item)

            # Enabled column - checkbox widget
            enabled_widget = QCheckBox()
            enabled_widget.setChecked(item.enabled)
            enabled_widget.setStyleSheet("margin-left: 20px;")  # Center the checkbox a bit
            enabled_widget.stateChanged.connect(lambda state, r=row: self.on_enabled_changed(r, state))
            table.setCellWidget(row, 2, enabled_widget)

        table.blockSignals(False)

    def add_grid_row(self):
        """Add a new row to the parameter grid."""
        new_item = ParameterGridItem(
            rule_file="*",
            parameter_string=self.default_device_params,
            enabled=True,
        )
        self.parameter_grid.append(new_item)
        self.refresh_grid_table()

        # Select the new row
        self.ui.tableWidgetParameterGrid.selectRow(len(self.parameter_grid) - 1)

    def delete_selected_rows(self):
        """Delete selected rows from the parameter grid."""
        selected_rows = set(
            item.row() for item in self.ui.tableWidgetParameterGrid.selectedItems()
        )
        if not selected_rows:
            return

        # Delete in reverse order to maintain indices
        for row in sorted(selected_rows, reverse=True):
            if row < len(self.parameter_grid):
                del self.parameter_grid[row]

        self.refresh_grid_table()

    def clear_grid(self):
        """Clear all rows from the parameter grid."""
        if self.parameter_grid:
            ret = QMessageBox.question(
                self,
                "Confirm Clear",
                "Remove all rows from the parameter grid?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            if ret == QMessageBox.StandardButton.Yes:
                self.parameter_grid.clear()
                self.refresh_grid_table()

    def on_cell_double_clicked(self, row: int, column: int):
        """Handle double-click on grid cells."""
        if column == 0:  # Rule column
            self.select_rule_file(row)

    def select_rule_file(self, row: int):
        """Open file dialog to select a rule file for the given row."""
        # Start in device folder
        if config.device_cfg.device_file:
            start_dir = Path(config.device_cfg.device_file).parent
        else:
            start_dir = Path.home()

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Rule File (Cancel for 'Current Rule')",
            str(start_dir),
            "Rule Files (*.prs)",
        )

        if file_path:
            self.parameter_grid[row].rule_file = file_path
        else:
            # User cancelled - set to "*" (current rule)
            self.parameter_grid[row].rule_file = "*"

        self.refresh_grid_table()

    def on_grid_item_changed(self, item: QTableWidgetItem):
        """Handle changes to grid items (parameter string editing)."""
        row = item.row()
        column = item.column()

        if column == 1 and row < len(self.parameter_grid):  # Parameter String
            self.parameter_grid[row].parameter_string = item.text()

    def on_enabled_changed(self, row: int, state: int):
        """Handle enabled checkbox state changes."""
        if row < len(self.parameter_grid):
            self.parameter_grid[row].enabled = bool(state)
