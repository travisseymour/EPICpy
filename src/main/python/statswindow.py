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

from datetime import datetime
from functools import partial

from PyQt5.QtCore import QTimer

from uifiles.statsui import Ui_StatsWindow
from PyQt5.QtGui import QCloseEvent, QFont
from PyQt5.QtWidgets import QMainWindow
import config


class StatsWin(QMainWindow):
    def __init__(self, context, parent):
        super(StatsWin, self).__init__()

        self.context = context
        self.view_type = b"StatsOut"
        self.setObjectName("StatsWindow")
        self.ui = Ui_StatsWindow()
        self.ui.setupUi(self)
        self.setCentralWidget(self.ui.statsTextBrowser)
        self.can_close = False

        now = datetime.now().strftime("%r")
        self.ui.statsTextBrowser.append(f"{f'Stats Out! ({now})'}")

        self.trace_out_view = None

        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )
        self.ui.statsTextBrowser.setFont(
            QFont(config.app_cfg.font_name, int(config.app_cfg.font_size))
        )

        self.ui.statsTextBrowser.mouseDoubleClickEvent = parent.mouseDoubleClickEvent

    def write(self, text: str):
        QTimer.singleShot(200, partial(self.ui.statsTextBrowser.append, text))

    def clear(self):
        QTimer.singleShot(200, self.ui.statsTextBrowser.clear)

    def closeEvent(self, event: QCloseEvent):
        if self.can_close:
            self.hide()
        else:
            QMainWindow.closeEvent(self, event)
