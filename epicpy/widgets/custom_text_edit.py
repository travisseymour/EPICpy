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

"""
CustomQTextEdit - A QTextEdit with write() and flush() methods for stream compatibility,
plus a custom command system for the context menu.
"""

import re
from dataclasses import dataclass
from typing import Callable, Optional

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextEdit, QWidget

_HTML_TAG_RE = re.compile(r"<[a-zA-Z][^>]*>")


@dataclass
class PopupCommand:
    """A named command for the context menu."""

    callback: Callable
    enabled: bool = True


class CustomQTextEdit(QTextEdit):
    """QTextEdit subclass that can be used as a file-like output stream."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        commands: Optional[dict[str, Callable]] = None,
    ):
        super().__init__(parent)

        # Custom commands for context menu
        self._commands: dict[str, PopupCommand] = {name: PopupCommand(callback=cb) for name, cb in (commands or {}).items()}

    def write(self, text: str, move_to_end: bool = True):
        """Append text to the widget. Enables use as a file-like object."""
        if "<" in text and _HTML_TAG_RE.search(text):
            self.append(text)
            if move_to_end:
                self.moveCursor(QTextCursor.MoveOperation.End)
                self.ensureCursorVisible()
        else:
            # Use insertPlainText at end to avoid paragraph spacing from append()
            self.moveCursor(QTextCursor.MoveOperation.End)
            self.insertPlainText(text)
            if move_to_end:
                self.ensureCursorVisible()

    def flush(self):
        """No-op for stream compatibility."""
        ...

    def move_to_end(self):
        # Scroll to the bottom
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.ensureCursorVisible()

    """
    ====================
    Context Menu Methods
    ====================
    """

    def contextMenuEvent(self, event):
        """Show context menu with standard actions and custom commands."""
        menu = self.createStandardContextMenu()

        # Custom commands
        if self._commands:
            menu.addSeparator()
            for name, cmd in self._commands.items():
                action = menu.addAction(name)
                action.setEnabled(cmd.enabled)
                action.triggered.connect(cmd.callback)

        menu.exec(event.globalPos())

    def enable_command(self, name: str, enabled: bool = True):
        """Enable or disable a single custom command by name."""
        if name in self._commands:
            self._commands[name].enabled = enabled

    def enable_commands(self, names: list[str]):
        """Enable the named custom commands."""
        for name in names:
            if name in self._commands:
                self._commands[name].enabled = True

    def disable_commands(self, names: list[str]):
        """Disable the named custom commands."""
        for name in names:
            if name in self._commands:
                self._commands[name].enabled = False

    def enable_all_commands(self):
        """Enable all custom commands."""
        for cmd in self._commands.values():
            cmd.enabled = True

    def disable_all_commands(self):
        """Disable all custom commands."""
        for cmd in self._commands.values():
            cmd.enabled = False

    def set_commands(self, commands: dict[str, Callable]):
        """
        Set up custom commands for the context menu.

        Replaces any existing commands. Use this when commands need to
        reference the widget itself (which isn't available at construction time).
        """
        self._commands = {name: PopupCommand(callback=cb) for name, cb in commands.items()}
