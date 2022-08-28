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

from uifiles.displaycontrolsui import Ui_DialogDisplayControls
from PyQt5.QtWidgets import QDialog
import config


class DisplayControlsWin(QDialog):
    def __init__(self, context):
        super(DisplayControlsWin, self).__init__()
        self.context = context
        self.ok = False
        self.ui = Ui_DialogDisplayControls()
        self.ui.setupUi(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)

        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )

        if "displaycontrolswindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["displaycontrolswindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        self.setLayout(self.ui.verticalLayout_3)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["displaycontrolswindow"] = [
            self.width(),
            self.height(),
        ]
        config.save_app_config(quiet=True)
        super(DisplayControlsWin, self).resizeEvent(event)

    def setup_options(self):
        self.ui.checkBoxPPSMemoryContents.setChecked(
            config.device_cfg.output_run_memory_contents
        )
        self.ui.checkBoxPPSRunMessages.setChecked(config.device_cfg.output_run_messages)
        self.ui.checkBoxPPSCompilerMessages.setChecked(
            config.device_cfg.output_compiler_messages
        )
        self.ui.checkBoxCompilerDetails.setChecked(
            config.device_cfg.output_compiler_details
        )
        self.ui.checkBoxRunDetails.setChecked(config.device_cfg.output_run_details)
        self.ui.checkBoxCalibrationGrid.setChecked(config.device_cfg.calibration_grid)
        self.ui.checkBoxCenterDot.setChecked(config.device_cfg.center_dot)
        self.ui.spinBoxSpatialScale.setValue(config.device_cfg.spatial_scale_degree)
        self.ui.checkBoxAllowDeviceImages.setChecked(
            config.device_cfg.allow_device_images
        )
        self.ui.checkBoxShowModelParameters.setChecked(
            config.device_cfg.describe_parameters
        )

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True
        config.device_cfg.output_run_memory_contents = (
            self.ui.checkBoxPPSMemoryContents.isChecked()
        )
        config.device_cfg.output_run_messages = (
            self.ui.checkBoxPPSRunMessages.isChecked()
        )
        config.device_cfg.output_compiler_messages = (
            self.ui.checkBoxPPSCompilerMessages.isChecked()
        )
        config.device_cfg.output_compiler_details = (
            self.ui.checkBoxCompilerDetails.isChecked()
        )
        config.device_cfg.output_run_details = self.ui.checkBoxRunDetails.isChecked()
        config.device_cfg.calibration_grid = self.ui.checkBoxCalibrationGrid.isChecked()
        config.device_cfg.center_dot = self.ui.checkBoxCenterDot.isChecked()
        config.device_cfg.spatial_scale_degree = self.ui.spinBoxSpatialScale.value()
        config.device_cfg.allow_device_images = (
            self.ui.checkBoxAllowDeviceImages.isChecked()
        )
        config.device_cfg.describe_parameters = (
            self.ui.checkBoxShowModelParameters.isChecked()
        )
        self.hide()
