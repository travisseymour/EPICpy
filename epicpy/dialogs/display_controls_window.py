# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from PySide6.QtWidgets import QDialog

from epicpy.uifiles.display_controls_ui import Ui_DialogDisplayControls
from epicpy.utils import config
from epicpy.utils.app_utils import clear_font


class DisplayControlsWin(QDialog):
    def __init__(self):
        super(DisplayControlsWin, self).__init__()
        self.ok = False
        self.ui = Ui_DialogDisplayControls()
        self.ui.setupUi(self)

        clear_font(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)

        if "displaycontrolswindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["displaycontrolswindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        # self.setLayout(self.ui.verticalLayout_3)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["displaycontrolswindow"] = [
            self.width(),
            self.height(),
        ]
        super(DisplayControlsWin, self).resizeEvent(event)

    def setup_options(self):
        self.ui.checkBoxPPSMemoryContents.setChecked(config.device_cfg.output_run_memory_contents)
        self.ui.checkBoxPPSRunMessages.setChecked(config.device_cfg.output_run_messages)
        self.ui.checkBoxPPSCompilerMessages.setChecked(config.device_cfg.output_compiler_messages)
        self.ui.checkBoxCompilerDetails.setChecked(config.device_cfg.output_compiler_details)
        self.ui.checkBoxRunDetails.setChecked(config.device_cfg.output_run_details)
        self.ui.checkBoxCalibrationGrid.setChecked(config.device_cfg.calibration_grid)
        self.ui.checkBoxCenterDot.setChecked(config.device_cfg.center_dot)
        self.ui.spinBoxSpatialScale.setValue(config.device_cfg.spatial_scale_degree)
        self.ui.checkBoxAllowDeviceImages.setChecked(config.device_cfg.allow_device_images)
        self.ui.checkBoxShowModelParameters.setChecked(config.device_cfg.describe_parameters)
        self.ui.checkBoxShowFullTraceback.setChecked(config.app_cfg.show_full_error_trace)

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True
        config.device_cfg.output_run_memory_contents = self.ui.checkBoxPPSMemoryContents.isChecked()
        config.device_cfg.output_run_messages = self.ui.checkBoxPPSRunMessages.isChecked()
        config.device_cfg.output_compiler_messages = self.ui.checkBoxPPSCompilerMessages.isChecked()
        config.device_cfg.output_compiler_details = self.ui.checkBoxCompilerDetails.isChecked()
        config.device_cfg.output_run_details = self.ui.checkBoxRunDetails.isChecked()
        config.device_cfg.calibration_grid = self.ui.checkBoxCalibrationGrid.isChecked()
        config.device_cfg.center_dot = self.ui.checkBoxCenterDot.isChecked()
        config.device_cfg.spatial_scale_degree = self.ui.spinBoxSpatialScale.value()
        config.device_cfg.allow_device_images = self.ui.checkBoxAllowDeviceImages.isChecked()
        config.device_cfg.describe_parameters = self.ui.checkBoxShowModelParameters.isChecked()
        config.app_cfg.show_full_error_trace = self.ui.checkBoxShowFullTraceback.isChecked()

        self.hide()
