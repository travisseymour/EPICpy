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

import config
from uifiles.searchui import Ui_DialogSearch
from PySide2.QtWidgets import QDialog
from PySide2.QtCore import Qt


class SearchWin(QDialog):
    def __init__(self):
        super(SearchWin, self).__init__()
        self.ok = False
        self.ui = Ui_DialogSearch()
        self.ui.setupUi(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonSearch.clicked.connect(self.clicked_ok_button)

        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )

        if "searchwindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["searchwindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        self.setLayout(self.ui.verticalLayout_2)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["searchwindow"] = [self.width(), self.height()]
        config.save_app_config(quiet=True)
        super(SearchWin, self).resizeEvent(event)

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clicked_cancel_button()
        elif event.key() == Qt.Key_Enter:
            self.clicked_ok_button()
