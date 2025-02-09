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

import time
from datetime import datetime
import base64
from pathlib import Path

from qtpy.QtCore import (
    QMargins,
)
from qtpy.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextBrowser,
    QMenu,
    QFileDialog,
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QSizePolicy,
)
from qtpy.QtGui import QCloseEvent

from epicpy.uifiles.statsui import Ui_StatsWindow
from epicpy.utils.apputils import clear_font


from qtpy.QtGui import QImage, QTextDocument

from epicpy.utils.config import get_start_dir
from loguru import logger as log


class CustomStatsTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._has_image = False
        # Use a size policy that allows vertical size adjustments.
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        # Whenever the document contents change, update the height.
        self.document().contentsChanged.connect(self.update_height)

    def update_height(self):
        """Adjust the height of the browser to fit its contents."""
        # Set the text width to the viewport width to get an accurate height.
        self.document().setTextWidth(self.viewport().width())
        # Get the height from the document's layout; add a margin if needed.
        new_height = self.document().size().height() + 10
        # Update the minimum and maximum height so the widget resizes exactly to fit.
        self.setMinimumHeight(int(new_height))
        self.setMaximumHeight(int(new_height))

    def setHtml(self, html: str) -> None:
        """Set HTML content and update flag if it contains an image tag."""
        super().setHtml(html)
        self._has_image = "<img" in html.lower()

    def setPlainText(self, text: str) -> None:
        """Set plain text content and update flag accordingly."""
        super().setPlainText(text)
        self._has_image = False

    def contextMenuEvent(self, event):
        """Override the context menu to show actions based on content type."""
        menu = QMenu(self)
        if self._has_image:
            # Offer "Save as Image" if the content contains an image.
            save_action = menu.addAction("Save as Image")
            action = menu.exec_(event.globalPos())
            if action == save_action:
                self.save_as_image()
        else:
            # For text-only content, offer three actions:
            copy_text_action = menu.addAction("Copy Text")
            copy_html_action = menu.addAction("Copy HTML")
            copy_md_action = menu.addAction("Copy Markdown")
            action = menu.exec_(event.globalPos())
            if action == copy_text_action:
                QApplication.clipboard().setText(self.toPlainText())
            elif action == copy_html_action:
                QApplication.clipboard().setText(self.toHtml())
            elif action == copy_md_action:
                # Assumes that self.toMarkdown() exists.
                QApplication.clipboard().setText(self.toMarkdown())

    def save_as_image(self):
        """Grab a pixmap of the widget and let the user save it as an image."""
        # Obtain references to the scrollbars.
        v_scroll = self.verticalScrollBar()
        h_scroll = self.horizontalScrollBar()

        try:
            # Hide the scrollbars temporarily.
            v_scroll.hide()
            h_scroll.hide()
            # Now grab the widget's pixmap without the scrollbars showing.
            pixmap = self.grab()
        finally:
            # Ensure the scrollbars are shown again, even if grab() fails.
            v_scroll.show()
            h_scroll.show()

        start_dir = get_start_dir()

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save as Image",
            str(Path(start_dir, "image.png")),
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)",
        )
        if file_path:
            pixmap.save(file_path)

    def loadResource(self, resource_type, url):
        """
        Override loadResource to handle data URIs.
        If the URL starts with 'data:', decode the base64 image data and return a QImage.
        """
        if resource_type == QTextDocument.ResourceType.ImageResource:
            url_str = url.toString()
            if url_str.startswith("data:"):
                marker = "base64,"
                idx = url_str.find(marker)
                if idx != -1:
                    b64_data = url_str[idx + len(marker) :]
                    try:
                        img_data = base64.b64decode(b64_data)
                        image = QImage()
                        if image.loadFromData(img_data):
                            return image
                        else:
                            print("Failed to load image from data.")
                    except Exception as e:
                        print("Error decoding data URI:", e)
        return super().loadResource(resource_type, url)


class StatsWin(QMainWindow):
    def __init__(self, parent):
        super(StatsWin, self).__init__()

        self.view_type = b"StatsOut"
        self.setObjectName("StatsWindow")
        self.ui = Ui_StatsWindow()
        self.ui.setupUi(self)

        # Create a scrollable area to host our custom text browsers.
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        self.can_close = False

        # # Container widget with a vertical layout.
        # self.container = QWidget()
        # self.vlayout = QVBoxLayout(self.container)
        # self.container.setLayout(self.vlayout)
        # scroll_area.setWidget(self.container)

        # Container widget with a vertical layout.
        self.container = QWidget()
        self.vlayout = QVBoxLayout(self.container)
        self.vlayout.setSpacing(0)  # Remove any spacing between widgets.
        self.vlayout.setContentsMargins(QMargins(0, 0, 0, 0))  # Remove any margins (ltrb).
        self.container.setLayout(self.vlayout)
        scroll_area.setWidget(self.container)

        # replace designed font with application-wide font
        clear_font(self)

        now = datetime.now().strftime("%r")
        self.ui.statsTextBrowser.append(f"{f'Stats Out! ({now})'}")

        self.trace_out_view = None

        try:
            self.container.mouseDoubleClickEvent = parent.mouseDoubleClickEvent
        except AttributeError:
            ...

        self.clearing: bool = False

    def _write(self, text: str):
        """
        Create a new CustomTextBrowser, set its content, and add it to the layout.
        If the text starts with '<', assume its HTML.
        """
        browser = CustomStatsTextBrowser()
        if text.strip().startswith("<"):
            browser.setHtml(text)
        else:
            browser.setPlainText(text)
        self.vlayout.addWidget(browser)

    def write(self, text: str):
        if not self.clearing:
            self._write(text)

    def export_contents(self, parent=None) -> None:
        """
        Export the combined contents of all the QTextBrowser widgets
        in the vertical layout as one HTML file.
        """

        if hasattr(parent, "write"):
            writer = parent.write
        else:
            writer = log.info

        # Start building an HTML document.
        export_html = (
            "<html>" f"<head><meta charset='utf-8'><title>EPICpy Stats Export {time.ctime()}</title></head>" "<body>"
        )

        # Iterate through all widgets in the layout.
        # We're assuming that every widget in self.vlayout is a CustomTextBrowser.
        for i in range(self.vlayout.count()):
            widget = self.vlayout.itemAt(i).widget()
            if widget is not None:
                # Append the widget's HTML content with a horizontal rule between widgets.
                export_html += widget.toHtml() + "<hr>"

        export_html += "</body></html>"

        start_dir = get_start_dir()

        default_filename = "stats_export.html"

        # Open a file dialog to select a save location.
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Stats",
            str(Path(start_dir, default_filename)),
            "HTML Files (*.html);;All Files (*)",
            "HTML Files (*.html)",  # Optional: default selected filter
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(export_html)
                writer(f"\nExported stats contents to {file_path}\n")
            except Exception as e:
                writer(f"\n**** Error exporting: {str(e)} ****\n")

    def clear_layout(self, layout):
        """
        Recursively remove all items (widgets and nested layouts) from the given layout.
        """
        if layout is None:
            return

        try:

            self.clearing = True

            while layout.count():
                # Remove the item at index 0 each time.
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    # Remove the widget from its parent and schedule it for deletion.
                    widget.setParent(None)
                    widget.deleteLater()
                else:
                    # If the item is a layout, recursively clear it.
                    child_layout = item.layout()
                    if child_layout is not None:
                        self.clear_layout(child_layout)

        finally:

            self.clearing = False

    def clear(self):
        self.clear_layout(self.vlayout)

    def closeEvent(self, event: QCloseEvent):
        if self.can_close:
            self.hide()
        else:
            QMainWindow.closeEvent(self, event)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    win = StatsWin(parent=None)
    win.show()

    # Example usage:
    win.write("This is a plain text message.")
    win.write("<h1>HTML Content</h1><p>This is an HTML paragraph.</p>")

    # Example: HTML snippet containing a base64 encoded image.
    dummy_img_html = (
        "<img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA"
        "AAAFCAYAAACNbyblAAAAHElEQVQI12P4"
        "//8/w38GIAXDIBKE0DHxgljNBAAO"
        "9TXL0Y4OHwAAAABJRU5ErkJggg==' />"
    )
    win.write(dummy_img_html)

    sys.exit(app.exec_())
