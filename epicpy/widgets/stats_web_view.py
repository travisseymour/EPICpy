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

"""QWebEngineView subclass that tracks and persists zoom level changes."""

from PySide6.QtWebEngineWidgets import QWebEngineView


class StatsWebView(QWebEngineView):
    """QWebEngineView subclass that preserves zoom across page loads."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._target_zoom = 1.0
        self.loadFinished.connect(self._reapply_zoom)

    def set_target_zoom(self, zoom: float):
        self._target_zoom = zoom
        self.setZoomFactor(zoom)

    def _reapply_zoom(self):
        if self._target_zoom != 1.0:
            self.setZoomFactor(self._target_zoom)

    def save_zoom(self):
        """Capture the current zoom factor (which may have been changed by the
        user via Ctrl+Wheel or Ctrl+Plus/Minus) so it survives page reloads."""
        self._target_zoom = self.zoomFactor()
        return self._target_zoom
