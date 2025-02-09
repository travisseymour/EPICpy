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

from functools import partial

from qtpy.QtCore import QSize

from epicpy.utils import config
from epicpy.uifiles.searchui import Ui_DialogSearch
from qtpy.QtWidgets import QDialog
from qtpy.QtCore import Qt

from epicpy.utils.apputils import clear_font


class SearchWin(QDialog):
    def __init__(self, *args, **kwargs):
        super(SearchWin, self).__init__(*args, **kwargs)
        self.ok = False
        self.ui = Ui_DialogSearch()
        self.ui.setupUi(self)

        # replace designed font with application-wide font
        clear_font(self)

        self.backwards: bool = False

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonSearchForward.clicked.connect(self.clicked_ok_button)
        self.ui.pushButtonSearchBackward.clicked.connect(partial(self.clicked_ok_button, backwards=True))
        self.ui.lineEditSearchText.editingFinished.connect(self.clicked_ok_button)

        if hasattr(config.app_cfg, "dialog_size") and "searchwindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["searchwindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(QSize(w, h))

        # self.setLayout(self.ui.verticalLayout_2)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        if hasattr(config.app_cfg, "searchwindow"):
            config.app_cfg.dialog_size["searchwindow"] = [self.width(), self.height()]
        super(SearchWin, self).resizeEvent(event)

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self, backwards: bool = False):
        self.backwards = backwards
        self.ok = True
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.clicked_cancel_button()
        elif event.key() == Qt.Key.Key_Enter:
            self.clicked_ok_button()
