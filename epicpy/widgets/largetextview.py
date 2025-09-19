from __future__ import annotations

import platform
import subprocess
import re
import sys
from itertools import islice
from pathlib import Path
from typing import List, Deque, Optional, Tuple

from qtpy.QtCore import QTimer, QRect
from qtpy import QtGui
from qtpy.QtWidgets import (
    QWidget,
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
    QApplication,
)
from collections import deque

from qtpy.QtCore import Qt, QPoint
from qtpy.QtGui import (
    QColor,
    QPainter,
    QFontMetrics,
    QFont,
    QContextMenuEvent,
    QKeySequence,
    QShortcut,
)

from epicpy.constants.stateconstants import RUNNING, PAUSED
from epicpy.utils import config

from epiclibcpp.epiclib.output_tee_globals import Exception_out


class SearchDialog(QDialog):
    def __init__(self, parent=None, start_text: str = "",
                 start_is_regex: bool = False, start_case_sensitive: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Find")
        v = QVBoxLayout(self)

        row = HBox()
        row.addWidget(QLabel("Find:"))
        self.input = QLineEdit(self)
        self.input.setText(start_text)
        row.addWidget(self.input)
        v.addLayout(row)

        self.regex_cb = QCheckBox("Regex", self)
        self.regex_cb.setChecked(start_is_regex)
        v.addWidget(self.regex_cb)

        self.case_cb = QCheckBox("Case Sensitive", self)
        self.case_cb.setChecked(start_case_sensitive)
        v.addWidget(self.case_cb)

        btns = HBox()
        self.prev_button = QPushButton("Find Prev", self)
        self.next_button = QPushButton("Find Next", self)
        btns.addWidget(self.prev_button)
        btns.addWidget(self.next_button)
        v.addLayout(btns)

        # normal button connections
        self.next_button.clicked.connect(self.accept)
        self.prev_button.clicked.connect(self.reject)

        # pressing the ENTER button in the input field acts like pressing "Find Next"
        self.input.returnPressed.connect(self.accept)




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

        # storage
        self.lines: List[str] = []
        self.pending_lines: Deque[str] = deque()

        # timing
        self.update_frequency_ms = int(update_frequency_ms)
        self.wait_msg_limit = int(wait_msg_limit)
        self.processing_paused = False
        QTimer.singleShot(self.update_frequency_ms, self.process_pending_lines)

        # font/metrics
        font = QFont("Courier New" if sys.platform == "win32" else "Courier", 14)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self._fm = QFontMetrics(self.font())

        # layout & scrollbars
        self.word_wrap = False  # keep default as before
        self.scroll_bar = QScrollBar(Qt.Orientation.Vertical, self)
        self.scroll_bar.setPageStep(page_step_lines)
        self.scroll_bar.valueChanged.connect(self.update)
        self.h_scroll = QScrollBar(Qt.Orientation.Horizontal, self)
        self.h_scroll.valueChanged.connect(self.update)
        self.scroll_bar.raise_()
        self.h_scroll.raise_()

        # longest line width tracking for H-scroll when wrap is off
        self._max_px_width = 0

        # selection (character-accurate)
        self.sel_anchor: Optional[Tuple[int, int]] = None  # (line, col)
        self.sel_caret: Optional[Tuple[int, int]] = None   # (line, col)

        # search state
        self.last_search_pattern: str = ""
        self.last_is_regex: bool = False
        self._last_regex: Optional[re.Pattern] = None
        self.current_search_index: int = -1
        self.last_case_sensitive: bool = False

        # focus & shortcuts
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scroll_bar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.h_scroll.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        if enable_shortcuts:
            sc = QShortcut(QKeySequence(QKeySequence.StandardKey.Copy), self)
            sc.setContext(Qt.ShortcutContext.WindowShortcut)
            sc.activated.connect(self.copy_selected_text)

            sca = QShortcut(QKeySequence(QKeySequence.StandardKey.SelectAll), self)
            sca.setContext(Qt.ShortcutContext.WindowShortcut)
            sca.activated.connect(self.select_all)

            sf = QShortcut(QKeySequence(QKeySequence.StandardKey.Find), self)
            sf.setContext(Qt.ShortcutContext.WindowShortcut)
            sf.activated.connect(self.show_search_dialog)

            sfn = QShortcut(QKeySequence(QKeySequence.StandardKey.FindNext), self)
            sfn.setContext(Qt.ShortcutContext.WindowShortcut)
            sfn.activated.connect(self.find_next)

            sfp = QShortcut(QKeySequence(QKeySequence.StandardKey.FindPrevious), self)
            sfp.setContext(Qt.ShortcutContext.WindowShortcut)
            sfp.activated.connect(self.find_prev)

    # ---------------- public API ----------------
    def line_height(self) -> int:
        return self._fm.lineSpacing()

    def write(self, text: str):
        self.pending_lines.extend(text.splitlines(False))

    def clear(self):
        self.lines.clear()
        self.pending_lines.clear()
        self._max_px_width = 0
        self.sel_anchor = self.sel_caret = None
        self.last_search_pattern = ""
        self._last_regex = None
        self.last_is_regex = False
        self.current_search_index = -1
        self.scroll_bar.setValue(0)
        self.scroll_bar.setMaximum(0)
        self.h_scroll.setValue(0)
        self.h_scroll.setMaximum(0)
        self.update()

    def get_text(self) -> str:
        self.flush()
        return "\n".join(self.lines)

    def process_pending_lines(self):
        if self.processing_paused:
            return
        delay = self.update_frequency_ms
        if self.pending_lines:
            n = min(5000, len(self.pending_lines))
            # pop many items quickly
            batch = list(islice(self.pending_lines, 0, n))
            for _ in range(n):
                self.pending_lines.popleft()
            self._append_batch(batch)
            delay = max(1, self.update_frequency_ms // 2)
        QTimer.singleShot(delay, self.process_pending_lines)

    def flush(self):
        """Drain *all* pending lines (fix #2)."""
        while self.pending_lines:
            n = min(5000, len(self.pending_lines))
            batch = list(islice(self.pending_lines, 0, n))
            for _ in range(n):
                self.pending_lines.popleft()
            self._append_batch(batch)

    # ---------------- internals ----------------
    def _append_batch(self, batch: List[str]) -> None:
        if not batch:
            return
        self.lines.extend(batch)
        if not self.word_wrap:
            fm = self._fm
            for s in batch:
                w = fm.horizontalAdvance(s)
                if w > self._max_px_width:
                    self._max_px_width = w
        self._recalc_scrollbar_limits()
        if self._should_follow_tail():
            self._scroll_to_bottom()
        self.update()

    @staticmethod
    def _should_follow_tail() -> bool:
        # maintains previous behavior: always stick to bottom in streaming mode
        return True

    def _visible_lines(self) -> int:
        horiz_bar_h = self.h_scroll.sizeHint().height() if self.h_scroll.isVisible() else 0
        return max(1, (self.height() - horiz_bar_h) // self.line_height())

    def _scroll_to_bottom(self):
        vis = self._visible_lines()
        self.scroll_bar.setValue(max(0, len(self.lines) - vis))

    def _recalc_scrollbar_limits(self):
        vis = self._visible_lines()
        self.scroll_bar.setMaximum(max(0, len(self.lines) - vis))
        if self.word_wrap:
            self.h_scroll.setMaximum(0)
            self.h_scroll.hide()
        else:
            vbar_w = self.scroll_bar.sizeHint().width()
            margin = self._fm.averageCharWidth() * 2
            usable_w = max(0, self.width() - vbar_w)
            max_x = max(0, self._max_px_width - usable_w)
            self.h_scroll.setMaximum(max(0, max_x + margin))
            self.h_scroll.show()

    # ---------------- events ----------------
    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
        super().resizeEvent(ev)
        vbar_w = self.scroll_bar.sizeHint().width()
        hbar_h = self.h_scroll.sizeHint().height()

        # Reserve bottom row for hbar, right column for vbar
        content_w = max(0, self.width() - vbar_w)
        content_h = max(0, self.height() - hbar_h)

        # Vertical bar on the RIGHT edge, full height minus hbar
        self.scroll_bar.setGeometry(self.width() - vbar_w, 0, vbar_w, content_h)
        # Horizontal bar on the BOTTOM, full width minus vbar
        self.h_scroll.setGeometry(0, self.height() - hbar_h, content_w, hbar_h)

        self._recalc_scrollbar_limits()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font())
        painter.setClipRect(event.rect())

        lh = self.line_height()
        first = self.scroll_bar.value()
        count = self._visible_lines()

        # Use sizeHint so the bar is always the right width even when manually placed
        vbar_w = self.scroll_bar.sizeHint().width()
        text_w = max(0, self.width() - vbar_w)
        x_offset = -self.h_scroll.value() if not self.word_wrap else 0

        highlight_color = self.palette().highlight().color()
        text_color = self.palette().text().color()

        # search highlight color (semi-transparent)
        search_bg = QColor(highlight_color)
        search_bg.setAlpha(120)

        # selection map by line
        sel_ranges = self._selection_ranges_normalized()

        for row in range(count):
            i = first + row
            if i >= len(self.lines):
                break
            y = row * lh
            line = self.lines[i]

            # selection fill
            for c0, c1 in sel_ranges.get(i, ()):  # may be multiple spans
                lpx = self._text_x_from_col(line, c0)
                rpx = self._text_x_from_col(line, c1)
                painter.fillRect(QRect(lpx + x_offset, y, max(1, rpx - lpx), lh), highlight_color)

            # search matches fill (fix #5)
            if self.last_search_pattern:
                for m0, m1 in self._match_spans(line):
                    lpx = self._text_x_from_col(line, m0)
                    rpx = self._text_x_from_col(line, m1)
                    painter.fillRect(QRect(lpx + x_offset, y, max(1, rpx - lpx), lh), search_bg)

            # draw text
            painter.setPen(text_color)
            flags = Qt.TextFlag.TextWordWrap if self.word_wrap else Qt.TextFlag.TextSingleLine
            painter.drawText(0 + x_offset, y, text_w, lh, flags | Qt.AlignmentFlag.AlignLeft, line)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            line = self.scroll_bar.value() + int(event.position().y()) // self.line_height()
            if 0 <= line < len(self.lines):
                col = self._col_from_x(self.lines[line], int(event.position().x()) + self.h_scroll.value())
                self.sel_anchor = (line, col)
                self.sel_caret = (line, col)
                self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            line = self.scroll_bar.value() + int(event.position().y()) // self.line_height()
            line = max(0, min(len(self.lines) - 1, line))
            col = self._col_from_x(self.lines[line], int(event.position().x()) + self.h_scroll.value())
            self.sel_caret = (line, col)
            self.update()

    # keyboard & wheel remain the same behavior
    def wheelEvent(self, event):
        dy = event.angleDelta().y()
        if dy:
            steps = dy // 120
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

    # context menu & actions
    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu(self)
        copy_action = menu.addAction("Copy")
        select_all_action = menu.addAction("Select All")
        find_action = menu.addAction("Find...")
        clear_action = menu.addAction("Clear")

        action = menu.exec(self.parent().mapToGlobal(event if isinstance(event, QPoint) else event.pos()))

        if action == copy_action:
            self.copy_selected_text()
        elif action == select_all_action:
            self.select_all()
        elif action == find_action:
            self.show_search_dialog()
        elif action == clear_action:
            self.clear()

    # ------------ search helpers (fix #1 & #5) ------------
    def _compile_regex(self, pattern: str, case_sensitive: bool) -> bool:
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            self._last_regex = re.compile(pattern, flags)
            return True
        except re.error as e:
            QMessageBox.warning(
                self,
                "Invalid Regex",
                f"{e}",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Ok,
            )
            self._last_regex = None
            return False

    def _match_spans(self, line: str) -> List[Tuple[int, int]]:
        if not self.last_search_pattern:
            return []

        if self.last_is_regex and self._last_regex is not None:
            return [(m.start(), m.end()) for m in self._last_regex.finditer(line)]

        # literal find spans
        spans: List[Tuple[int, int]] = []
        pat = self.last_search_pattern
        src = line if self.last_case_sensitive else line.lower()
        pat_cmp = pat if self.last_case_sensitive else pat.lower()
        start = 0
        while True:
            idx = src.find(pat_cmp, start)
            if idx == -1:
                break
            spans.append((idx, idx + len(pat)))
            start = idx + max(1, len(pat))
        return spans

    def _matches(self, line: str) -> bool:
        return bool(self._match_spans(line))

    def show_search_dialog(self):
        dlg = SearchDialog(self, self.last_search_pattern,
                           self.last_is_regex, self.last_case_sensitive)
        ok = dlg.exec()
        pattern = dlg.input.text()
        is_regex = dlg.regex_cb.isChecked()
        case_sensitive = dlg.case_cb.isChecked()

        changed = ((pattern and pattern != self.last_search_pattern) or
                   (is_regex != self.last_is_regex) or
                   (case_sensitive != self.last_case_sensitive))

        if pattern:
            if is_regex:
                if not self._compile_regex(pattern, case_sensitive):
                    return
            else:
                self._last_regex = None
            self.last_search_pattern = pattern
            self.last_is_regex = is_regex
            self.last_case_sensitive = case_sensitive

        if changed:
            # reset start: after selection if present; otherwise -1 or end
            if self.sel_caret is not None:
                self.current_search_index = self.sel_caret[0]
            else:
                self.current_search_index = -1 if ok else len(self.lines)

        if ok:
            self.find_next()
        else:
            self.find_prev()

    def _ensure_visible(self, line_idx):
        vis = self._visible_lines()
        target = max(0, min(line_idx - vis // 2, len(self.lines) - vis))
        self.scroll_bar.setValue(target)

    def find_next(self):
        if not self.last_search_pattern:
            return -1
        if self.last_is_regex and (self._last_regex is None or self._last_regex.pattern != self.last_search_pattern):
            if not self._compile_regex(self.last_search_pattern, self.last_case_sensitive):
                return -1
        start = self.current_search_index
        for i in range(start + 1, len(self.lines)):
            if self._matches(self.lines[i]):
                self.current_search_index = i
                self._ensure_visible(i)
                self._select_whole_line(i)
                self.update()
                return i
        for i in range(0, max(0, start + 1)):
            if self._matches(self.lines[i]):
                self.current_search_index = i
                self._ensure_visible(i)
                self._select_whole_line(i)
                self.update()
                return i
        self._clear_selection()
        self.update()
        return -1

    def find_prev(self):
        if not self.last_search_pattern:
            return -1
        if self.last_is_regex and (self._last_regex is None or self._last_regex.pattern != self.last_search_pattern):
            if not self._compile_regex(self.last_search_pattern, self.last_case_sensitive):
                return -1
        start = len(self.lines) if self.current_search_index < 0 else self.current_search_index
        for i in range(start - 1, -1, -1):
            if self._matches(self.lines[i]):
                self.current_search_index = i
                self._ensure_visible(i)
                self._select_whole_line(i)
                self.update()
                return i
        for i in range(len(self.lines) - 1, start - 1, -1):
            if self._matches(self.lines[i]):
                self.current_search_index = i
                self._ensure_visible(i)
                self._select_whole_line(i)
                self.update()
                return i
        self._clear_selection()
        self.update()
        return -1

    # selection utilities
    def _clear_selection(self):
        self.sel_anchor = None
        self.sel_caret = None

    def _select_whole_line(self, i: int):
        line = self.lines[i]
        self.sel_anchor = (i, 0)
        self.sel_caret = (i, len(line))

    def _selection_ranges_normalized(self) -> dict[int, List[Tuple[int, int]]]:
        if not self.sel_anchor or not self.sel_caret:
            return {}
        (l0, c0), (l1, c1) = self.sel_anchor, self.sel_caret
        if (l1, c1) < (l0, c0):
            (l0, c0), (l1, c1) = (l1, c1), (l0, c0)
        ranges: dict[int, List[Tuple[int, int]]] = {}
        for li in range(l0, l1 + 1):
            line = self.lines[li]
            if l0 == l1:
                a, b = c0, c1
            elif li == l0:
                a, b = c0, len(line)
            elif li == l1:
                a, b = 0, c1
            else:
                a, b = 0, len(line)
            a = max(0, min(len(line), a))
            b = max(0, min(len(line), b))
            if a != b:
                ranges.setdefault(li, []).append((a, b))
        return ranges

    def _selected_text(self) -> str:
        ranges = self._selection_ranges_normalized()
        if not ranges:
            return ""
        parts: List[str] = []
        for i in sorted(ranges):
            line = self.lines[i]
            spans = ranges[i]
            out = []
            for a, b in spans:
                out.append(line[a:b])
            parts.append("".join(out))
        return "\n".join(parts)

    def copy_selected_text(self):
        txt = self._selected_text()
        if txt:
            QApplication.clipboard().setText(txt)

    def select_all(self):
        if not self.lines:
            return
        last = len(self.lines) - 1
        self.sel_anchor = (0, 0)
        self.sel_caret = (last, len(self.lines[last]))
        self.update()

    # ---- column/x mapping ----
    def _col_from_x(self, line: str, x_view_px: int) -> int:
        if not line:
            return 0
        fm = self._fm
        if x_view_px <= 0:
            return 0
        if x_view_px >= fm.horizontalAdvance(line):
            return len(line)
        lo, hi = 0, len(line)
        while lo < hi:
            mid = (lo + hi) // 2
            w = fm.horizontalAdvance(line[:mid])
            if w <= x_view_px:
                lo = mid + 1
            else:
                hi = mid
        return max(0, lo - 1)

    def _text_x_from_col(self, line: str, col: int) -> int:
        col = max(0, min(len(line), col))
        return self._fm.horizontalAdvance(line[:col])

    # ---- pause/resume (unchanged) ----
    def pause_writes(self):
        self.processing_paused = True

    def resume_writes(self):
        self.processing_paused = False
        QTimer.singleShot(0, self.process_pending_lines)

    def is_paused(self):
        return self.processing_paused



class CustomLargeTextView(LargeTextView):
    """
    Same as LargeTextView, but with extra context menu suitable for the NormalOutputWindow in EPIC
    """

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        device_file_exists = (
            bool(config.device_cfg.device_file)
            and Path(config.device_cfg.device_file).is_file()
        )
        rule_file_exists = (
            bool(config.device_cfg.rule_files)
            and Path(config.device_cfg.rule_files[0]).is_file()
        )
        sim_setup = device_file_exists and rule_file_exists
        # running = COORDINATOR.state in (SimState.running, SimState.timed_out)
        running = (self._parent.run_state == RUNNING) and (
            not self._parent.run_state == PAUSED
        )

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

        copy_action.setEnabled(
            (
                    self.sel_anchor is not None and self.sel_caret is not None
            )
            and not running
        )

        stop_action.setEnabled(
            sim_setup and (running or self._parent.run_state == PAUSED)
        )

        # process menu
        action = menu.exec(
            self.parent().mapToGlobal(
                event if isinstance(event, QPoint) else event.pos()
            )
        )

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
                msg = f"ERROR: Opening project folder when OS=='{operating_system}' is not yet implemented!"
                try:
                    Exception_out(msg)
                except Exception:
                    print(msg)
            if open_cmd and config.device_cfg.device_file:
                cmd = [
                    open_cmd,
                    str(Path(config.device_cfg.device_file).resolve().parent),
                ]
                subprocess.run(args=cmd)
        elif action == quit_action:
            # self._parent.halt_simulation()
            self._parent.close()


if __name__ == "__main__":
    from qtpy.QtWidgets import QMainWindow

    # from qtpy.QtCore import QTimer
    import timeit
    # import sys

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("LargeTextView Demo")
            self.resize(800, 600)

            central = QWidget(self)
            layout = QVBoxLayout(central)

            self.view = LargeTextView()

            layout.addWidget(self.view)
            self.setCentralWidget(central)

            # self.content = Path("temp_text_choice_100_output.txt").read_text().splitlines()
            self.content = (
                Path(
                    "/home/nogard/Dropbox/Documents/EPICSTUFF/EPICLib_fullbindings/epiclib_flat/devices/covert_warning/data_output.csv"
                )
                .read_text()
                .splitlines()
            )
            # Simulate real-time appending
            self.counter = 1
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.append_line)
            self.start = timeit.default_timer()
            self.timer.start(0)

        def append_line(self):
            try:
                aline = self.content[self.counter]
                self.view.write(aline)
                self.counter += 1
            except Exception as e:
                extra = f' ({e})' if e else ''
                self.timer.stop()
                self.view.write(
                    f"Time Elapsed: {timeit.default_timer() - self.start:0.5f} sec.{extra}"
                )

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
