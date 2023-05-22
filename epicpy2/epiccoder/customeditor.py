"""
EPICcoder is a minimal programmer's text editor created for use with the
EPIC, EPICpy and pyEPIC simulation environments.
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
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pathlib import Path
from typing import Callable, Optional

# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
#
# from PyQt5.Qsci import *

import keyword
import pkgutil

from PyQt5.Qsci import QsciScintilla
from PyQt5.Qsci import QsciLexerPython
from PyQt5.Qsci import QsciLexerCPP
from PyQt5.Qsci import QsciAPIs

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QKeyEvent

from epicpy2.epiccoder.lexer import PyCustomLexer, PPSCustomLexer, TextCustomLexer


class CustomEditor(QsciScintilla):
    def __init__(
        self,
        parent=None,
        file_path: Optional[Path] = None,
        star_func: Optional[Callable] = None,
    ):
        super(CustomEditor, self).__init__(parent)

        assert isinstance(file_path, Path)
        assert isinstance(star_func, Callable)

        self.file_path = file_path
        self.star_func = star_func
        self.changed = False

        # encoding
        self.setUtf8(True)
        # Font
        self.window_font = QFont("Fira Code")
        self.window_font.setPointSize(12)
        self.setFont(self.window_font)

        # brace matching
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # indentation
        self.setIndentationGuides(True)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)

        # autocomplete
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        # caret
        self.setCaretForegroundColor(QColor("#dedcdc"))
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        self.setCaretLineBackgroundColor(QColor("#2c313c"))

        # EOL
        self.setEolMode(QsciScintilla.EolWindows)
        self.setEolVisibility(False)

        # lexer for syntax highlighting

        self.color1 = "#abb2bf"
        self.color2 = "#282c34"

        if self.file_path.suffix == ".py":
            self.pylexer = QsciLexerPython(self)

            # Default Settings
            self.pylexer.setDefaultColor(QColor(self.color1))
            self.pylexer.setDefaultPaper(QColor(self.color2))
            self.pylexer.setDefaultFont(QFont("Consolas", 14))

            for i in range(50):
                self.pylexer.setFont(QFont("Consolas", 14), i)

            self.pylexer.setColor(QColor("#4397E0"), QsciLexerPython.Number)
            self.pylexer.setColor(QColor("#F18622"), QsciLexerPython.Keyword)
            self.pylexer.setColor(QColor("#91C71E"), QsciLexerPython.DoubleQuotedString)
            self.pylexer.setColor(QColor("#91C71E"), QsciLexerPython.SingleQuotedString)
            self.pylexer.setColor(
                QColor("#91C71E"), QsciLexerPython.TripleDoubleQuotedString
            )
            self.pylexer.setColor(
                QColor("#91C71E"), QsciLexerPython.TripleSingleQuotedString
            )
            self.pylexer.setColor(QColor("#F0A91D"), QsciLexerPython.FunctionMethodName)
            self.pylexer.setColor(QColor("#8C8C8C"), QsciLexerPython.Comment)
            self.pylexer.setColor(QColor("#8C8C8C"), QsciLexerPython.CommentBlock)
            self.pylexer.setColor(QColor("#B45DD9"), QsciLexerPython.Identifier)

        elif self.file_path.suffix in (".h", ".c", ".cpp", ".hpp"):
            self.pylexer = QsciLexerCPP(self)

            # Default Settings
            self.pylexer.setDefaultColor(QColor(self.color1))
            self.pylexer.setDefaultPaper(QColor(self.color2))
            self.pylexer.setDefaultFont(QFont("Consolas", 14))

            for i in range(50):
                self.pylexer.setFont(QFont("Consolas", 14), i)

            self.pylexer.setColor(QColor("#4397E0"), QsciLexerCPP.Number)
            self.pylexer.setColor(QColor("#F18622"), QsciLexerCPP.Keyword)
            self.pylexer.setColor(QColor("#91C71E"), QsciLexerCPP.DoubleQuotedString)
            self.pylexer.setColor(QColor("#91C71E"), QsciLexerCPP.SingleQuotedString)
            self.pylexer.setColor(QColor("#8C8C8C"), QsciLexerCPP.Comment)
            self.pylexer.setColor(QColor("#8C8C8C"), QsciLexerCPP.CommentLine)
            self.pylexer.setColor(QColor("#B45DD9"), QsciLexerCPP.Identifier)
            self.pylexer.setColor(QColor("white"), QsciLexerCPP.Operator)

        elif self.file_path.suffix == ".prs":
            self.pylexer = PPSCustomLexer(self)
        else:
            self.pylexer = TextCustomLexer(self)

        self.pylexer.setDefaultFont(self.window_font)

        # Api (you can add autocompletion using this)
        self.api = QsciAPIs(self.pylexer)
        for key in keyword.kwlist + dir(
            __builtins__
        ):  # adding builtin functions and keywords
            self.api.add(key)

        for (
            _,
            name,
            _,
        ) in (
            pkgutil.iter_modules()
        ):  # adding all modules names from current interpreter
            self.api.add(name)

        self.api.prepare()

        self.setLexer(self.pylexer)

        # line numbers
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(QColor("#ff888888"))
        self.setMarginsBackgroundColor(QColor("#282c34"))
        self.setMarginsFont(self.window_font)

        # key press
        # self.keyPressEvent = self.handle_editor_press

        # text change indicator
        self.got_first_change_event = False
        self.textChanged.connect(self.onTextChanged)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_Space:
            self.autoCompleteFromAll()
        else:
            return super().keyPressEvent(e)

    def onTextChanged(self):
        # Ignore First Change Event
        if not self.got_first_change_event:
            self.got_first_change_event = True
        # Signal Next Event If Change Is Novel
        elif not self.changed:
            self.star_func(self.file_path)
