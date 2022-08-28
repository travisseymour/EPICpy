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

import builtins
import keyword
import re
import types
from typing import Optional

from PyQt5.Qsci import QsciLexerCustom, QsciScintilla, QsciLexerPython
from PyQt5.QtGui import *


class PyCustomLexer(QsciLexerCustom):
    def __init__(self, parent):
        super(PyCustomLexer, self).__init__(parent)

        self.color1 = "#ffffff"  # "#abb2bf"
        self.color2 = "#282c34"

        # Default Settings
        self.setDefaultColor(QColor(self.color1))
        self.setDefaultPaper(QColor(self.color2))
        self.setDefaultFont(QFont("Consolas", 14))

        # Keywords
        self.KEYWORD_LIST = keyword.kwlist

        self.builtin_functions_names = [
            name
            for name, obj in vars(builtins).items()
            if isinstance(obj, types.BuiltinFunctionType)
        ]

        # color per style
        self.DEFAULT = 0
        self.KEYWORD = 1
        self.TYPES = 2
        self.STRING = 3
        self.KEYARGS = 4
        self.BRACKETS = 5
        self.COMMENTS = 6
        self.CONSTANTS = 7
        self.FUNCTIONS = 8
        self.CLASSES = 9
        self.FUNCTION_DEF = 10

        # styles
        self.setColor(QColor(self.color1), self.DEFAULT)
        self.setColor(QColor("#c678dd"), self.KEYWORD)  # (198 , 120 , 221)
        self.setColor(QColor("#56b6c2"), self.TYPES)  # (86 , 182 , 194)
        self.setColor(QColor("#98c379"), self.STRING)  # (152 , 195 , 121)
        self.setColor(QColor("#c678dd"), self.KEYARGS)  # (198 , 120 , 221)
        self.setColor(QColor("#c678dd"), self.BRACKETS)  # (198 , 120 , 221)
        self.setColor(QColor("#777777"), self.COMMENTS)  # (119 , 119 , 119)
        self.setColor(QColor("#d19a5e"), self.CONSTANTS)  # (209 , 154 , 94)
        self.setColor(QColor("#61afd1"), self.FUNCTIONS)  # (97 , 175 , 209)
        self.setColor(QColor("#C68F55"), self.CLASSES)  # (198 , 143 , 85)
        self.setColor(QColor("#61afd1"), self.FUNCTION_DEF)  # (97 , 175 , 209)

        # paper color
        self.setPaper(QColor(self.color2), self.DEFAULT)
        self.setPaper(QColor(self.color2), self.KEYWORD)
        self.setPaper(QColor(self.color2), self.TYPES)
        self.setPaper(QColor(self.color2), self.STRING)
        self.setPaper(QColor(self.color2), self.KEYARGS)
        self.setPaper(QColor(self.color2), self.BRACKETS)
        self.setPaper(QColor(self.color2), self.COMMENTS)
        self.setPaper(QColor(self.color2), self.CONSTANTS)
        self.setPaper(QColor(self.color2), self.FUNCTIONS)
        self.setPaper(QColor(self.color2), self.CLASSES)
        self.setPaper(QColor(self.color2), self.FUNCTION_DEF)

        # font
        self.setFont(QFont("Consolas", 14, QFont.Bold), self.DEFAULT)
        self.setFont(QFont("Consolas", 14, QFont.Bold), self.KEYWORD)
        self.setFont(QFont("Consolas", 14, QFont.Bold), self.CLASSES)
        self.setFont(QFont("Consolas", 14, QFont.Bold), self.FUNCTION_DEF)

    def language(self) -> str:
        return "PYCustomLexer"

    def description(self, style: int) -> str:
        if style == self.DEFAULT:
            return "DEFAULT"
        elif style == self.KEYWORD:
            return "KEYWORD"
        elif style == self.TYPES:
            return "TYPES"
        elif style == self.STRING:
            return "STRING"
        elif style == self.KEYARGS:
            return "KEYARGS"
        elif style == self.BRACKETS:
            return "BRACKETS"
        elif style == self.COMMENTS:
            return "COMMENTS"
        elif style == self.CONSTANTS:
            return "CONSTANTS"
        elif style == self.FUNCTIONS:
            return "FUNCTIONS"
        elif style == self.CLASSES:
            return "CLASSES"
        elif style == self.FUNCTION_DEF:
            return "FUNCTION_DEF"
        else:
            return ""

    def get_tokens(self, text) -> list[str, int]:
        # 3. Tokenize the text
        # ---------------------
        p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")

        # 'token_list' is a list of tuples: (token_name, token_len), ex: '(class, 5)'
        return [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

    def styleText(self, start: int, end: int) -> None:

        self.startStyling(start)
        editor: QsciScintilla = self.parent()

        text = editor.text()[start:end]
        token_list = self.get_tokens(text)

        string_flag = False

        if start > 0:
            previous_style_nr = editor.SendScintilla(editor.SCI_GETSTYLEAT, start - 1)
            if previous_style_nr == self.STRING:
                string_flag = False

        def next_tok(skip: int = None):
            if len(token_list) > 0:
                if skip is not None and skip != 0:
                    for _ in range(skip - 1):
                        if len(token_list) > 0:
                            token_list.pop(0)
                return token_list.pop(0)
            else:
                return None

        def peek_tok(n=0):
            try:
                return token_list[n]
            except IndexError:
                return [""]

        def skip_space_peek(skip=None):
            i = 0
            tok = " "
            if skip is not None:
                i = skip
            while tok[0].isspace():
                tok = peek_tok(i)
                i += 1
            return tok, i

        while True:
            curr_token = next_tok()
            if curr_token is None:
                break
            tok: str = curr_token[0]
            tok_len: int = curr_token[1]

            if string_flag:
                self.setStyling(tok_len, self.STRING)
                if tok == '"' or tok == "'":
                    string_flag = False
                continue

            if tok == "class":
                name, ni = skip_space_peek()
                brac_or_colon, _ = skip_space_peek(ni)
                if name[0].isidentifier() and brac_or_colon[0] in (":", "("):
                    self.setStyling(tok_len, self.KEYWORD)
                    _ = next_tok(ni)
                    self.setStyling(name[1] + 1, self.CLASSES)
                    continue
                else:
                    self.setStyling(tok_len, self.KEYWORD)
                    continue
            elif tok == "def":
                name, ni = skip_space_peek()
                if name[0].isidentifier():
                    self.setStyling(tok_len, self.KEYWORD)
                    _ = next_tok(ni)
                    self.setStyling(name[1] + 1, self.FUNCTION_DEF)
                    continue
                else:
                    self.setStyling(tok_len, self.KEYWORD)
                    continue
            elif tok in self.KEYWORD_LIST:
                self.setStyling(tok_len, self.KEYWORD)
            elif tok.isnumeric() or tok == "self":
                self.setStyling(tok_len, self.CONSTANTS)
            elif tok in ["(", ")", "{", "}", "[", "]"]:
                self.setStyling(tok_len, self.BRACKETS)
            elif tok == '"' or tok == "'":
                self.setStyling(tok_len, self.STRING)
                string_flag = True
            elif tok in self.builtin_functions_names or tok in [
                "+",
                "-",
                "*",
                "/",
                "%",
                "=",
                "<",
                ">",
            ]:
                self.setStyling(tok_len, self.TYPES)
            else:
                self.setStyling(tok_len, self.DEFAULT)


class TextCustomLexer(QsciLexerCustom):
    def __init__(self, parent):
        super(TextCustomLexer, self).__init__(parent)
        light_gray = QColor("#abb2bf")
        charcoal = QColor("#282c34")
        self.default_text_color = light_gray
        self.default_bg_color = charcoal

        # Default Settings
        self.setDefaultColor(light_gray)
        self.setDefaultPaper(charcoal)
        self.setDefaultFont(QFont("Consolas", 14))

        self.DEFAULT = 0
        self.NUMBER = 1

        # colors
        bright_green = QColor("#a6e22b")
        red = QColor("#f9245e")
        teal = QColor("#c678dd")
        brown = QColor("#736643")
        light_brown = QColor("#b39e69")
        purple = QColor("#ac7db8")
        yellow = QColor("#e7db74")
        orange = QColor("#fc9221")
        hot_pink = QColor("#ff00cc")
        light_blue = QColor("#6495ed")

        # styles
        self.setColor(QColor(self.default_text_color), self.DEFAULT)
        self.setColor(purple, self.NUMBER)

        # paper color
        self.setPaper(self.default_bg_color, self.DEFAULT)
        self.setPaper(self.default_bg_color, self.NUMBER)

    def description(self, style: int) -> str:
        if style == self.DEFAULT:
            return "DEFAULT"
        elif style == self.NUMBER:
            return "NUMBER"
        else:
            return ""

    def get_tokens(self, text) -> list[str, int]:

        p = re.compile(r"[*]|\/\/+|\s+|\w+|\W|\s")

        return [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

    def styleText(self, start: int, end: int) -> None:
        self.startStyling(start)
        editor: QsciScintilla = self.parent()

        text = editor.text()[start:end]
        token_list = [
            (s.lower(), i) if isinstance(s, str) else (s, i)
            for s, i in self.get_tokens(text)
        ]

        def next_tok(skip: int = None):
            if len(token_list) > 0:
                if skip is not None and skip != 0:
                    for _ in range(skip - 1):
                        if len(token_list) > 0:
                            token_list.pop(0)
                return token_list.pop(0)
            else:
                return None

        while True:
            current_token = next_tok()

            if current_token is None:
                break

            tok: str = current_token[0]
            tok_len: int = current_token[1]

            if tok.isnumeric():
                self.setStyling(tok_len, self.NUMBER)
            else:
                self.setStyling(tok_len, self.DEFAULT)


class PPSCustomLexer(QsciLexerCustom):
    def __init__(self, parent):
        super(PPSCustomLexer, self).__init__(parent)

        light_gray = QColor("#abb2bf")
        charcoal = QColor("#282c34")
        self.default_text_color = light_gray
        self.default_bg_color = charcoal

        self.last_tok: Optional[str] = None

        # Default Settings
        self.setDefaultColor(light_gray)
        self.setDefaultPaper(charcoal)
        self.setDefaultFont(QFont("Consolas", 14))

        # Keywords

        self.RULE_SECTIONS = "if", "then"
        self.COMPARISONS = [
            "not",
            "equal",
            "greater",
            "least",
            "different",
            "less-than",
            "less_than",
            "greater-than",
            "greater_than",
            "equal-to",
            "equal_to",
        ]
        self.DIRECTIVES = [
            "if-only-one",
            "if_only_one",
            "use-only-one",
            "use_only_one",
            "randomly-choose-one",
            "randomly_choose_one",
            "unique",
        ]
        self.ARCHITECTURES = [
            "goal",
            "step",
            "tag",
            "visual",
            "auditory",
            "tactile",
            "more",
            "initial-memory-contents",
            "initial_memory_contents",
            "parameters",
            "named-location",
            "named_location",
            "motor",
            "ocular",
            "manual",
            "vocal",
        ]
        self.KEYWORDS = [
            "add",
            "adddb",
            "del",
            "delete",
            "log",
            "define",
            "set-mode",
            "set_mode",
            "send-to-motor",
            "send_to_motor",
            "delay-countdown",
            "delay_countdown",
            "increment",
            "send-to-temporal",
            "send_to_temporal",
        ]

        # color per style
        self.DEFAULT = 0

        self.RULE_SECTION = 1
        self.COMPARISON = 2
        self.DIRECTIVE = 3  # rule binding directives
        self.ARCHITECTURE = 4  # architecture names (wm and other)

        self.COMMENT = 5  # // based comments
        self.NUMBER = 6

        self.RULE_NAME = 7
        self.VARIABLE = 8

        self.KEYWORD = 9
        self.PARENS = 10

        # colors
        bright_green = QColor("#a6e22b")  # (166 , 226 , 43)
        red = QColor("#f9245e")  # (249 , 36 , 94)
        teal = QColor("#c678dd")  # (198 , 120 , 221)
        brown = QColor("#736643")  # (115 , 102 , 67)
        light_brown = QColor("#b39e69")  # (179 , 158 , 105)
        purple = QColor("#ac7db8")  # (172 , 125 , 184)
        yellow = QColor("#e7db74")  # (231 , 219 , 116)
        orange = QColor("#fc9221")  # (252 , 146 , 33)
        hot_pink = QColor("#ff00cc")  # (255 , 0 , 204)
        light_blue = QColor("#6495ed")  # (100 , 149 , 237)

        # styles
        self.setColor(QColor(self.default_text_color), self.DEFAULT)
        self.setColor(QColor(self.default_text_color), self.PARENS)
        self.setColor(yellow, self.RULE_SECTION)
        self.setColor(bright_green, self.COMPARISON)
        self.setColor(red, self.DIRECTIVE)
        self.setColor(teal, self.ARCHITECTURE)
        self.setColor(brown, self.COMMENT)
        self.setColor(purple, self.NUMBER)
        self.setColor(yellow, self.RULE_NAME)
        self.setColor(orange, self.VARIABLE)
        self.setColor(light_blue, self.KEYWORD)

        # paper color
        self.setPaper(self.default_bg_color, self.DEFAULT)
        self.setPaper(self.default_bg_color, self.PARENS)
        self.setPaper(self.default_bg_color, self.RULE_SECTION)
        self.setPaper(self.default_bg_color, self.COMPARISON)
        self.setPaper(self.default_bg_color, self.DIRECTIVE)
        self.setPaper(self.default_bg_color, self.ARCHITECTURE)
        self.setPaper(self.default_bg_color, self.COMMENT)
        self.setPaper(self.default_bg_color, self.NUMBER)
        self.setPaper(self.default_bg_color, self.RULE_NAME)
        self.setPaper(self.default_bg_color, self.VARIABLE)
        self.setPaper(self.default_bg_color, self.KEYWORD)

        # font
        normal_font = QFont("Consolas", 14)
        bold_font = QFont("Consolas", 14, weight=QFont.Bold)
        self.setFont(normal_font, self.DEFAULT)
        self.setFont(normal_font, self.PARENS)
        self.setFont(bold_font, self.RULE_SECTION)
        self.setFont(bold_font, self.COMPARISON)
        self.setFont(bold_font, self.DIRECTIVE)
        self.setFont(bold_font, self.ARCHITECTURE)
        self.setFont(normal_font, self.COMMENT)
        self.setFont(normal_font, self.NUMBER)
        self.setFont(bold_font, self.RULE_NAME)
        self.setFont(normal_font, self.VARIABLE)
        self.setFont(bold_font, self.KEYWORD)

    def language(self) -> str:
        return "PPS_Rule_Lexer"

    def description(self, style: int) -> str:
        if style == self.DEFAULT:
            return "DEFAULT"
        elif style == self.RULE_SECTION:
            return "RULE_SECTION"
        elif style == self.COMPARISON:
            return "COMPARISON"
        elif style == self.DIRECTIVE:
            return "DIRECTIVE"
        elif style == self.ARCHITECTURE:
            return "ARCHITECTURE"
        elif style == self.COMMENT:
            return "COMMENT"
        elif style == self.NUMBER:
            return "NUMBER"
        elif style == self.RULE_NAME:
            return "RULE_NAME"
        elif style == self.VARIABLE:
            return "VARIABLE"
        elif style == self.KEYWORD:
            return "KEYWORD"
        elif style == self.PARENS:
            return "PARENS"
        else:
            return ""

    def get_tokens(self, text) -> list[str, int]:
        # 3. Tokenize the text
        # ---------------------

        p = re.compile(r"[*]|\/\/+|\s+|\w+|\W|\s")

        # 'token_list' is a list of tuples: (token_name, token_len), ex: '(class, 5)'
        return [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

    def styleText(self, start: int, end: int) -> None:
        self.startStyling(start)
        editor: QsciScintilla = self.parent()

        text = editor.text()[start:end]
        token_list = [
            (s.lower(), i) if isinstance(s, str) else (s, i)
            for s, i in self.get_tokens(text)
        ]
        # from pathlib import Path
        # Path('freaky_deekey.txt').write_text(str(token_list))
        string_flag = False

        if start > 0:
            previous_style_nr = editor.SendScintilla(editor.SCI_GETSTYLEAT, start - 1)
            if previous_style_nr == self.COMMENT:
                string_flag = False

        def next_tok(skip: int = None):
            if len(token_list) > 0:
                if skip is not None and skip != 0:
                    for _ in range(skip - 1):
                        if len(token_list) > 0:
                            token_list.pop(0)
                return token_list.pop(0)
            else:
                return None

        def peek_tok(n=0):
            try:
                return token_list[n]
            except IndexError:
                return [""]

        def skip_space_peek(skip=None):
            i = 0
            tok = " "
            if skip is not None:
                i = skip
            while tok[0].isspace():
                tok = peek_tok(i)
                i += 1
            return tok, i

        last_token: Optional[str] = None
        current_token: Optional[str] = None

        while True:
            if current_token:
                last_token = current_token
            current_token = next_tok()

            if current_token is None:
                break

            tok: str = current_token[0]
            tok_len: int = current_token[1]

            if string_flag:
                self.setStyling(tok_len, self.COMMENT)
                if tok.startswith("\n"):
                    string_flag = False
                continue

            elif tok in self.RULE_SECTIONS:
                self.setStyling(tok_len, self.RULE_SECTION)
            elif tok in self.COMPARISONS:
                self.setStyling(tok_len, self.COMPARISON)
            elif tok in self.DIRECTIVES:
                self.setStyling(tok_len, self.DIRECTIVE)
            elif tok in self.ARCHITECTURES:
                self.setStyling(tok_len, self.ARCHITECTURE)
            elif tok in self.KEYWORDS:
                self.setStyling(tok_len, self.KEYWORD)
            elif tok.isnumeric():
                self.setStyling(tok_len, self.NUMBER)
            elif tok in ("(", ")"):
                self.setStyling(tok_len, self.PARENS)
            elif tok.startswith(";") or tok.startswith("//"):
                self.setStyling(tok_len, self.COMMENT)
                string_flag = True
            else:
                peek = peek_tok()

                if (
                    len(tok) > 2
                    and last_token
                    and last_token[0] == "("
                    and peek
                    and peek[0].startswith("\n")
                ):
                    self.setStyling(tok_len, self.RULE_NAME)
                elif tok == "?" and last_token and last_token[0] in ("?", " ", "("):
                    self.setStyling(tok_len, self.VARIABLE)
                elif "?" not in tok and last_token and last_token[0] == "?":
                    self.setStyling(tok_len, self.VARIABLE)
                else:
                    self.setStyling(tok_len, self.DEFAULT)
