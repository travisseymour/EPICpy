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
import re

from PyQt5.QtCore import Qt, QRegExp

from dialogs.searchwindow import SearchWin
from stateconstants import RUNNING
from uifiles.traceui import Ui_TraceWindow
from PyQt5.QtGui import QCloseEvent, QFont, QTextCursor, QTextDocument
from PyQt5.QtWidgets import QMainWindow, QMenu
import datetime
import config


class TraceWin(QMainWindow):
    def __init__(self, context, parent):
        super(TraceWin, self).__init__()
        self._parent = parent
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

        # stuff needed for search

        self.search_pattern = ""
        self.search_using_regex = False
        self.search_ignore_case = False

        self.search_dialog = SearchWin()
        self.search_dialog.setModal(True)

        self.ui.plainTextEditOutput.customContextMenuRequested.connect(
            self.search_context_menu
        )

    # =============================================
    # Context Menu Behavior
    # =============================================

    def search_context_menu(self, event):
        contextMenu = QMenu(self)

        if hasattr(self._parent, 'run_state') and self._parent.run_state == RUNNING:
            return

        searchAction = contextMenu.addAction("Search")
        selectAllAction = contextMenu.addAction("Select All")

        contextMenu.addSeparator()
        if self.ui.plainTextEditOutput.copyAvailable and len(
            self.ui.plainTextEditOutput.toPlainText()
        ):
            copyAction = contextMenu.addAction("Copy")
        else:
            copyAction = None
        clearAction = contextMenu.addAction("Clear")

        contextMenu.addSeparator()


        action = contextMenu.exec_(self.mapToGlobal(event))

        if action is None:
            ...
        elif action == clearAction:
            self.clear()
        elif action == searchAction:
            self.query_search()
        elif action == selectAllAction:
            self.ui.plainTextEditOutput.selectAll()
        elif action == copyAction:
            self.ui.plainTextEditOutput.copy()


    def query_search(self):
        self.search_dialog.ok = False
        self.search_dialog.ui.checkBoxRegEx.setChecked(self.search_using_regex)
        self.search_dialog.ui.checkBoxIgnoreCase.setChecked(self.search_ignore_case)
        self.search_dialog.exec_()

        if self.search_dialog.ok:
            self.search_pattern = (
                self.search_dialog.ui.lineEditSearchText.text().strip()
            )
            self.search_using_regex = self.search_dialog.ui.checkBoxRegEx.isChecked()
            self.search_ignore_case = (
                self.search_dialog.ui.checkBoxIgnoreCase.isChecked()
            )
            self.search_active = True
            self.do_search(backwards=self.search_dialog.backwards)

    # start text cursor utility functions --------
    def get_text_cursor(self):
        return self.ui.plainTextEditOutput.textCursor()

    def set_text_cursor_pos(self, value):
        tc = self.get_text_cursor()
        tc.setPosition(value, QTextCursor.KeepAnchor)
        self.ui.plainTextEditOutput.setTextCursor(tc)

    def get_text_cursor_pos(self):
        return self.get_text_cursor().position()

    def get_text_selection(self):
        cursor = self.get_text_cursor()
        return cursor.selectionStart(), cursor.selectionEnd()

    def set_text_selection(self, start, end):
        cursor = self.get_text_cursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        self.ui.plainTextEditOutput.setTextCursor(cursor)

    # ---------------- end text cursor utility functions

    def do_search(self, backwards: bool = False):
        if not self.search_pattern:
            return

        sensitivity = (
            Qt.CaseInsensitive if self.search_ignore_case else Qt.CaseSensitive
        )
        pattern = (
            self.search_pattern
            if self.search_using_regex
            else re.escape(self.search_pattern)
        )

        regex = QRegExp(pattern, sensitivity)

        text_cursor = self.get_text_cursor()

        if backwards:
            if text_cursor.atStart():
                self.ui.plainTextEditOutput.moveCursor(QTextCursor.End)
            result = self.ui.plainTextEditOutput.find(regex, QTextDocument.FindBackward)
        else:
            if text_cursor.atEnd():
                self.ui.plainTextEditOutput.moveCursor(QTextCursor.Start)
            result = self.ui.plainTextEditOutput.find(regex)

        if result:
            self.ui.plainTextEditOutput.setFocus()

    # ----------------------------------------

    def enable_text_updates(self, enable: bool = True):
        self.ui.plainTextEditOutput.cache_text = not enable

    def write(self, text: str):
        self.ui.plainTextEditOutput.write(text)

    def dump_cache(self):
        return self.ui.plainTextEditOutput.dump_cache()

    def clear(self):
        self.ui.plainTextEditOutput.clear()

    def closeEvent(self, event: QCloseEvent):
        if self.can_close:
            self.hide()
        else:
            QMainWindow.closeEvent(self, event)
