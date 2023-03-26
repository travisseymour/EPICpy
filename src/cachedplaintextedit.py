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
from functools import partial

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QPlainTextEdit

from emoji import emoji_box, e_hourglass


class CachedPlainTextEdit(QPlainTextEdit):
    """
    When something is appended to this QPlainTextEdit widget, it gets added to the
    cache no matter what. If cache_text is enabled, then no further action is taken.
    If cache_text is disabled, then this method will lead to the entire cache being
    dumped to the widget.
    """

    def __init__(self, *args, **kwargs):
        super(CachedPlainTextEdit, self).__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.cache_text = False
        self.text_cache = []
        self.write_warning_limit = (
            kwargs["write_warning_limit"] if "write_warning_limit" in kwargs else 100000
        )
        self.dark_mode = False

    def write(self, text: str, disable_cache: bool = False) -> None:
        # _text = f"{text}"
        _text = str(text)

        if disable_cache:
            self.cache_text = False

        # NOTE:  This is a kludge to force dumping cache when sim is paused because of a
        # break on a rule. It's needed because this resulting pause does not use the pause
        # code in epicsimulation.py, but is instead handled within EPIC (initialed by
        # PPS and carried out in the Cog Processor.
        dump_cache_this_time = "Break on this cycle from rule" in _text

        if dump_cache_this_time:
            _text = emoji_box(_text)

        self.text_cache.append(_text)

        if dump_cache_this_time or not self.cache_text:
            N = len(self.text_cache)
            if N > self.write_warning_limit:
                # this write has to be direct, immediate, and not added to cache!
                msg = emoji_box(
                    f"\n\n{e_hourglass} Writing {N} lines of cached text...\n\n",
                    line="thick",
                )
                self.appendPlainText(msg)
                self.update()

            big_text = "\n".join(self.text_cache)

            if big_text.strip():
                # don't dump to widget if empty!
                ss = QTimer()
                ss.singleShot(100, partial(self.appendPlainText, big_text))

            self.text_cache = []

    def dump_cache(self):
        old_cache_status = self.cache_text
        self.cache_text = False
        self.write("")

        self.cache_text = old_cache_status
