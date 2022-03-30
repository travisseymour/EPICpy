"""
This file is part of EPICpy, Created by Travis L. Seymour, PhD.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar.
If not, see <https://www.gnu.org/licenses/>.
"""

from PySide2.QtCore import QSize
from PySide2.QtGui import QShowEvent, QFont

from uifiles.fontsizeui import Ui_DialogFontSize
from PySide2.QtWidgets import QDialog
import config


class FontSizeDialog(QDialog):
    def __init__(self, context):
        super(FontSizeDialog, self).__init__()
        self.context = context
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

        self.setLayout(self.ui.verticalLayout)

    def font_size_changed(self, change: int):
        self.setup_options(update_spin_box=False)

    def showEvent(self, event: QShowEvent) -> None:
        self.setup_options()
        super(FontSizeDialog, self).showEvent(event)

    def resizeEvent(self, event: QSize):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["fontsizewindow"] = [self.width(), self.height()]
        config.save_app_config(quiet=True)
        super(FontSizeDialog, self).resizeEvent(event)

    def setup_options(self, update_spin_box: bool = True):
        self.ui.plainTextEditFontSample.setFont(
            QFont(config.app_cfg.font_name, int(config.app_cfg.font_size))
        )
        if update_spin_box:
            self.ui.spinBoxFontSize.setValue(int(config.app_cfg.font_size))

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True
        config.app_cfg.font_size = self.ui.spinBoxFontSize.value()
        self.hide()
