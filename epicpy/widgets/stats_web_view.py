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

"""QWebEngineView subclass that tracks and persists zoom level changes."""

import base64
from pathlib import Path

from loguru import logger as log
from PySide6.QtCore import QUrl
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWebEngineCore import QWebEngineContextMenuRequest
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu


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

    # ------------------------------------------------------------------
    # Context menu
    # ------------------------------------------------------------------

    def _image_from_data_uri(self, url: QUrl) -> QImage | None:
        """Decode a ``data:image/...;base64,...`` URI and return a QImage."""
        uri = url.toString()
        if not uri.startswith("data:image/"):
            return None
        try:
            # strip "data:image/png;base64," prefix
            b64 = uri.split(",", 1)[1]
            raw = base64.b64decode(b64)
            img = QImage()
            if img.loadFromData(raw):
                return img
        except Exception as e:
            log.warning(f"Failed to decode data-URI image: {e}")
        return None

    def _copy_image(self, url: QUrl):
        """Place the image at *url* on the system clipboard."""
        img = self._image_from_data_uri(url)
        if img is not None:
            QApplication.clipboard().setImage(img)

    def _save_image(self, url: QUrl):
        """Prompt the user and save the image at *url* to disk."""
        img = self._image_from_data_uri(url)
        if img is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image As",
            str(Path.home() / "graph.png"),
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;All Files (*)",
        )
        if file_path:
            path = Path(file_path)
            fmt = path.suffix.lstrip(".").upper()
            if fmt not in ("PNG", "JPG", "JPEG"):
                fmt = "PNG"
                path = path.with_suffix(".png")
            img.save(str(path), fmt)

    def _save_page(self):
        """Save the full page HTML (including embedded images) to disk."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Page As",
            str(Path.home() / "stats_output.html"),
            "HTML Files (*.html);;All Files (*)",
        )
        if not file_path:
            return

        out = Path(file_path)
        if out.suffix.lower() not in (".html", ".htm"):
            out = out.with_suffix(".html")

        def _on_html(html: str, dest=out):
            try:
                dest.write_text(html, encoding="utf-8")
            except OSError as e:
                log.error(f"Failed to save stats page: {e}")

        self.page().toHtml(_on_html)

    def contextMenuEvent(self, event):
        """Build a context menu with image and page actions."""
        menu = QMenu(self)
        ctx = self.lastContextMenuRequest()

        is_image = (
            ctx is not None
            and ctx.mediaType() == QWebEngineContextMenuRequest.MediaType.MediaTypeImage
        )

        if is_image:
            media_url = ctx.mediaUrl()
            copy_img = menu.addAction("Copy Image")
            copy_img.triggered.connect(lambda: self._copy_image(media_url))
            save_img = menu.addAction("Save Image As\u2026")
            save_img.triggered.connect(lambda: self._save_image(media_url))
            menu.addSeparator()

        # text copy when there is a selection
        if ctx is not None and ctx.selectedText():
            copy_text = menu.addAction("Copy")
            copy_text.triggered.connect(lambda: self.page().triggerAction(self.page().WebAction.Copy))
            menu.addSeparator()

        save_page = menu.addAction("Save Page As\u2026")
        save_page.triggered.connect(self._save_page)

        menu.exec(event.globalPos())
