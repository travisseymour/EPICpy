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

from cachedplaintextedit import CachedPlainTextEdit


# class EPICTextViewCachedWrite(View_base):
#     """
#     Version of EPICTextView that is passed an instance of CachedPlainTextEdit
#     to which it posts text output.
#     """
#
#     def __init__(self, text_widget: CachedPlainTextEdit):
#         super(EPICTextViewCachedWrite, self).__init__()
#         self.text_widget = text_widget
#
#     def clear(self):
#         self.text_widget.clear()
#
#     def notify_append_text(self, text: str):
#         self.text_widget.write(str(text).strip())
#
#     def __getattr__(self, name):
#         def _missing(*args, **kwargs):
#             print("A missing method was called.")
#             print("The object was %r, the method was %r. " % (self, name))
#             print("It was called with %r and %r as arguments" % (args, kwargs))
#
#         return _missing

class EPICTextViewCachedWrite:
    """
    Version of EPICTextView that is passed an instance of CachedPlainTextEdit
    to which it posts text output.
    NOTE: instead of being derivative of View_base, we just need a write_char interface
          for use with PyStreamer objects (see py_streamer.h)
    """

    def __init__(self, text_widget: CachedPlainTextEdit):
        super(EPICTextViewCachedWrite, self).__init__()
        self.text_widget = text_widget
        self.buffer = []

    def clear(self):
        self.text_widget.clear()

    def write_char(self, char: str):
        """writes one character to a local buffer, only submitting to attached text_widget after a newline"""
        if char == '\n':
            self.text_widget.write(f"".join(self.buffer))
            self.buffer = []
        else:
            self.buffer.append(char)  # NOTE: if this leads to double-spaced output, move this to an else block

    def write(self, text: str):
        """writes given text to attached text_widget"""
        self.text_widget.write(str(text).strip())  # TODO: do we need this strip() -- maybe stripping of the newline??

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            print("A missing method was called.")
            print("The object was %r, the method was %r. " % (self, name))
            print("It was called with %r and %r as arguments" % (args, kwargs))

        return _missing
