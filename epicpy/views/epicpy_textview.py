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

from pathlib import Path
from typing import List, Optional

import _io  # for type hinting only

from PySide6.QtWidgets import QWidget

from epicpy.widgets.largetextview import LargeTextView


class EPICTextViewCachedWrite(QWidget):
    """
    Version of EPICTextView that is passed an instance of CachedPlainTextEdit
    to which it posts text output.
    NOTE: instead of being derivative of View_base, we just need a write_char interface
          for use with PyStreamer objects (see py_streamer.h)
    """

    def __init__(self, text_widget: LargeTextView):
        super(EPICTextViewCachedWrite, self).__init__()
        self.text_widget = text_widget
        self.buffer = []
        self.file_writer = EPICTextViewFileWriter()

    def clear(self):
        self.text_widget.clear()

    def write_char(self, char: str):
        """writes one character to a local buffer, only submitting to attached text_widget after a newline"""
        if char == "\n":
            txt = f"".join(self.buffer)
            extra = "" if txt.endswith("\n") else "\n"
            self.buffer = []
            self.text_widget.write(txt)
            if self.file_writer.enabled:
                self.file_writer.write(txt + extra)
        else:
            self.buffer.append(char)  # NOTE: if this leads to double-spaced output, move this to an else block

    def write(self, text: str):
        """writes given text to attached text_widget"""
        extra = ""  # if text.endswith('\n') else '\n'
        txt = text + extra
        self.text_widget.write(txt)
        if self.file_writer.enabled:
            self.file_writer.write(txt + extra)

    def flush(self):
        self.buffer.clear()
        self.text_widget.clear()

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            print("A missing method was called.")
            print("The object was %r, the method was %r. " % (self, name))
            print("It was called with %r and %r as arguments" % (args, kwargs))

        return _missing


class EPICTextViewFileWriter:
    """
    Version of EPICTextView that is passed a file path to which it posts text output.
    NOTE: instead of being derivative of View_base, we just need a write_char interface
          for use with PyStreamer objects (see py_streamer.h)
    """

    def __init__(self):
        super(EPICTextViewFileWriter, self).__init__()
        self.file_path: Optional[Path] = None
        self.file_mode = "a"
        self.file_object: _io.TextIOWrapper | None = None
        self.buffer: List[str] = []
        self.enabled = False

    def set_enabled(self):
        self.enabled = (
            isinstance(self.file_object, _io.TextIOWrapper)
            and not self.file_object.closed
            and self.file_object.writable()
        )

    def clear(self):
        """
        Clear the log file's content
        """
        try:
            self.file_object.truncate(0)
        except:
            ...
        self.set_enabled()

    def refresh(self):
        """
        Attempt to close and then open log file
        """
        if self.enabled:
            self.close()
            self.open(self.file_path, self.file_mode)
        self.set_enabled()

    def open(self, file_path: Path, file_mode: str = "a"):
        """
        Attempt to open log file for writing
        """
        self.close()

        self.file_mode = file_mode if file_mode in ("w", "a") else "a"

        try:
            self.file_object = open(file_path, self.file_mode)
            self.file_path = Path(file_path)
        except:
            self.file_object = None
            self.file_path = None
            raise
        finally:
            self.set_enabled()

    def close(self):
        """
        Attempt to close log file
        """
        if self.enabled:
            self.file_object.flush()
            self.file_object.close()
        else:
            self.file_object = None

        self.set_enabled()

    def write(self, text: str):
        """writes given text to attached file"""
        try:
            self.file_object.write(f"{text}")
        except:
            ...
