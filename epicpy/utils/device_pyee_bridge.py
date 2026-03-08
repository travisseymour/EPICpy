"""
This file is part of the EPICpy source code. EPICpy is a tool for simulating
human performance tasks using the EPIC computational cognitive architecture
(David Kieras and David Meyer 1997a) using the Python programming language.
Copyright (C) 2022-2026 Travis L. Seymour, PhD

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

from epicpydevicelib.device_emitter import bus
from PySide6.QtCore import QObject, Signal


class QtEvents(QObject):
    stats_write = Signal(str)
    background_image = Signal(object)
    progress = Signal(int)


qt_events = QtEvents()

# Bridge pyee -> Qt signals
bus.on("stats_write", qt_events.stats_write.emit)
bus.on("background_image", qt_events.background_image.emit)
bus.on("progress", qt_events.progress.emit)

# GUI connects to qt_events signals:
# qt_events.info.connect(self.on_info)
