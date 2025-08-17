import platform
import subprocess
import re
from pathlib import Path
import sys

from qtpy import QtGui
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QScrollBar,
    QMenu,
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QHBoxLayout as HBox,
    QCheckBox,
    QMessageBox,
)
from collections import deque

from qtpy.QtCore import Qt, QPoint, QTimer
from qtpy.QtGui import QPainter, QFontMetrics, QFont, QContextMenuEvent, QKeySequence, QShortcut

from epicpy.constants.stateconstants import PAUSED, RUNNING
from epicpy.utils import config


class SearchDialog(QDialog):
    def __init__(self, parent=None, start_text: str = "", start_is_regex: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Find Text")
        self.setModal(True)
        self.setMinimumWidth(420)  # make it wider

        self.input = QLineEdit(self)
        self.regex_cb = QCheckBox("Regex", self)

        self.next_button = QPushButton("Find Next")
        self.prev_button = QPushButton("Find Previous")

        layout = QVBoxLayout(self)

        form = HBox()
        form.addWidget(QLabel("Find:"))
        form.addWidget(self.input)
        layout.addLayout(form)

        layout.addWidget(self.regex_cb)

        button_row = HBox()
        button_row.addWidget(self.prev_button)
        button_row.addWidget(self.next_button)
        layout.addLayout(button_row)

        self.next_button.clicked.connect(self.accept)
        self.prev_button.clicked.connect(self.reject)

        if start_text:
            self.input.setText(start_text)
            self.input.selectAll()
        self.regex_cb.setChecked(start_is_regex)


class LargeTextView(QWidget):
    def __init__(
        self,
        parent: object = None,
        update_frequency_ms: int = 100,
        page_step_lines: int = 100,
        wait_msg_limit: int = 100_000,
        name: str = "",
        enable_shortcuts: bool = True,
    ):
        super().__init__(parent)
        self.name = name
        self._parent = parent

        self.lines: list[str] = []
        self.pending_lines = deque()

        self.update_frequency_ms = update_frequency_ms
        self.wait_msg_limit = wait_msg_limit

        self.selection_start_line = None
        self.selection_end_line = None
        self.word_wrap = True
        self.current_search_index = 0
        self.processing_paused = False

        self.last_search_pattern: str = ""
        self.last_is_regex: bool = False
        self._last_regex = None  # type: re.Pattern | None

        font = QFont("Courier New" if sys.platform == "win32" else "Courier", 14)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self._font_metrics = QFontMetrics(self.font())

        self.scroll_bar = QScrollBar(Qt.Orientation.Vertical, self)
        self.scroll_bar.valueChanged.connect(self.update)
        self.scroll_bar.setMaximum(0)
        self.scroll_bar.setPageStep(page_step_lines)
        # self.scroll_bar.setSingleStep(3)

        layout = QHBoxLayout(self)
        layout.addWidget(self.scroll_bar, 0, Qt.AlignmentFlag.AlignRight)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # make focusable
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scroll_bar.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # shortcuts: disable if you are planning global shortcuts on the parent window.
        if enable_shortcuts:
            self.copy_sc = QShortcut(QKeySequence(QKeySequence.StandardKey.Copy), self)
            self.copy_sc.setContext(Qt.ShortcutContext.WindowShortcut)
            self.copy_sc.activated.connect(self.copy_selected_text)

            self.selall_sc = QShortcut(QKeySequence(QKeySequence.StandardKey.SelectAll), self)
            self.selall_sc.setContext(Qt.ShortcutContext.WindowShortcut)
            self.selall_sc.activated.connect(self.select_all)

            self.find_sc = QShortcut(QKeySequence(QKeySequence.StandardKey.Find), self)
            self.find_sc.setContext(Qt.ShortcutContext.WindowShortcut)
            self.find_sc.activated.connect(self.show_search_dialog)

            self.find_next_sc = QShortcut(QKeySequence(QKeySequence.StandardKey.FindNext), self)
            self.find_next_sc.setContext(Qt.ShortcutContext.WindowShortcut)
            self.find_next_sc.activated.connect(self.find_next)

            self.find_prev_sc = QShortcut(QKeySequence(QKeySequence.StandardKey.FindPrevious), self)
            self.find_prev_sc.setContext(Qt.ShortcutContext.WindowShortcut)
            self.find_prev_sc.activated.connect(self.find_prev)

        QTimer.singleShot(self.update_frequency_ms, self.process_pending_lines)

    def line_height(self):
        return self._font_metrics.lineSpacing()

    def write(self, text: str):
        self.pending_lines.extend(text.splitlines(False))

    def clear(self):
        self.lines.clear()
        self.pending_lines.clear()
        self.selection_start_line = None
        self.selection_end_line = None
        self.scroll_bar.setValue(0)
        self.scroll_bar.setMaximum(0)
        self.current_search_index = 0
        self.last_search_pattern = ""
        self.last_is_regex = False
        self._last_regex = None
        self.update()

    def get_text(self):
        self.flush()
        return "\n".join(self.lines)

    def process_pending_lines(self):
        # Exit early if paused - don't schedule another timer
        if self.processing_paused:
            return

        delay = self.update_frequency_ms

        if self.pending_lines:
            batch_size = min(5000, len(self.pending_lines))
            for _ in range(batch_size):
                self.lines.append(self.pending_lines.popleft())

            # self.scroll_bar.setMaximum(len(self.lines) - 1)
            self._recalc_scrollbar_limits()
            visible_lines = self.height() // self.line_height()
            self.scroll_bar.setValue(max(0, len(self.lines) - visible_lines))
            self.update()
            delay = self.update_frequency_ms // 2

        # Only schedule next processing if not paused
        QTimer.singleShot(delay, self.process_pending_lines)

    def flush(self):
        """
        Similar to process_pending_lines(),
        but does not enable the singleShot
        """
        if self.pending_lines:
            batch_size = min(5000, len(self.pending_lines))
            for _ in range(batch_size):
                self.lines.append(self.pending_lines.popleft())

            # self.scroll_bar.setMaximum(len(self.lines) - 1)
            self._recalc_scrollbar_limits()
            visible_lines = self.height() // self.line_height()
            self.scroll_bar.setValue(max(0, len(self.lines) - visible_lines))
            self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._recalc_scrollbar_limits()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font())
        line_height = self.line_height()
        visible_lines = self.height() // line_height
        start_line = self.scroll_bar.value()
        text_area_width = self.width() - self.scroll_bar.width()

        highlight_color = self.palette().highlight().color()
        text_color = self.palette().text().color()

        if self.selection_start_line is not None and self.selection_end_line is not None:
            sel_start = min(self.selection_start_line, self.selection_end_line)
            sel_end = max(self.selection_start_line, self.selection_end_line)
        else:
            sel_start = sel_end = -1

        for i in range(visible_lines):
            line_number = start_line + i
            if line_number >= len(self.lines):
                break
            y = i * line_height
            if sel_start <= line_number <= sel_end:
                painter.fillRect(0, y, text_area_width, line_height, highlight_color)

            painter.setPen(text_color)
            flags = Qt.TextFlag.TextWordWrap if self.word_wrap else Qt.TextFlag.TextSingleLine
            painter.drawText(
                0, y, text_area_width, line_height, flags | Qt.AlignmentFlag.AlignLeft, self.lines[line_number]
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            clicked_line = self.scroll_bar.value() + int(event.position().y()) // self.line_height()
            self.selection_start_line = clicked_line
            self.selection_end_line = clicked_line
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            current_line = self.scroll_bar.value() + int(event.position().y()) // self.line_height()
            self.selection_end_line = current_line
            self.update()

    def copy_selected_text(self):
        if self.selection_start_line is not None and self.selection_end_line is not None:
            start = max(0, min(self.selection_start_line, self.selection_end_line))
            end = min(len(self.lines) - 1, max(self.selection_start_line, self.selection_end_line))
            selected_text = "\n".join(self.lines[start : end + 1])
            QApplication.clipboard().setText(selected_text)

    def select_all(self):
        self.selection_start_line = 0
        self.selection_end_line = len(self.lines) - 1
        self.update()

    def _recalc_scrollbar_limits(self):
        vis = max(1, self.height() // self.line_height())
        self.scroll_bar.setMaximum(max(0, len(self.lines) - vis))

    def wheelEvent(self, event):
        # positive y => wheel up
        dy = event.angleDelta().y()
        if dy == 0:
            return
        steps = dy // 120  # 120 units per notch
        self.scroll_bar.setValue(self.scroll_bar.value() - steps * self.scroll_bar.singleStep())
        self.update()

    def keyPressEvent(self, event):
        key = event.key()
        sb = self.scroll_bar
        if key == Qt.Key.Key_Up:
            sb.setValue(sb.value() - sb.singleStep())
        elif key == Qt.Key.Key_Down:
            sb.setValue(sb.value() + sb.singleStep())
        elif key == Qt.Key.Key_PageUp:
            sb.setValue(max(sb.minimum(), sb.value() - sb.pageStep()))
        elif key == Qt.Key.Key_PageDown:
            sb.setValue(min(sb.maximum(), sb.value() + sb.pageStep()))
        elif key == Qt.Key.Key_Home:
            sb.setValue(sb.minimum())
        elif key == Qt.Key.Key_End:
            sb.setValue(sb.maximum())
        else:
            super().keyPressEvent(event)
        self.update()

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu(self)
        copy_action = menu.addAction("Copy")
        select_all_action = menu.addAction("Select All")
        find_action = menu.addAction("Find...")
        clear_action = menu.addAction("Clear")

        # action = menu.exec(event.globalPos())
        action = menu.exec(self.parent().mapToGlobal(event if isinstance(event, QPoint) else event.pos()))
        if action == copy_action:
            self.copy_selected_text()
        elif action == select_all_action:
            self.select_all()
        elif action == find_action:
            self.show_search_dialog()
        elif action == clear_action:
            self.clear()

    # ---- search helpers ----
    def _compile_regex(self, pattern: str) -> bool:
        try:
            self._last_regex = re.compile(pattern)
            return True
        except re.error as e:
            QMessageBox.warning(self, "Invalid Regex", f"{e}")
            self._last_regex = None
            return False

    def _matches(self, line: str) -> bool:
        if not self.last_search_pattern:
            return False
        if self.last_is_regex:
            return bool(self._last_regex.search(line)) if self._last_regex else False
        return self.last_search_pattern in line

    def show_search_dialog(self):
        dlg = SearchDialog(self, self.last_search_pattern, self.last_is_regex)
        ok = dlg.exec()
        pattern = dlg.input.text()
        is_regex = dlg.regex_cb.isChecked()

        if pattern:
            if is_regex:
                if not self._compile_regex(pattern):
                    return
            self.last_search_pattern = pattern
            self.last_is_regex = is_regex

        if ok:
            self.find_next()
        else:
            self.find_prev()

    def find_next(self):
        if not self.last_search_pattern:
            return -1
        # ensure compiled if regex
        if self.last_is_regex and (self._last_regex is None or self._last_regex.pattern != self.last_search_pattern):
            if not self._compile_regex(self.last_search_pattern):
                return -1

        for i in range(self.current_search_index + 1, len(self.lines)):
            if self._matches(self.lines[i]):
                self.current_search_index = i
                self.scroll_bar.setValue(i)
                self.selection_start_line = self.selection_end_line = i
                self.update()
                return i

        # no match → clear selection
        self.selection_start_line = None
        self.selection_end_line = None
        self.update()

        return -1

    def find_prev(self):
        if not self.last_search_pattern:
            return -1
        # ensure compiled if regex
        if self.last_is_regex and (self._last_regex is None or self._last_regex.pattern != self.last_search_pattern):
            if not self._compile_regex(self.last_search_pattern):
                return -1

        for i in range(self.current_search_index - 1, -1, -1):
            if self._matches(self.lines[i]):
                self.current_search_index = i
                self.scroll_bar.setValue(i)
                self.selection_start_line = self.selection_end_line = i
                self.update()
                return i

        # no match → clear selection
        self.selection_start_line = None
        self.selection_end_line = None
        self.update()

        return -1

    def pause_writes(self):
        """Pause processing of pending lines to UI. Writes to buffer continue."""
        self.processing_paused = True
        # Timer will naturally stop scheduling new singleShots

    def resume_writes(self):
        """Resume processing of pending lines to UI."""
        self.processing_paused = False
        # Restart the processing timer immediately
        QTimer.singleShot(0, self.process_pending_lines)

    def is_paused(self) -> bool:
        """Check if UI processing is paused."""
        return self.processing_paused


class CustomLargeTextView(LargeTextView):
    """
    Same as LargeTextView, but with extra context menu suitable for the NormalOutputWindow in EPIC
    """

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        device_file_exists = bool(config.device_cfg.device_file) and Path(config.device_cfg.device_file).is_file()
        rule_file_exists = bool(config.device_cfg.rule_files) and Path(config.device_cfg.rule_files[0]).is_file()
        sim_setup = device_file_exists and rule_file_exists
        #running = COORDINATOR.state in (SimState.running, SimState.timed_out)
        running = (self._parent.run_state == RUNNING) and (not self._parent.run_state == PAUSED)

        # define context menu

        menu = QMenu(self)
        copy_action = menu.addAction("Copy")
        select_all_action = menu.addAction("Select All")
        find_action = menu.addAction("Find...")
        clear_action = menu.addAction("Clear")
        menu.addSeparator()
        stop_action = menu.addAction("Stop Simulation")
        menu.addSeparator()
        open_output_action = menu.addAction("Open Normal Output Text")
        edit_rules_action = menu.addAction("Edit Production Rule File")
        edit_data_action = menu.addAction("Edit Data Output File")
        open_folder_action = menu.addAction("Open Project Folder")
        menu.addSeparator()
        quit_action = menu.addAction("Quit Application")

        # Decide Which Items Are Enabled

        find_action.setEnabled(not running)
        clear_action.setEnabled(not running)
        open_output_action.setEnabled(not running)
        open_folder_action.setEnabled(device_file_exists and not running)

        edit_data_action.setEnabled(sim_setup and not running)
        edit_rules_action.setEnabled(sim_setup and not running)

        copy_action.setEnabled(bool(self.selection_start_line or self.selection_end_line) and not running)

        stop_action.setEnabled(sim_setup and (running or self._parent.run_state == PAUSED))

        # process menu
        action = menu.exec(self.parent().mapToGlobal(event if isinstance(event, QPoint) else event.pos()))

        if action == copy_action:
            self.copy_selected_text()
        elif action == select_all_action:
            self.select_all()
        elif action == find_action:
            self.show_search_dialog()
        elif action == clear_action:
            self.clear()
        elif action == stop_action:
            self._parent.halt_simulation()
        elif action == open_output_action:
            self._parent.launchEditor(which_file="NormalOut")
        elif action == edit_rules_action:
            self._parent.launchEditor(which_file="RuleFile")
        elif action == edit_data_action:
            self._parent.launchEditor(which_file="DataFile")
        elif action == open_folder_action:
            operating_system = platform.system()
            if operating_system == "Linux":
                open_cmd = "xdg-open"
            elif operating_system == "Darwin":
                open_cmd = "open"
            elif operating_system == "Windows":
                open_cmd = "explorer"
            else:
                open_cmd = ""
                self._parent.write(f"ERROR: Opening project folder when OS=='{operating_system}' is not yet implemented!")
            if open_cmd and config.device_cfg.device_file:
                cmd = [open_cmd, str(Path(config.device_cfg.device_file).resolve().parent)]
                subprocess.run(args=cmd)
        elif action == quit_action:
            # self._parent.halt_simulation()
            self._parent.close()


if __name__ == "__main__":
    from qtpy.QtWidgets import QMainWindow, QApplication
    from qtpy.QtCore import QTimer
    import timeit
    import sys

    class LTTTestMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Large Text Viewer")

            self.viewer = CustomLargeTextView(parent=self)
            self.viewer.cache_writes = True
            self.viewer.setFixedSize(800, 600)
            self.setCentralWidget(self.viewer)

            # Delay the call to populate_text so the UI is ready.
            QTimer.singleShot(0, self.populate_text)

        def populate_text(self):
            n = 241_511
            # n = 1_000_000
            start = timeit.default_timer()
            batch_size = 10  # Number of lines per batch
            buffer = []

            for i in range(n):
                buffer.append(f"Line {i}")
                if len(buffer) >= batch_size:
                    self.viewer.write("\n".join(buffer))
                    buffer.clear()
                    QApplication.processEvents()

            if buffer:
                self.viewer.write("\n".join(buffer))
            self.viewer.cache_writes = False
            print(f"populate_text added {n} lines in {timeit.default_timer() - start} sec.")

    app = QApplication(sys.argv)
    window = LTTTestMainWindow()
    window.show()
    sys.exit(app.exec())
