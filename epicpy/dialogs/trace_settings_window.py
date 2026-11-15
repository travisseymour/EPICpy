# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from PySide6.QtWidgets import QDialog

from epicpy.uifiles.trace_settings_ui import Ui_DialogTraceSettings
from epicpy.utils import config
from epicpy.utils.app_utils import clear_font


class TraceSettingsWin(QDialog):
    def __init__(self):
        super(TraceSettingsWin, self).__init__()
        self.ok = False
        self.ui = Ui_DialogTraceSettings()
        self.ui.setupUi(self)

        # replace designed font with application-wide font
        clear_font(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)

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
