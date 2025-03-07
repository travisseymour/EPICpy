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

from qtpy.QtCore import Qt

from epicpy.dialogs.searchwindow import SearchWin
from epicpy.constants.stateconstants import RUNNING
from epicpy.uifiles.traceui import Ui_TraceWindow
from qtpy.QtGui import (
    QCloseEvent,
    QFont,
    QShowEvent,
    QHideEvent,
)
from qtpy.QtWidgets import QMainWindow, QMenu
import datetime
from epicpy.utils import config
from epicpy.utils.apputils import clear_font
from epicpy.widgets.largetextview import LargeTextView


class Ui_TraceWindowCustom(Ui_TraceWindow):
    """
    This is so that we can add the LargeTextView and still
    have PyCharm do proper lookups where it understands that
    self.ui.plainTextEditOutput is a LargeTextView object
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plainTextEditOutput: LargeTextView = LargeTextView()


class TraceWin(QMainWindow):
    def __init__(self, parent):
        super(TraceWin, self).__init__(parent)
        self._parent = parent
        self.view_type = b"TraceOut"
        self.setObjectName("TraceWindow")
        self.ui = Ui_TraceWindowCustom()
        self.ui.setupUi(self)

        # replace designed font with application-wide font
        clear_font(self)

        self.ui.plainTextEditOutput = LargeTextView(enable_context_menu=False)
        self.setCentralWidget(self.ui.plainTextEditOutput)
        self.can_close: bool = False

        self.ui.plainTextEditOutput.setPlainText(f'Trace Out! ({datetime.datetime.now().strftime("%r")})\n')

        self.trace_out_view = None

        self.ui.plainTextEditOutput.mouseDoubleClickEvent = parent.mouseDoubleClickEvent

        # stuff needed for search

        self.search_pattern = ""
        self.search_using_regex = False
        self.search_ignore_case = False

        self.search_dialog = SearchWin()
        self.search_dialog.setModal(True)

        self.ui.plainTextEditOutput.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.plainTextEditOutput.customContextMenuRequested.connect(self.search_context_menu)

        # connect self.write directly to widget's write!
        self.write = self.ui.plainTextEditOutput.write

    # =============================================
    # Context Menu Behavior
    # =============================================

    def search_context_menu(self, event):
        contextMenu = QMenu(self)

        if hasattr(self._parent, "simulation") and self._parent.run_state == RUNNING:
            return

        searchAction = contextMenu.addAction("Search")
        clearAction = contextMenu.addAction("Clear")
        # contextMenu.addSeparator()
        # selectAllAction = contextMenu.addAction("Select All")
        copyAction = contextMenu.addAction("Copy")
        copyAction.setText(f"Copy All Lines)")
        # contextMenu.addSeparator()

        action = contextMenu.exec(self.mapToGlobal(event))

        if action is None:
            ...
        elif action == clearAction:
            self.ui.plainTextEditOutput.flush()
        elif action == searchAction:
            self.ui.plainTextEditOutput.query_search()
        # elif action == selectAllAction:
        #     self.ui.plainTextEditOutput.selectAll()
        elif action == copyAction:
            self.ui.plainTextEditOutput.copy_all_to_clipboard()

    # ----------------------------------------

    def enable_output_updating(self):
        # FIXME: check what these were for and see if we need to add some functionality back somewhere??
        #        Mar 4 2025 - tls
        # self.ui.plainTextEditOutput.set_updating(True)
        return

    def disable_output_updating(self):
        # self.ui.plainTextEditOutput.set_updating(False)
        return

    def write(self, text: str):
        self.ui.plainTextEditOutput.write(text)

    def clear(self):
        self.ui.plainTextEditOutput.flush()

    def hideEvent(self, event: QHideEvent) -> None:
        # self.ui.plainTextEditOutput.set_updating(False)
        QMainWindow.hideEvent(self, event)

    def showEvent(self, event: QShowEvent) -> None:
        # self.ui.plainTextEditOutput.set_updating(True)
        QMainWindow.showEvent(self, event)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.can_close:  # FIXME: Is this backwards...shouldn't can_close lead to a close??
            self.hide()
        else:
            QMainWindow.closeEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F3:
            if not self.ui.plainTextEditOutput.continue_find_text():
                self.ui.plainTextEditOutput.query_search()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key.Key_F and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.ui.plainTextEditOutput.query_search()
        else:
            super().keyPressEvent(event)
