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

from uifiles.traceui import Ui_TraceWindow
from PySide2.QtGui import QCloseEvent, QFont
from PySide2.QtWidgets import QMainWindow
import datetime
import config


class TraceWin(QMainWindow):
    def __init__(self, context, parent):
        super(TraceWin, self).__init__()
        self.context = context
        self.view_type = b"TraceOut"
        self.setObjectName("TraceWindow")
        self.ui = Ui_TraceWindow()
        self.ui.setupUi(self)
        self.setCentralWidget(self.ui.plainTextEditOutput)
        self.can_close = False

        self.ui.plainTextEditOutput.setPlainText(
            f'Trace Out! ({datetime.datetime.now().strftime("%r")})\n'
        )

        self.trace_out_view = None

        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )
        self.ui.plainTextEditOutput.setFont(
            QFont(config.app_cfg.font_name, int(config.app_cfg.font_size))
        )

        self.ui.plainTextEditOutput.mouseDoubleClickEvent = parent.mouseDoubleClickEvent

    def enable_text_updates(self, enable: bool = True):
        self.ui.plainTextEditOutput.cache_text = not enable

    def write(self, text: str, copy_to_trace: bool = False):
        if text.strip():
            self.ui.plainTextEditOutput.write(text)
            if copy_to_trace:
                self.trace_win.ui.plainTextEditOutput.write(text)

    def dump_cache(self):
        return self.ui.plainTextEditOutput.dump_cache()

    def clear(self):
        self.ui.plainTextEditOutput.clear()

    def closeEvent(self, event: QCloseEvent):
        if self.can_close:
            self.hide()
        else:
            QMainWindow.closeEvent(self, event)
