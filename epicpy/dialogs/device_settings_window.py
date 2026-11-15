# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QListWidgetItem

from epicpy.uifiles.device_settings_ui import Ui_DialogDeviceOptions
from epicpy.utils import config
from epicpy.utils.app_utils import clear_font


class DeviceOptionsWin(QDialog):
    def __init__(self, device):
        super(DeviceOptionsWin, self).__init__()
        self.device = device
        self.ui = Ui_DialogDeviceOptions()
        self.ui.setupUi(self)

        clear_font(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)

        if "deviceoptionswindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["deviceoptionswindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        # self.setLayout(self.ui.verticalLayout)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["deviceoptionswindow"] = [
            self.width(),
            self.height(),
        ]
        super(DeviceOptionsWin, self).resizeEvent(event)

    def setup_options(self):
        if not self.device:
            self.ui.labelDeviceNameAndInfo.setText("No device appears to be loaded!")
        elif not hasattr(self.device, "option") or not isinstance(self.device.option, dict) or not len(self.device.option.keys()):
            msg = f"Device {self.device.device_name} does not expose any user adjustable options."
            self.ui.labelDeviceNameAndInfo.setText(msg)
        else:
            msg = f"Device {self.device.device_name} User Options:"
            self.ui.labelDeviceNameAndInfo.setText(msg)
            font = QApplication.instance().font()
            for option_name in self.device.option:
                item = QListWidgetItem(self.ui.listWidgetOptions)
                item.setFont(font)
                cb = QCheckBox(option_name)
                cb.setFont(font)
                cb.setChecked(self.device.option[option_name])
                self.ui.listWidgetOptions.setItemWidget(item, cb)

    def clicked_cancel_button(self):
        """
        Close instead of hide so there are never any stale references to previous devices.
        """
        self.close()

    def clicked_ok_button(self):
        states = [
            self.ui.listWidgetOptions.itemWidget(self.ui.listWidgetOptions.item(index)).checkState()
            for index in range(self.ui.listWidgetOptions.count())
        ]
        if states:
            option_states = list(zip(self.device.option.keys(), states))
            for rule_name, state in option_states:
                self.device.option[rule_name] = bool(state)
        self.close()
