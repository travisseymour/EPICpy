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

import logging
from pathlib import Path
from typing import List, Optional

import _io  # for type hinting only

from qtpy.QtWidgets import QWidget

from epicpy.widgets.largetextview import LargeTextView


class EPICTextViewCachedWrite(QWidget):
    """
    Version of EPICTextView that is passed an instance of CachedPlainTextEdit
    to which it posts text output.
    QUESTION: Why Not Just Use A LTV and skip this thing?!
    """

    def __init__(self, text_widget: LargeTextView):
        super(EPICTextViewCachedWrite, self).__init__()
        self._buffer: str = ""
        self.widget_writer = text_widget
        self.file_writer = EPICTextViewFileWriter()
        self._rem = ""

    def write(self, text, /):
        # Fast path: no newline in this chunk -> just accumulate
        if "\n" not in text:
            self._rem += text
            return

        # One concat, then split in C
        chunk = self._rem + text
        parts = chunk.split("\n")  # split removes '\n'
        self._rem = parts.pop()  # last part may be partial (no newline)

        if not parts:
            return

        do_file_write = self.file_writer.enabled
        widget_writer, file_writer = self.widget_writer.write, self.file_writer.write
        # Build once; one call per completed line
        for line in parts:
            widget_writer(line)
            if do_file_write:
                file_writer(line)

    def flush(self):
        # Finalize any partial line as a full line
        if self._rem:
            self.widget_writer.write(self._rem)
            if self.file_writer.enabled:
                self.file_writer.write(self._rem)
            self._rem = ""

    def close(self):
        self.flush()


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
            self.file_object.write(text)
        except:
            ...
