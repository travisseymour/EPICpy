# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

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
