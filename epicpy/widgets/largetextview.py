import sys
import timeit

from qtpy.QtTest import QTest
from qtpy.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QScrollBar, QLabel, QMessageBox, QMenu
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QPainter, QFontMetrics, QWheelEvent, QFont, QContextMenuEvent

from epicpy.dialogs.searchwindow import SearchWin
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
        self.pending_lines: list[str] = []

        self.enable_context_menu = enable_context_menu
        self.current_line_location = 0
        self.default_pen = None
        self.update_frequency_ms = update_frequency_ms
        self.wait_msg_limit = wait_msg_limit

        # create context menu
        if self.enable_context_menu:
            self.context_menu = QMenu(self)
            self.search_action = self.context_menu.addAction("Search")
            self.context_menu.addSeparator()
            self.copy_action = self.context_menu.addAction("Copy")
            self.copy_action.setText(f"Copy All")
            self.context_menu.addSeparator()
            self.clear_action = self.context_menu.addAction("Clear")
            self.contextMenuEvent = self.context_menu_event_handler
        else:
            self.context_menu = None
            self.clear_action = None
            self.search_action = None

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

        # search dialog setup
        self.search_dialog = SearchWin()
        self.search_dialog.setModal(True)
        self.last_search_spec = {}

        # Create a QLabel for the "Please Wait" message
        wait_font = QFont(QApplication.instance().font())
        wait_font.setPointSize(48)  # was 54
        self.wait_label = QLabel("Please Wait")
        self.wait_label.setFont(wait_font)
        self.wait_label.setStyleSheet("color: rgba(106, 121, 240, 50);")
        self.wait_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wait_label.setVisible(False)
        self.wait_threshold = self.wait_msg_limit

        # Timer to periodically update the view
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.process_pending_lines)
        self.set_updating(True)

    @property
    def line_height(self):
        return QFontMetrics(self.font()).lineSpacing()

    @property
    def is_updating(self) -> bool:
        return self.update_timer.isActive()

    def set_updating(self, flag: bool):
        if flag:
            if not self.is_updating:
                self.update_timer.start(self.update_frequency_ms)
        else:
            if self.is_updating:
                self.update_timer.stop()

    def setPlainText(self, text: str):
        self.clear()
        self.write(text)

    def append_text(self, text):
        self.write(text)

    def write(self, text):
        if "\n" in text:
            for aline in text.splitlines(keepends=False):
                self.pending_lines.append(aline)
        else:
            self.pending_lines.append(text)

    def clear(self):
        self.update_timer.stop()
        self.lines = []
        self.pending_lines = []
        self.current_line_location = 0
        self.scroll_bar.setValue(0)
        self.scroll_bar.setMaximum(0)
        self.update_timer.start(self.update_frequency_ms)

    def is_idle(self):
        return not self.pending_lines

    def flush(self):
        self.clear()

    def get_text(self) -> str:
        """
        This is kind of a bad idea if self.lines contains, e.g., 10 million lines of text.
        It is much wiser to just read through self.lines and either save them to disk, display
        them somewhere, etc.
        """
        return "\n".join(self.lines)

    def process_pending_lines(self):
        if not self.update_timer.isActive():
            return

        if len(self.pending_lines) > self.wait_threshold:
            if not self.wait_label.isVisible():
                self.wait_label.setVisible(True)
        else:
            if self.wait_label.isVisible():
                self.wait_label.setVisible(False)

        self.update()

        if self.pending_lines:
            self.lines.extend(self.pending_lines)
            self.pending_lines = []
            self.scroll_bar.setMaximum(len(self.lines) - 1)

            start_line = max(0, len(self.lines) - self.height() // self.line_height)
            end_line = min(len(self.lines), start_line + self.height() // self.line_height)

            if start_line > 0 or end_line < len(self.lines):
                self.scroll_bar.setSliderPosition(start_line)

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

        # Adjust the painting area to avoid drawing behind the scrollbar
        text_area_width = self.width() - self.scroll_bar.width()

        for i in range(visible_lines):
            line_number = start_line + i

            highlighted_line_number = self.current_line_location - self.scroll_bar.value()
            if 0 <= highlighted_line_number < visible_lines:
                painter.drawRect(0, highlighted_line_number * line_height, text_area_width, line_height)

            if line_number < len(self.lines):
                line_text = self.lines[line_number]
                painter.drawText(
                    0,
                    (i + 0) * line_height,
                    text_area_width,
                    line_height,
                    Qt.AlignmentFlag.AlignLeft,
                    line_text,
                )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scroll_bar.setSingleStep(self.height() // self.line_height)
        self.update_wait_label_position()

    def wheelEvent(self, event: QWheelEvent):
        scroll_amount = event.angleDelta().y()
        new_value = self.scroll_bar.value() - scroll_amount // 120  # Standard delta is 120 per step
        self.scroll_bar.setValue(new_value)
        event.accept()

    def update_wait_label_position(self):
        self.wait_label.setGeometry(0, 0, self.width(), self.height())

    def continue_find_text(self) -> bool:
        if not self.last_search_spec or not len(self.lines):
            return False

        if self.last_search_spec["backwards"] is True:
            if self.current_line_location - 1 < 0:
                self.current_line_location -= 1
        if self.last_search_spec["backwards"] is False:
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

        if len(self.lines) > 500_000:
            find_func = find_next_index_with_target_parallel_concurrent
        else:
            find_func = find_next_index_with_target_serial

        result = find_func(
            lines=self.lines,
            target=pattern,
            start_line=self.current_line_location,  # self.scroll_bar.value(),
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
                f"{'BACKWARD' if backwards else 'FORWARD'}SEARCH ERROR: Unable to locate '{pattern}' "
                f"in text starting from the current search start location "
                f"(Line {self.current_line_location}).",
            )

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
            # Calculate the clicked row based on the click position and line height
            line_height = self.line_height
            click_pos = event.position() - self.rect().topLeft()
            clicked_row = (click_pos.y() + self.scroll_bar.value() * line_height) // line_height

            # Ensure clicked_row is within the range of lines
            if 0 <= clicked_row < len(self.lines):
                self.current_line_location = int(clicked_row)  # was clicked_row - 1
                # print("Clicked row:", self.current_line_location)
                # print("Text:", self.lines[self.current_line_location])

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F3:
            self.continue_find_text()
        else:
            super().keyPressEvent(event)

    def query_search(self):
        if not len(self.lines):
            QMessageBox.warning(self, "Warning", "There is currently no text to search.", QMessageBox.StandardButton.Ok)

        self.search_dialog.ok = False
        self.search_dialog.ui.checkBoxRegEx.setChecked(
            self.last_search_spec["use_regex"] if hasattr(self.last_search_spec, "use_regex") else False
        )
        self.search_dialog.ui.checkBoxIgnoreCase.setChecked(
            self.last_search_spec["ignore_case"] if hasattr(self.last_search_spec, "ignore_case") else False
        )
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
            f"Copied contexts of this window to the clipboard",
        )


if __name__ == "__main__":

    class LTTTestMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Large Text Viewer")

            self.viewer = LargeTextView(update_frequency_ms=50)
            self.viewer.setFixedSize(800, 600)
            self.setCentralWidget(self.viewer)

            # Use QTimer.singleShot to delay the call to populate_text
            QTimer.singleShot(0, self.populate_text)

        def populate_text(self):
            # n = 33_000_000
            # n = 10_000_000
            # n = 1_000_000
            n = 100_000
            # n = 1000
            start = timeit.default_timer()
            for i in range(n):
                self.viewer.append_text(f"Line {i}")
                if i % 1000 == 0:
                    QTest.qWait(1)
            print(f"populate_text added {n} lines in {timeit.default_timer() - start} sec.")

    app = QApplication(sys.argv)
    window = LTTTestMainWindow()
    window.show()
    sys.exit(app.exec())
