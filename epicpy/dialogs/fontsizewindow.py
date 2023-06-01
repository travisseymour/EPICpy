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

from PySide6.QtCore import QSize
from PySide6.QtGui import QShowEvent

from epicpy.uifiles.fontsizeui import Ui_DialogFontSize
from PySide6.QtWidgets import QDialog
from epicpy.utils import config


class FontSizeDialog(QDialog):
    def __init__(self):
        super(FontSizeDialog, self).__init__()
        self.ok = False
        self.ui = Ui_DialogFontSize()
        self.ui.setupUi(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)
        self.ui.spinBoxFontSize.valueChanged.connect(self.font_size_changed)

        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )

        if "fontsizewindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["fontsizewindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        # self.setLayout(self.ui.verticalLayout)

    def font_size_changed(self, change: int):
        self.setup_options(update_spin_box=False)

    def showEvent(self, event: QShowEvent) -> None:
        self.setup_options()
        super(FontSizeDialog, self).showEvent(event)

    def resizeEvent(self, event: QSize):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["fontsizewindow"] = [self.width(), self.height()]
        super(FontSizeDialog, self).resizeEvent(event)

    def setup_options(self, update_spin_box: bool = True):
        if update_spin_box:
            # usually called when dialog opened (pulls size from config)
            self.ui.spinBoxFontSize.setValue(int(config.app_cfg.font_size))
            self.ui.plainTextEditFontSample.setStyleSheet(
                'QWidget {font: "'
                + config.app_cfg.font_name
                + '"; font-size: '
                + str(int(config.app_cfg.font_size))
                + "pt}"
            )
        else:
            # usually called when spinbox changes (pulls size from widget)
            self.ui.plainTextEditFontSample.setStyleSheet(
                'QWidget {font: "'
                + config.app_cfg.font_name
                + '"; font-size: '
                + str(int(self.ui.spinBoxFontSize.value()))
                + "pt}"
            )

        self.ui.plainTextEditFontSample.update()

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True
        config.app_cfg.font_size = self.ui.spinBoxFontSize.value()
        self.hide()
