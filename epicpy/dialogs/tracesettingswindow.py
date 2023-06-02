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

from epicpy.uifiles.tracesettingsui import Ui_DialogTraceSettings
from qtpy.QtWidgets import QDialog
from epicpy.utils import config


class TraceSettingsWin(QDialog):
    def __init__(self):
        super(TraceSettingsWin, self).__init__()
        self.ok = False
        self.ui = Ui_DialogTraceSettings()
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

        if "tracesettingswindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["tracesettingswindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        # self.setLayout(self.ui.verticalLayout)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["tracesettingswindow"] = [
            self.width(),
            self.height(),
        ]
        super(TraceSettingsWin, self).resizeEvent(event)

    def setup_options(self):
        self.ui.checkBoxVocal.setChecked(config.device_cfg.trace_vocal)
        self.ui.checkBoxDevice.setChecked(config.device_cfg.trace_device)
        self.ui.checkBoxManual.setChecked(config.device_cfg.trace_manual)
        self.ui.checkBoxOcular.setChecked(config.device_cfg.trace_ocular)
        self.ui.checkBoxVisual.setChecked(config.device_cfg.trace_visual)
        self.ui.checkBoxAuditory.setChecked(config.device_cfg.trace_auditory)
        self.ui.checkBoxCognitive.setChecked(config.device_cfg.trace_cognitive)
        self.ui.checkBoxTemporal.setChecked(config.device_cfg.trace_temporal)

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True
        config.device_cfg.trace_vocal = self.ui.checkBoxVocal.isChecked()
        config.device_cfg.trace_device = self.ui.checkBoxDevice.isChecked()
        config.device_cfg.trace_manual = self.ui.checkBoxManual.isChecked()
        config.device_cfg.trace_ocular = self.ui.checkBoxOcular.isChecked()
        config.device_cfg.trace_visual = self.ui.checkBoxVisual.isChecked()
        config.device_cfg.trace_auditory = self.ui.checkBoxAuditory.isChecked()
        config.device_cfg.trace_cognitive = self.ui.checkBoxCognitive.isChecked()
        config.device_cfg.trace_temporal = self.ui.checkBoxTemporal.isChecked()
        self.hide()
