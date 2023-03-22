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

import cppyy
from cppinclude import epiclib_include
from cachedplaintextedit import CachedPlainTextEdit

epiclib_include("Model-View Classes/View_base.h")

from cppyy.gbl import View_base


class EPICTextViewCachedWrite(View_base):
    """
    Version of EPICTextView that is passed an instance of CachedPlainTextEdit
    to which it posts text output.
    """

    def __init__(self, text_widget: CachedPlainTextEdit):
        super(EPICTextViewCachedWrite, self).__init__()
        self.text_widget = text_widget

    def clear(self):
        self.text_widget.clear()

    def notify_append_text(self, text: str):
        self.text_widget.write(str(text).strip())

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            print("A missing method was called.")
            print("The object was %r, the method was %r. " % (self, name))
            print("It was called with %r and %r as arguments" % (args, kwargs))

        return _missing
