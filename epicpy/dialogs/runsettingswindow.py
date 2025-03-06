"""
This file is part of the EPICpy source code. EPICpy is a tool for simulating
human performance tasks using the EPIC computational cognitive architecture
(David Kieras and David Meyer 1997a) using the Python programming language.
Copyright (C) 2022 Travis L. Seymour, PhD

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

from qtpy.QtWidgets import QDialog, QButtonGroup, QMessageBox
from qtpy.QtGui import QShowEvent

from typing import Callable

from epicpy.uifiles.runsettingsui import Ui_DialogRunSettings
from epicpy.utils import config
from epicpy.utils.apputils import clear_font


class RunSettingsWin(QDialog):
    def __init__(
        self,
        default_device_params: str,
        data_delete_func: Callable = None,
        data_info_func: Callable = None,
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

        self.ui.pushButtonResetParams.clicked.connect(self.reset_device_params)

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
        else:
            self.ui.radioButtonRefreshNone.setChecked(True)

        # FIXME: Do this stuff in the ui file instead of here.
        # ------------------------------------------------------------------
        dep_msg = "This option is depreciated and will be removed shortly."
        self.ui.radioButtonRefreshEachCycleText.setEnabled(False)
        self.ui.radioButtonRefreshEachCycleText.setToolTip(dep_msg)
        self.ui.spinBoxTextRefreshSteps.setEnabled(False)
        self.ui.spinBoxTextRefreshSteps.setToolTip(dep_msg)

        self.ui.radioButtonRefreshEachSecs.setToolTip(dep_msg)
        self.ui.doubleSpinBoxRefreshSecs.setToolTip(dep_msg)
        self.ui.radioButtonRefreshContinuouslyText.setText("Continuously")
        # ------------------------------------------------------------------

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
            config.device_cfg.display_refresh_value = 1
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

        self.hide()

    def clicked_continuous_button(self):
        self.ui.radioButtonRunUntilDone.setChecked(True)
        self.ui.radioButtonRefreshNone.setChecked(True)
        self.ui.radioButtonRefreshNoneText.setChecked(True)
        self.ui.spinBoxTimeDelay.setValue(0)
