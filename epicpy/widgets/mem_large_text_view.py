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

from __future__ import annotations

import bisect
import re
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import (
    QEvent,
    QPoint,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QGuiApplication,
    QKeyEvent,
    QKeySequence,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QResizeEvent,
    QShortcut,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

"""
MemLargeTextView - A text viewer backed by an in-memory deque.
"""

_MAX_SEARCH_HISTORY = 50
_search_history: list[str] = []


@dataclass
class PopupCommand:
    """A named command for the context menu."""

    callback: Callable
    enabled: bool = True


@dataclass
class Selection:
    """Represents a text selection as line/column ranges."""

    start_line: int
    start_col: int
    end_line: int
    end_col: int

    def is_empty(self) -> bool:
        return self.start_line == self.end_line and self.start_col == self.end_col

    def normalized(self) -> "Selection":
        """Return selection with start before end."""
        if self.start_line > self.end_line or (self.start_line == self.end_line and self.start_col > self.end_col):
            return Selection(self.end_line, self.end_col, self.start_line, self.start_col)
        return Selection(self.start_line, self.start_col, self.end_line, self.end_col)


class SearchDialog(QDialog):
    """
    Search dialog with editable dropdown history.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find")
        self.setModal(False)

        layout = QVBoxLayout(self)

        # Search input (editable combo with history)
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Find:"))
        self.search_input = QComboBox()
        self.search_input.setEditable(True)
        self.search_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.search_input.setMaxCount(_MAX_SEARCH_HISTORY)
        self.search_input.setMinimumWidth(300)
        self._refresh_history()
        input_layout.addWidget(self.search_input)
        layout.addLayout(input_layout)

        # Options
        options_layout = QHBoxLayout()
        self.case_sensitive = QCheckBox("Case sensitive")
        self.regex_mode = QCheckBox("Regex")
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.regex_mode)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.find_next_btn = QPushButton("Find Next")
        self.find_prev_btn = QPushButton("Find Previous")
        self.close_btn = QPushButton("Close")
        button_layout.addWidget(self.find_prev_btn)
        button_layout.addWidget(self.find_next_btn)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)

        self.close_btn.clicked.connect(self.hide)
        line_edit = self.search_input.lineEdit()
        if line_edit:
            line_edit.returnPressed.connect(self.find_next_btn.click)

    def _refresh_history(self):
        """Rebuild dropdown items from the module-level history."""
        current = self.search_input.currentText()
        self.search_input.blockSignals(True)
        self.search_input.clear()
        for term in _search_history:
            self.search_input.addItem(term)
        self.search_input.setCurrentText(current)
        self.search_input.blockSignals(False)

    def add_to_history(self, term: str):
        """Record a search term in session history and refresh the dropdown."""
        term = term.strip()
        if not term:
            return
        # Move to front if already present
        if term in _search_history:
            _search_history.remove(term)
        _search_history.insert(0, term)
        # Enforce max size
        del _search_history[_MAX_SEARCH_HISTORY:]
        self._refresh_history()

    def get_search_text(self) -> str:
        return self.search_input.currentText()

    def is_case_sensitive(self) -> bool:
        return self.case_sensitive.isChecked()

    def is_regex(self) -> bool:
        return self.regex_mode.isChecked()


class GoToLineDialog(QDialog):
    """Dialog to jump to a specific line."""

    def __init__(self, max_line: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Go to Line")
        self.setModal(True)

        layout = QVBoxLayout(self)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel(f"Line number (1-{max_line}):"))
        self.line_input = QLineEdit()
        self.line_input.setMinimumWidth(150)
        input_layout.addWidget(self.line_input)
        layout.addLayout(input_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.line_input.returnPressed.connect(self.accept)

    def get_line_number(self) -> Optional[int]:
        try:
            return int(self.line_input.text())
        except ValueError:
            return None


class MemLargeTextView(QAbstractScrollArea):
    """
    Text viewer backed by an in-memory deque.

    Supports write() to append text and load() to adopt an existing deque.
    Renders only visible lines for efficiency.
    """

    # Signals
    content_changed = Signal(int)  # line count after change

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        commands: Optional[dict[str, Callable]] = None,
    ):
        super().__init__(parent)

        # Custom commands for context menu: wrap bare callables into PopupCommand
        self._commands: dict[str, PopupCommand] = {name: PopupCommand(callback=cb) for name, cb in (commands or {}).items()}

        # Memory storage - double buffer system
        self._write_buffer: deque[str] = deque()  # Temp buffer where writes go
        self._partial_text: str = ""  # Buffer for text without trailing newline
        self._lines: deque[str] = deque()  # Display buffer that paintEvent draws from

        # Display settings
        # self._font = QFont("Monospace", 12)
        self._font = QApplication.instance().font()
        self._font.setStyleHint(QFont.StyleHint.Monospace)
        self._font_metrics: Optional[QFontMetrics] = None
        self._line_height: int = 0
        self._char_width: int = 0
        self._update_font_metrics()

        # Colors
        self._bg_color = QColor(255, 255, 255)
        self._text_color = QColor(0, 0, 0)
        self._selection_bg = QColor(51, 153, 255, 100)
        self._selection_text = QColor(0, 0, 0)
        self._line_number_bg = QColor(240, 240, 240)
        self._line_number_color = QColor(128, 128, 128)
        self._search_highlight = QColor(255, 255, 0, 180)

        # Line numbers
        self._show_line_numbers = True
        self._line_number_width = 60

        # Selection state
        self._selection: Optional[Selection] = None
        self._is_selecting = False
        self._selection_anchor_line = 0
        self._selection_anchor_col = 0

        # Search state
        self._search_matches: list[tuple[int, int, int]] = []  # (line, start_col, end_col)
        self._current_match_index = -1
        self._search_dialog: Optional[SearchDialog] = None

        # Search cache for fast searching (joined text + char offsets)
        self._search_text: Optional[str] = None  # Cached "\n".join(lines)
        self._char_offsets: list[int] = []  # Character offset for start of each line

        # Horizontal scroll
        self._max_line_width = 0
        self._horizontal_offset = 0

        # Setup
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.viewport().setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Enable mouse tracking for selection
        self.viewport().setMouseTracking(True)

        # Progress bar (shown during search index building)
        self._progress_bar = QProgressBar(self.viewport())
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFixedHeight(20)
        self._progress_bar.hide()

        # Keyboard shortcuts
        self._setup_shortcuts()

        # Apply initial theme
        self.update_theme()

    def _setup_shortcuts(self):
        """
        Setup keyboard shortcuts.
        """
        ctx = Qt.ShortcutContext.WidgetWithChildrenShortcut

        # Ctrl+C - Copy
        copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        copy_shortcut.setContext(ctx)
        copy_shortcut.activated.connect(self.copy_selection)

        # Ctrl+A - Select all
        select_all_shortcut = QShortcut(QKeySequence.StandardKey.SelectAll, self)
        select_all_shortcut.setContext(ctx)
        select_all_shortcut.activated.connect(self.select_all)

        # Ctrl+F - Find
        find_shortcut = QShortcut(QKeySequence.StandardKey.Find, self)
        find_shortcut.setContext(ctx)
        find_shortcut.activated.connect(self.show_search_dialog)

        # Ctrl+G - Go to line
        goto_shortcut = QShortcut(QKeySequence("Ctrl+G"), self)
        goto_shortcut.setContext(ctx)
        goto_shortcut.activated.connect(self.show_goto_dialog)

        # F3 - Find next
        find_next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F3), self)
        find_next_shortcut.setContext(ctx)
        find_next_shortcut.activated.connect(self.find_next)

        # Shift+F3 - Find previous
        find_prev_shortcut = QShortcut(QKeySequence("Shift+F3"), self)
        find_prev_shortcut.setContext(ctx)
        find_prev_shortcut.activated.connect(self.find_previous)

        # Escape - Clear selection / close search
        esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc_shortcut.setContext(ctx)
        esc_shortcut.activated.connect(self._handle_escape)

    def update_theme(self):
        """
        Update colors based on the current system color scheme (dark/light mode)."""
        try:
            scheme = QGuiApplication.styleHints().colorScheme()
            is_dark = scheme == Qt.ColorScheme.Dark
        except AttributeError:
            # Fallback for older Qt versions
            is_dark = False

        if is_dark:
            # Dark mode colors (matching qdarkstyle)
            self._bg_color = QColor(25, 35, 45)  # #19232D
            self._text_color = QColor(224, 225, 227)  # #E0E1E3
            self._selection_bg = QColor(52, 103, 146, 150)  # #346792
            self._selection_text = QColor(224, 225, 227)
            self._line_number_bg = QColor(50, 65, 75)  # #32414B
            self._line_number_color = QColor(148, 150, 152)  # #949698
            self._search_highlight = QColor(255, 200, 0, 150)
        else:
            # Light mode colors
            self._bg_color = QColor(255, 255, 255)
            self._text_color = QColor(0, 0, 0)
            self._selection_bg = QColor(51, 153, 255, 100)
            self._selection_text = QColor(0, 0, 0)
            self._line_number_bg = QColor(240, 240, 240)
            self._line_number_color = QColor(128, 128, 128)
            self._search_highlight = QColor(255, 255, 0, 180)

        self.viewport().update()

    def changeEvent(self, event: QEvent):
        """Handle theme change events."""
        if event.type() == QEvent.Type.PaletteChange:
            self.update_theme()
        super().changeEvent(event)

    def _update_font_metrics(self):
        """Update cached font metrics."""
        self._font_metrics = QFontMetrics(self._font)
        self._line_height = self._font_metrics.height()
        self._char_width = self._font_metrics.horizontalAdvance("M")

    def set_font(self, font: QFont):
        """Set the display font (should be monospace)."""
        self._font = font
        self._update_font_metrics()
        self._update_scrollbars()
        self.viewport().update()

    def font(self) -> QFont:
        return self._font

    def set_show_line_numbers(self, show: bool):
        """Show or hide line numbers."""
        self._show_line_numbers = show
        self._update_line_number_width()
        self.viewport().update()

    def _update_line_number_width(self):
        """Calculate width needed for line numbers."""
        line_count = len(self._lines)
        if not self._show_line_numbers or line_count == 0:
            self._line_number_width = 0
            return
        digits = len(str(line_count))
        self._line_number_width = self._char_width * (digits + 2) + 10

    # -------------------------------------------------------------------------
    # Memory Loading / Writing
    # -------------------------------------------------------------------------

    def load(self, lines: deque[str]):
        """
        Extend the widget's display buffer with lines from another deque.
        The provided lines are appended to existing displayed content.
        """
        self._lines += lines
        self._on_content_changed()

    def write(self, text: str):
        """
        Append text to the write buffer.
        """
        if not text:
            return

        # Prepend any buffered partial text
        if self._partial_text:
            text = self._partial_text + text
            self._partial_text = ""

        # Split keeping line endings to identify partial lines
        lines = text.splitlines(keepends=True)

        for line in lines:
            if line.endswith(("\n", "\r")):
                # Complete line - strip the line ending and add to write buffer
                self._write_buffer.append(line.rstrip("\r\n"))
            else:
                # Partial line (no newline at end) - buffer it
                self._partial_text = line

    def flush(self):
        """
        Flush any partial text to the write buffer. Does not update the display (call update_display() for that).
        """
        if self._partial_text:
            self._write_buffer.append(self._partial_text)
            self._partial_text = ""

    def update_display(self):
        """
        Transfer all content from the write buffer to the display buffer
        and refresh the display. Flushes any partial text first.
        """
        # First flush any partial text to write buffer
        self.flush()

        # Transfer write buffer to display buffer
        if self._write_buffer:
            self._lines += self._write_buffer
            self._write_buffer.clear()

        self._on_content_changed()

    def _on_content_changed(self):
        """Handle content changes - update display."""
        self._selection = None
        self._search_matches = []
        self._current_match_index = -1
        self._max_line_width = 0
        self._horizontal_offset = 0

        # Invalidate search cache
        self._search_text = None
        self._char_offsets = []

        self._update_line_number_width()
        self._update_scrollbars()
        self.viewport().update()

        self.content_changed.emit(len(self._lines))

    def clear(self):
        """
        Clear all content from both write buffer and display buffer.
        """
        self._write_buffer.clear()
        self._partial_text = ""
        self._lines.clear()
        self._on_content_changed()

    def save(self, file: str | Path) -> bool:
        """
        Save all text to the specified file.
        Returns True if save succeeded, False otherwise.
        """
        try:
            path = Path(file) if isinstance(file, str) else file
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(f"{line}\n" for line in self._lines)
            return True
        except OSError:
            return False

    def line_count(self) -> int:
        return len(self._lines)

    @property
    def lines(self) -> deque[str]:
        return self._lines

    def get_text(self) -> str:
        """
        Return all content as a single string."""
        if self._search_text is not None:
            return self._search_text
        return "\n".join(self._lines)

    # -------------------------------------------------------------------------
    # Line Access
    # -------------------------------------------------------------------------

    def _get_line(self, line_num: int) -> str:
        """Get text for a line (0-indexed)."""
        if line_num < 0 or line_num >= len(self._lines):
            return ""
        return self._lines[line_num]

    def _get_lines_range(self, start_line: int, count: int) -> list[str]:
        """Get multiple lines."""
        lines = []
        for i in range(start_line, min(start_line + count, len(self._lines))):
            lines.append(self._lines[i])
        return lines

    # -------------------------------------------------------------------------
    # Scrolling
    # -------------------------------------------------------------------------

    def _update_scrollbars(self):
        line_count = len(self._lines)
        if line_count == 0:
            self.verticalScrollBar().setRange(0, 0)
            self.horizontalScrollBar().setRange(0, 0)
            return

        visible_lines = self._visible_line_count()
        max_scroll = max(0, line_count - visible_lines)
        self.verticalScrollBar().setRange(0, max_scroll)
        self.verticalScrollBar().setPageStep(visible_lines)

        # Horizontal scrollbar
        text_area_width = self._text_area_width()
        if self._max_line_width > text_area_width:
            self.horizontalScrollBar().setRange(0, self._max_line_width - text_area_width)
            self.horizontalScrollBar().setPageStep(text_area_width)
        else:
            self.horizontalScrollBar().setRange(0, 0)

    def _visible_line_count(self) -> int:
        if self._line_height == 0:
            return 0
        return self.viewport().height() // self._line_height

    def _text_area_width(self) -> int:
        return self.viewport().width() - self._line_number_width

    def _first_visible_line(self) -> int:
        return self.verticalScrollBar().value()

    def scroll_to_line(self, line_num: int):
        line_count = len(self._lines)
        line_idx = max(0, min(line_num - 1, line_count - 1))
        visible = self._visible_line_count()

        # Center the line if possible
        target = max(0, line_idx - visible // 2)
        self.verticalScrollBar().setValue(target)

    def scroll_to_bottom(self):
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self._update_scrollbars()
        # Reposition progress bar if visible
        if self._progress_bar.isVisible():
            self._show_search_progress_bar()

    def scrollContentsBy(self, dx: int, dy: int):
        """Handle scroll events."""
        self._horizontal_offset = self.horizontalScrollBar().value()
        self.viewport().update()

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel scrolling."""
        delta = event.angleDelta().y()
        if delta != 0:
            lines = -delta // 40  # ~3 lines per scroll notch
            new_val = self.verticalScrollBar().value() + lines
            self.verticalScrollBar().setValue(new_val)
        event.accept()

    # -------------------------------------------------------------------------
    # Painting
    # -------------------------------------------------------------------------

    def paintEvent(self, event: QPaintEvent):
        line_count = len(self._lines)
        if line_count == 0:
            # Draw empty background
            painter = QPainter(self.viewport())
            painter.fillRect(0, 0, self.viewport().width(), self.viewport().height(), self._bg_color)
            return

        painter = QPainter(self.viewport())
        painter.setFont(self._font)

        vp = self.viewport()
        vp_width = vp.width()
        vp_height = vp.height()

        # Background
        painter.fillRect(0, 0, vp_width, vp_height, self._bg_color)

        # Line number background
        if self._show_line_numbers and self._line_number_width > 0:
            painter.fillRect(0, 0, self._line_number_width, vp_height, self._line_number_bg)

        first_line = self._first_visible_line()
        visible_count = self._visible_line_count() + 2  # +2 for partial lines

        text_x = self._line_number_width - self._horizontal_offset
        selection = self._selection.normalized() if self._selection else None

        # Track max width for horizontal scroll
        max_width_seen = self._max_line_width

        for i in range(visible_count):
            line_idx = first_line + i
            if line_idx >= line_count:
                break

            y = i * self._line_height
            text_y = y + self._font_metrics.ascent()

            # Get line text
            line_text = self._get_line(line_idx)
            line_width = self._font_metrics.horizontalAdvance(line_text)
            max_width_seen = max(max_width_seen, line_width + self._line_number_width + 20)

            # Draw line number
            if self._show_line_numbers:
                painter.setPen(self._line_number_color)
                line_num_str = str(line_idx + 1)
                num_x = self._line_number_width - self._font_metrics.horizontalAdvance(line_num_str) - 8
                painter.drawText(num_x, text_y, line_num_str)

            # Draw selection background
            if selection and not selection.is_empty():
                self._draw_selection_for_line(painter, line_idx, line_text, y, text_x, selection)

            # Draw search highlights
            self._draw_search_highlights_for_line(painter, line_idx, line_text, y, text_x)

            # Draw text
            painter.setPen(self._text_color)
            painter.drawText(text_x, text_y, line_text)

        # Update max line width if changed
        if max_width_seen > self._max_line_width:
            self._max_line_width = max_width_seen
            self._update_scrollbars()

    def _draw_selection_for_line(
        self,
        painter: QPainter,
        line_idx: int,
        line_text: str,
        y: int,
        text_x: int,
        selection: Selection,
    ):
        """Draw selection highlight for a line."""
        if line_idx < selection.start_line or line_idx > selection.end_line:
            return

        line_len = len(line_text)

        if line_idx == selection.start_line and line_idx == selection.end_line:
            # Selection within single line
            start_col = min(selection.start_col, line_len)
            end_col = min(selection.end_col, line_len)
        elif line_idx == selection.start_line:
            start_col = min(selection.start_col, line_len)
            end_col = line_len
        elif line_idx == selection.end_line:
            start_col = 0
            end_col = min(selection.end_col, line_len)
        else:
            # Entire line selected
            start_col = 0
            end_col = line_len

        if start_col >= end_col and line_idx != selection.end_line:
            end_col = line_len  # Select to end of line

        # Calculate pixel positions
        x1 = text_x + self._font_metrics.horizontalAdvance(line_text[:start_col])
        x2 = text_x + self._font_metrics.horizontalAdvance(line_text[:end_col])

        # Draw highlight rectangle
        painter.fillRect(x1, y, x2 - x1, self._line_height, self._selection_bg)

    def _draw_search_highlights_for_line(self, painter: QPainter, line_idx: int, line_text: str, y: int, text_x: int):
        for match_line, start_col, end_col in self._search_matches:
            if match_line != line_idx:
                continue

            x1 = text_x + self._font_metrics.horizontalAdvance(line_text[:start_col])
            x2 = text_x + self._font_metrics.horizontalAdvance(line_text[:end_col])
            painter.fillRect(x1, y, x2 - x1, self._line_height, self._search_highlight)

    # -------------------------------------------------------------------------
    # Selection
    # -------------------------------------------------------------------------

    def _pos_to_line_col(self, pos: QPoint) -> tuple[int, int]:
        """
        Convert viewport position to line/column.
        """
        line_count = len(self._lines)
        if line_count == 0:
            return 0, 0

        line_idx = self._first_visible_line() + pos.y() // self._line_height
        line_idx = max(0, min(line_idx, line_count - 1))

        text_x = pos.x() - self._line_number_width + self._horizontal_offset
        if text_x < 0:
            return line_idx, 0

        line_text = self._get_line(line_idx)
        # Find column by measuring character widths
        col = 0
        for i, char in enumerate(line_text):
            char_width = self._font_metrics.horizontalAdvance(line_text[: i + 1])
            if char_width > text_x:
                # Check if closer to this char or next
                prev_width = self._font_metrics.horizontalAdvance(line_text[:i])
                if text_x - prev_width < char_width - text_x:
                    col = i
                else:
                    col = i + 1
                break
            col = i + 1

        return line_idx, col

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and len(self._lines) > 0:
            line, col = self._pos_to_line_col(event.position().toPoint())
            self._selection_anchor_line = line
            self._selection_anchor_col = col
            self._selection = Selection(line, col, line, col)
            self._is_selecting = True
            self.viewport().update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_selecting and len(self._lines) > 0:
            line, col = self._pos_to_line_col(event.position().toPoint())
            self._selection = Selection(self._selection_anchor_line, self._selection_anchor_col, line, col)
            self.viewport().update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_selecting = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Select word on double-click."""
        if event.button() == Qt.MouseButton.LeftButton and len(self._lines) > 0:
            line, col = self._pos_to_line_col(event.position().toPoint())
            line_text = self._get_line(line)

            # Find word boundaries
            start = col
            end = col
            while start > 0 and line_text[start - 1].isalnum():
                start -= 1
            while end < len(line_text) and line_text[end].isalnum():
                end += 1

            self._selection = Selection(line, start, line, end)
            self.viewport().update()
        super().mouseDoubleClickEvent(event)

    def select_all(self):
        """Select all text."""
        line_count = len(self._lines)
        if line_count > 0:
            last_line = line_count - 1
            last_col = len(self._get_line(last_line))
            self._selection = Selection(0, 0, last_line, last_col)
            self.viewport().update()

    def clear_selection(self):
        """Clear the current selection."""
        self._selection = None
        self.viewport().update()

    def get_selected_text(self) -> str:
        """Get the currently selected text."""
        if not self._selection or self._selection.is_empty():
            return ""

        sel = self._selection.normalized()
        lines = []

        for line_idx in range(sel.start_line, sel.end_line + 1):
            line_text = self._get_line(line_idx)

            if line_idx == sel.start_line and line_idx == sel.end_line:
                lines.append(line_text[sel.start_col : sel.end_col])
            elif line_idx == sel.start_line:
                lines.append(line_text[sel.start_col :])
            elif line_idx == sel.end_line:
                lines.append(line_text[: sel.end_col])
            else:
                lines.append(line_text)

        return "\n".join(lines)

    def copy_selection(self):
        """Copy selected text to clipboard."""
        text = self.get_selected_text()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    def show_search_dialog(self):
        """Show the search dialog."""
        if not self._search_dialog:
            self._search_dialog = SearchDialog(self)
            self._search_dialog.find_next_btn.clicked.connect(self.find_next)
            self._search_dialog.find_prev_btn.clicked.connect(self.find_previous)
        self._search_dialog.show()
        self._search_dialog.search_input.setFocus()
        line_edit = self._search_dialog.search_input.lineEdit()
        if line_edit:
            line_edit.selectAll()

    def find_next(self):
        """Find next occurrence of search text."""
        if not self._search_dialog:
            return

        search_text = self._search_dialog.get_search_text()
        if not search_text:
            return

        self._do_search(search_text, forward=True)

    def find_previous(self):
        """Find previous occurrence of search text."""
        if not self._search_dialog:
            return

        search_text = self._search_dialog.get_search_text()
        if not search_text:
            return

        self._do_search(search_text, forward=False)

    def _show_search_progress_bar(self):
        vp = self.viewport()
        bar_width = min(400, vp.width() - 40)
        x = (vp.width() - bar_width) // 2
        y = (vp.height() - 20) // 2
        self._progress_bar.setGeometry(x, y, bar_width, 20)
        self._progress_bar.setValue(0)
        self._progress_bar.setFormat("Building search index... %p%")
        self._progress_bar.show()
        QApplication.processEvents()

    def _ensure_search_cache(self):
        """
        Build search cache if not already built. Shows progress bar.
        """
        if self._search_text is not None:
            return  # Already cached

        line_count = len(self._lines)
        if line_count == 0:
            self._search_text = ""
            self._char_offsets = []
            return

        # Show progress bar for large content
        show_progress = line_count > 10000
        if show_progress:
            self._show_search_progress_bar()

        # Build character offset index
        self._char_offsets = []
        offset = 0
        update_interval = max(line_count // 100, 10000)  # Update every 1% or 10K lines
        last_update = 0

        for i, line in enumerate(self._lines):
            self._char_offsets.append(offset)
            offset += len(line) + 1  # +1 for newline

            # Update progress bar periodically
            if show_progress and i - last_update >= update_interval:
                progress = int((i / line_count) * 90)  # Reserve 10% for join
                self._progress_bar.setValue(progress)
                QApplication.processEvents()
                last_update = i

        # Show "Finalizing..." phase
        if show_progress:
            self._progress_bar.setValue(90)
            self._progress_bar.setFormat("Joining text...")
            QApplication.processEvents()

        # Join all lines into a single string
        self._search_text = "\n".join(self._lines)

        # Done
        if show_progress:
            self._progress_bar.hide()

    def _char_offset_to_line_col(self, char_offset: int) -> tuple[int, int]:
        """
        Convert character offset in joined text to (line_idx, col).
        """
        if not self._char_offsets:
            return 0, 0

        line_idx = bisect.bisect_right(self._char_offsets, char_offset) - 1
        line_idx = max(0, min(line_idx, len(self._lines) - 1))
        col = char_offset - self._char_offsets[line_idx]

        return line_idx, col

    def _do_search(self, search_text: str, forward: bool = True):
        line_count = len(self._lines)
        if line_count == 0:
            return

        # Record search term in history
        if self._search_dialog:
            self._search_dialog.add_to_history(search_text)

        # Ensure search cache is built
        self._ensure_search_cache()

        if self._search_text is None:
            return

        case_sensitive = self._search_dialog.is_case_sensitive() if self._search_dialog else False
        is_regex = self._search_dialog.is_regex() if self._search_dialog else False

        # Determine starting character offset
        if self._selection:
            sel = self._selection.normalized()
            if forward:
                # Start after current selection
                start_char = self._char_offsets[sel.end_line] + sel.end_col
            else:
                # Start before current selection
                start_char = self._char_offsets[sel.start_line] + sel.start_col
        else:
            # Start from first visible line
            first_line = self._first_visible_line()
            start_char = self._char_offsets[first_line] if first_line < line_count else 0

        # Prepare search
        text_to_search = self._search_text
        if not case_sensitive and not is_regex:
            text_to_search = self._search_text.lower()
            search_text = search_text.lower()

        found_char = -1
        match_len = len(search_text)

        if is_regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(search_text, flags)
            except re.error:
                return  # Invalid regex

            if forward:
                # Search from start_char to end, then wrap to beginning
                match = pattern.search(self._search_text, start_char)
                if match is None and start_char > 0:
                    match = pattern.search(self._search_text, 0, start_char)
                if match:
                    found_char = match.start()
                    match_len = match.end() - match.start()
            else:
                # Search backward: find last match before start_char
                # Then wrap to find last match after start_char
                last_match = None
                for m in pattern.finditer(self._search_text, 0, start_char):
                    last_match = m
                if last_match is None:
                    # Wrap: find last match after start_char
                    for m in pattern.finditer(self._search_text, start_char):
                        last_match = m
                if last_match:
                    found_char = last_match.start()
                    match_len = last_match.end() - last_match.start()
        else:
            # Literal search
            if forward:
                found_char = text_to_search.find(search_text, start_char)
                if found_char == -1 and start_char > 0:
                    # Wrap around
                    found_char = text_to_search.find(search_text, 0, start_char)
            else:
                # Backward search
                found_char = text_to_search.rfind(search_text, 0, start_char)
                if found_char == -1:
                    # Wrap around
                    found_char = text_to_search.rfind(search_text, start_char)

        if found_char >= 0:
            # Convert character offset to line/column
            found_line, found_start = self._char_offset_to_line_col(found_char)
            found_end = found_start + match_len

            # Select the found text
            self._selection = Selection(found_line, found_start, found_line, found_end)
            self.scroll_to_line(found_line + 1)

            # Update search highlights
            self._search_matches = [(found_line, found_start, found_end)]
            self.viewport().update()

    def clear_search(self):
        self._search_matches = []
        self._current_match_index = -1
        self.viewport().update()

    # -------------------------------------------------------------------------
    # Go to Line
    # -------------------------------------------------------------------------

    def show_goto_dialog(self):
        line_count = len(self._lines)
        if line_count == 0:
            return

        dialog = GoToLineDialog(line_count, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            line_num = dialog.get_line_number()
            if line_num and 1 <= line_num <= line_count:
                self.scroll_to_line(line_num)
                # Select the line
                line_text = self._get_line(line_num - 1)
                self._selection = Selection(line_num - 1, 0, line_num - 1, len(line_text))
                self.viewport().update()

    # -------------------------------------------------------------------------
    # Keyboard Navigation
    # -------------------------------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_Home:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.verticalScrollBar().setValue(0)
            else:
                self._horizontal_offset = 0
                self.horizontalScrollBar().setValue(0)
                self.viewport().update()

        elif key == Qt.Key.Key_End:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

        elif key == Qt.Key.Key_PageUp:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - self._visible_line_count())

        elif key == Qt.Key.Key_PageDown:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + self._visible_line_count())

        elif key == Qt.Key.Key_Up:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - 1)

        elif key == Qt.Key.Key_Down:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + 1)

        elif key == Qt.Key.Key_Left:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - self._char_width * 4)

        elif key == Qt.Key.Key_Right:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + self._char_width * 4)

        else:
            super().keyPressEvent(event)

    def _handle_escape(self):
        if self._search_dialog and self._search_dialog.isVisible():
            self._search_dialog.hide()
            self.clear_search()
        elif self._selection:
            self.clear_selection()

    # -------------------------------------------------------------------------
    # Context Menu
    # -------------------------------------------------------------------------

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        line_count = len(self._lines)

        # Copy action
        copy_action = menu.addAction("Copy")
        copy_action.setShortcut("Ctrl+C")
        copy_action.setEnabled(self._selection is not None and not self._selection.is_empty())
        copy_action.triggered.connect(self.copy_selection)

        # Select All action
        select_all_action = menu.addAction("Select All")
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.setEnabled(line_count > 0)
        select_all_action.triggered.connect(self.select_all)

        menu.addSeparator()

        # Find action
        find_action = menu.addAction("Find...")
        find_action.setShortcut("Ctrl+F")
        find_action.setEnabled(line_count > 0)
        find_action.triggered.connect(self.show_search_dialog)

        # Find Next action
        find_next_action = menu.addAction("Find Next")
        find_next_action.setShortcut("F3")
        find_next_action.setEnabled(line_count > 0 and self._search_dialog is not None)
        find_next_action.triggered.connect(self.find_next)

        # Find Previous action
        find_prev_action = menu.addAction("Find Previous")
        find_prev_action.setShortcut("Shift+F3")
        find_prev_action.setEnabled(line_count > 0 and self._search_dialog is not None)
        find_prev_action.triggered.connect(self.find_previous)

        menu.addSeparator()

        # Go to Line action
        goto_action = menu.addAction("Go to Line...")
        goto_action.setShortcut("Ctrl+G")
        goto_action.setEnabled(line_count > 0)
        goto_action.triggered.connect(self.show_goto_dialog)

        menu.addSeparator()

        # Toggle line numbers
        line_numbers_action = menu.addAction("Show Line Numbers")
        line_numbers_action.setCheckable(True)
        line_numbers_action.setChecked(self._show_line_numbers)
        line_numbers_action.triggered.connect(self._toggle_line_numbers)

        # Custom commands
        if self._commands:
            menu.addSeparator()
            for name, cmd in self._commands.items():
                action = menu.addAction(name)
                action.setEnabled(cmd.enabled)
                action.triggered.connect(cmd.callback)

        menu.exec(event.globalPos())

    def enable_command(self, name: str, enabled: bool = True):
        """
        Enable or disable a single custom command by name.
        """
        if name in self._commands:
            self._commands[name].enabled = enabled

    def enable_commands(self, names: list[str]):
        for name in names:
            if name in self._commands:
                self._commands[name].enabled = True

    def disable_commands(self, names: list[str]):
        for name in names:
            if name in self._commands:
                self._commands[name].enabled = False

    def enable_all_commands(self):
        for cmd in self._commands.values():
            cmd.enabled = True

    def disable_all_commands(self):
        for cmd in self._commands.values():
            cmd.enabled = False

    def set_commands(self, commands: dict[str, Callable]):
        """
        Set up custom commands for the context menu. Note that this replaces any existing commands.
        Use this when commands need to reference the widget itself
        (which isn't available at construction time).
        """
        self._commands = {name: PopupCommand(callback=cb) for name, cb in commands.items()}

    def _toggle_line_numbers(self):
        self.set_show_line_numbers(not self._show_line_numbers)


# =============================================================================
# Main entry point for testing
# =============================================================================

if __name__ == "__main__":
    import sys
    import time
    from pathlib import Path

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("MemLargeTextView Test")
            self.resize(988, 800)

            # Deque to hold file content (separate from widget)
            self._file_deque: deque[str] = deque()

            # Create viewer with commands
            self.viewer = MemLargeTextView(
                self,
                commands={
                    "Read large_output.txt": self._read_file,
                    "Load text into widget": self._load_into_widget,
                    "Quit": self.close,
                },
            )
            self.setCentralWidget(self.viewer)

            # Initially disable "Load text into widget" until file is read
            self.viewer.disable_commands(["Load text into widget"])

            # Connect signals
            self.viewer.content_changed.connect(self._on_content_changed)

            # Add some initial content
            self.viewer.write("Right-click to access commands.\n")
            self.viewer.write("1. 'Read large_output.txt' - reads file into memory\n")
            self.viewer.write("2. 'Load text into widget' - loads the deque into the viewer\n")

        def _read_file(self):
            """Read large_output.txt into self._file_deque."""
            file_path = Path(__file__).parent / "large_output.txt"
            if not file_path.exists():
                self.viewer.clear()
                self.viewer.write(f"File not found: {file_path}\n")
                return

            self.setWindowTitle("Reading file...")
            QApplication.processEvents()

            start_time = time.perf_counter()

            self._file_deque.clear()
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    self._file_deque.append(line.rstrip("\n\r"))

            elapsed = time.perf_counter() - start_time

            self.viewer.clear()
            self.viewer.write(f"Read {len(self._file_deque):,} lines in {elapsed:.3f} seconds.\n")
            self.viewer.write("Now use 'Load text into widget' to test load() performance.\n")
            self.setWindowTitle(f"MemLargeTextView Test - {len(self._file_deque):,} lines in deque")

            # Enable the load command
            self.viewer.enable_commands(["Load text into widget"])

        def _load_into_widget(self):
            """Load self._file_deque into the viewer."""
            if len(self._file_deque) == 0:
                self.viewer.write("No data in deque. Read a file first.\n")
                return

            self.setWindowTitle("Loading into widget...")
            QApplication.processEvents()

            start_time = time.perf_counter()
            self.viewer.load(self._file_deque)
            elapsed = time.perf_counter() - start_time

            print(f"Loaded {len(self._file_deque):,} lines in {elapsed:.3f} seconds")
            self.setWindowTitle(f"MemLargeTextView Test - {len(self._file_deque):,} lines loaded in {elapsed:.3f}s")

        def _on_content_changed(self, _line_count: int):
            pass  # Title is set elsewhere for timing info

    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
