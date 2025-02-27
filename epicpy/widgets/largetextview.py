import sys
import timeit
from collections import deque

from epicpy.utils import config
from qtpy.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QScrollBar, QMessageBox, QMenu
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QPainter, QFontMetrics, QWheelEvent, QFont, QContextMenuEvent

from epicpy.dialogs.searchwindow import SearchWin
from epicpy.utils.apputils import is_dark_mode
from epicpy.utils.viewsearch import find_next_index_with_target_parallel_concurrent, find_next_index_with_target_serial


class LargeTextView(QWidget):
    def __init__(
        self,
        parent=None,
        update_frequency_ms: int = 100,
        page_step_lines: int = 100,
        wait_msg_limit: int = 100_1000,
        enable_context_menu: bool = True,
    ):
        super().__init__(parent)
        self.lines: list[str] = []
        self.pending_lines = deque()

        self.enable_updates: bool = True
        self.is_dark_mode: bool = config.app_cfg.dark_mode.lower() == 'dark' or is_dark_mode()
        self.enable_context_menu = enable_context_menu
        self.current_line_location = 0
        self.default_pen = None
        self.update_frequency_ms = update_frequency_ms
        self.wait_msg_limit = wait_msg_limit

        # Create context menu if enabled
        if self.enable_context_menu:
            self.context_menu = QMenu(self)
            self.search_action = self.context_menu.addAction("Search")
            self.context_menu.addSeparator()
            self.copy_action = self.context_menu.addAction("Copy")
            self.copy_action.setText("Copy All")
            self.context_menu.addSeparator()
            self.clear_action = self.context_menu.addAction("Clear")
            self.contextMenuEvent = self.context_menu_event_handler
        else:
            self.context_menu = None

        # Create the scrollbar and set it to the right
        self.scroll_bar = QScrollBar(Qt.Orientation.Vertical, self)
        self.scroll_bar.valueChanged.connect(self.update)
        self.scroll_bar.setMaximum(0)
        self.scroll_bar.setPageStep(page_step_lines)

        # Create a layout to hold the scrollbar and content area
        layout = QHBoxLayout(self)
        layout.addWidget(self.scroll_bar, 0, Qt.AlignmentFlag.AlignRight)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search dialog setup
        self.search_dialog = SearchWin()
        self.search_dialog.setModal(True)
        self.last_search_spec = {}

        # (The "Please Wait" label has been removed)

        # Start the self-rescheduling timer
        QTimer.singleShot(self.update_frequency_ms, self.process_pending_lines)

    @property
    def line_height(self):
        return QFontMetrics(self.font()).lineSpacing()

    def setPlainText(self, text: str):
        self.clear()
        self.write(text)

    def append_text(self, text):
        self.write(text)

    def write(self, text):
        if "\n" in text:
            self.pending_lines.extend(
                line for line in text.splitlines(False) if "TLSDEBUG" not in line
            )
        elif "TLSDEBUG" not in text:
            self.pending_lines.append(text)
        # No need to start a timer—our self-rescheduling timer is always running

    def clear(self):
        self.lines = []
        self.pending_lines.clear()
        self.current_line_location = 0
        self.scroll_bar.setValue(0)
        self.scroll_bar.setMaximum(0)
        self.update()  # Force immediate repaint

    def is_idle(self):
        return not self.pending_lines

    def flush(self):
        self.clear()

    def get_text(self) -> str:
        return "\n".join(self.lines)

    def process_pending_lines(self):
        delay = self.update_frequency_ms

        if self.enable_updates:
            # Process pending lines if any
            if self.pending_lines:
                # Process in controlled batches
                batch_size = min(5000, len(self.pending_lines))
                for _ in range(batch_size):
                    self.lines.append(self.pending_lines.popleft())

                # Adjust scrollbar maximum and auto-scroll to the bottom
                self.scroll_bar.setMaximum(len(self.lines) - 1)
                visible_lines = self.height() // self.line_height
                new_scroll_value = max(0, len(self.lines) - visible_lines)
                self.scroll_bar.setValue(new_scroll_value)
                # Use a shorter delay when there’s a backlog
                delay = self.update_frequency_ms // 2

                self.update()  # Trigger UI repaint only if a change is made

        # Reschedule the next update
        QTimer.singleShot(delay, self.process_pending_lines)

    def lines_in_view(self):
        visible_lines = self.height() // self.line_height
        start_line = self.scroll_bar.value()
        return set(range(start_line, start_line + visible_lines))

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.default_pen is None:
            self.default_pen = painter.pen()

        line_height = self.line_height
        visible_lines = self.height() // line_height
        start_line = self.scroll_bar.value()
        text_area_width = self.width() - self.scroll_bar.width()

        # Determine a suitable highlight color
        if self.is_dark_mode:
            highlight_color = self.palette().highlight().color().lighter(120)
        else:
            highlight_color = self.palette().highlight().color().darker(120)

        # Determine the relative position of the highlighted line
        highlighted_line = self.current_line_location - start_line
        if 0 <= highlighted_line < visible_lines:
            painter.fillRect(0, highlighted_line * line_height, text_area_width, line_height,
                             highlight_color)

        for i in range(visible_lines):
            line_number = start_line + i
            if line_number < len(self.lines):
                line_text = self.lines[line_number]
                painter.drawText(0, i * line_height, text_area_width, line_height,
                                 Qt.AlignmentFlag.AlignLeft, line_text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scroll_bar.setSingleStep(self.height() // self.line_height)

    def wheelEvent(self, event: QWheelEvent):
        scroll_amount = event.angleDelta().y()
        new_value = self.scroll_bar.value() - scroll_amount // 120  # Standard delta is 120 per step
        self.scroll_bar.setValue(new_value)
        event.accept()

    def context_menu_event_handler(self, event: QContextMenuEvent):
        action = self.context_menu.exec(event.globalPos())
        if action == self.clear_action:
            self.clear()
        elif action == self.search_action:
            self.query_search()
        elif action == self.copy_action:
            self.copy_to_clipboard()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            line_height = self.line_height
            click_pos = event.position() - self.rect().topLeft()
            clicked_row = (click_pos.y() + self.scroll_bar.value() * line_height) // line_height
            if 0 <= clicked_row < len(self.lines):
                self.current_line_location = int(clicked_row)
                self.update()  # Force a repaint to show the highlight

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F3:
            self.continue_find_text()
        else:
            super().keyPressEvent(event)

    def continue_find_text(self) -> bool:
        if not self.last_search_spec or not self.lines:
            return False

        if self.last_search_spec["backwards"]:
            if self.current_line_location - 1 >= 0:
                self.current_line_location -= 1
        else:
            if self.current_line_location + 1 < len(self.lines):
                self.current_line_location += 1

        self.find_text(
            pattern=self.last_search_spec["pattern"],
            use_regex=self.last_search_spec["use_regex"],
            ignore_case=self.last_search_spec["ignore_case"],
            backwards=self.last_search_spec["backwards"],
        )
        return True

    def find_text(
        self,
        pattern: str,
        use_regex: bool = False,
        ignore_case: bool = False,
        backwards: bool = False,
    ):
        self.last_search_spec = {
            "pattern": pattern,
            "use_regex": use_regex,
            "ignore_case": ignore_case,
            "backwards": backwards,
        }

        if self.current_line_location > len(self.lines) - 1:
            self.current_line_location = len(self.lines) - 1

        find_func = (
            find_next_index_with_target_parallel_concurrent
            if len(self.lines) > 500_000
            else find_next_index_with_target_serial
        )

        result = find_func(
            lines=self.lines,
            target=pattern,
            start_line=self.current_line_location,
            direction="backward" if backwards else "forward",
            is_regex=use_regex,
            ignore_case=ignore_case,
        )

        if result >= 0:
            self.scroll_bar.setValue(result)
            self.current_line_location = result
            self.update()
        else:
            QMessageBox.critical(
                self,
                "Search Error",
                f"{'BACKWARD' if backwards else 'FORWARD'} SEARCH ERROR: Unable to locate '{pattern}' "
                f"in text starting from line {self.current_line_location}.",
                QMessageBox.StandardButton.Ok,
            )

    def query_search(self):
        if not self.lines:
            QMessageBox.warning(self, "Warning", "There is currently no text to search.", QMessageBox.StandardButton.Ok)
            return

        self.search_dialog.ok = False
        self.search_dialog.ui.checkBoxRegEx.setChecked(self.last_search_spec.get("use_regex", False))
        self.search_dialog.ui.checkBoxIgnoreCase.setChecked(self.last_search_spec.get("ignore_case", False))
        self.search_dialog.exec()

        if self.search_dialog.ok:
            self.last_search_spec = {
                "pattern": self.search_dialog.ui.lineEditSearchText.text(),
                "use_regex": self.search_dialog.ui.checkBoxRegEx.isChecked(),
                "ignore_case": self.search_dialog.ui.checkBoxIgnoreCase.isChecked(),
                "backwards": self.search_dialog.backwards,
            }
            self.find_text(**self.last_search_spec)

    def copy_to_clipboard(self):
        QApplication.instance().clipboard().setText(self.get_text())
        QMessageBox.information(
            self,
            "Text Copied To Clipboard",
            "Copied contents of this window to the clipboard",
        )


if __name__ == "__main__":

    class LTTTestMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Large Text Viewer")

            self.viewer = LargeTextView(update_frequency_ms=50)
            self.viewer.setFixedSize(800, 600)
            self.setCentralWidget(self.viewer)

            # Delay the call to populate_text so the UI is ready.
            QTimer.singleShot(0, self.populate_text)

        def populate_text(self):
            # n = 33_000_000
            n = 10_000_000
            # n = 1_000_000
            # n = 100_000
            # n = 1000
            start = timeit.default_timer()
            batch_size = 5000  # Number of lines per batch
            buffer = []

            for i in range(n):
                buffer.append(f"Line {i}")
                if len(buffer) >= batch_size:
                    self.viewer.append_text("\n".join(buffer))
                    buffer.clear()
                    QApplication.processEvents()

            if buffer:
                self.viewer.append_text("\n".join(buffer))

            print(f"populate_text added {n} lines in {timeit.default_timer() - start} sec.")

    app = QApplication(sys.argv)
    window = LTTTestMainWindow()
    window.show()
    sys.exit(app.exec())
