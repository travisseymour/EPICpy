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

from epicpy.utils import config
from epicpy.uifiles.devicesettingsui import Ui_DialogDeviceOptions
from qtpy.QtWidgets import QDialog, QCheckBox, QListWidgetItem


class DeviceOptionsWin(QDialog):
    def __init__(self, device):
        super(DeviceOptionsWin, self).__init__()
        self.device = device
        self.ui = Ui_DialogDeviceOptions()
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
        elif (
            not hasattr(self.device, "option")
            or not isinstance(self.device.option, dict)
            or not len(self.device.option.keys())
        ):
            msg = (
                f"Device {self.device.device_name} does not expose any user "
                f"adjustable options."
            )
            self.ui.labelDeviceNameAndInfo.setText(msg)
        else:
            msg = f"Device {self.device.device_name} User Options:"
            self.ui.labelDeviceNameAndInfo.setText(msg)
            for option_name in self.device.option:
                item = QListWidgetItem(self.ui.listWidgetOptions)
                cb = QCheckBox(option_name)
                cb.setChecked(self.device.option[option_name])
                self.ui.listWidgetOptions.setItemWidget(item, cb)

    def clicked_cancel_button(self):
        """
        Close instead of hide so there are never any stale references to previous devices.
        """
        self.close()

    def clicked_ok_button(self):
        states = [
            self.ui.listWidgetOptions.itemWidget(
                self.ui.listWidgetOptions.item(index)
            ).checkState()
            for index in range(self.ui.listWidgetOptions.count())
        ]
        if states:
            option_states = list(zip(self.device.option.keys(), states))
            for rule_name, state in option_states:
                self.device.option[rule_name] = bool(state)
        self.close()
