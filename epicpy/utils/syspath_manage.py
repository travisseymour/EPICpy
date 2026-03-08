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

from __future__ import annotations

import atexit
import os
import sys
from typing import Optional

# plugin_syspath.py
"""
Manage a single active plugin directory on sys.path.

Typical usage (host side):

    import plugin_syspath as psp

    psp.set_active_plugin_path(plugin_dir)
    # now plugin code can do `import screenmetrics` from that directory

This module is intentionally global-stateful: only one plugin directory is kept
active at a time. On interpreter shutdown, the active directory is removed.
"""

# The currently active plugin path (normalized absolute path), or None.
_active_plugin_path: Optional[str] = None

# Tracks whether the currently active plugin path was inserted by *this* module.
# This prevents us from removing a path the application inserted independently.
_active_installed_by_us: bool = False


def _normalize_path(path: str) -> str:
    """
    Normalize a path for stable comparisons:
    - expand ~
    - make absolute
    - normalize separators and up-level references
    - realpath to resolve symlinks
    """
    expanded = os.path.expanduser(path)
    absolute = os.path.abspath(expanded)
    normalized = os.path.normpath(absolute)
    resolved = os.path.realpath(normalized)
    return resolved


def _remove_path_from_syspath(path: str) -> bool:
    """
    Remove *all* occurrences of `path` from sys.path.
    Returns True if anything was removed.
    """
    removed_any = False
    # Remove duplicates safely by looping until gone.
    while True:
        try:
            sys.path.remove(path)
            removed_any = True
        except ValueError:
            break
    return removed_any


def _install_path_on_syspath(path: str) -> None:
    """
    Install `path` at the front of sys.path if not already present.
    """
    if path not in sys.path:
        sys.path.insert(0, path)


def set_active_plugin_path(plugin_dir: str) -> None:
    """
    Make `plugin_dir` the active plugin directory on sys.path.
    - If `plugin_dir` is the same as the currently active path (after normalization),
      do nothing.
    - Otherwise, remove the currently active plugin path from sys.path (only if this
      module installed it), then install the new one and store it as active.
    """
    global _active_plugin_path, _active_installed_by_us

    if not plugin_dir or not plugin_dir.strip():
        raise ValueError("plugin_dir must be a non-empty path")

    new_path = _normalize_path(plugin_dir)

    if not os.path.exists(new_path):
        raise FileNotFoundError(new_path)
    if not os.path.isdir(new_path):
        raise NotADirectoryError(new_path)

    # Idempotent: same plugin path => nothing to do.
    if _active_plugin_path == new_path:
        return

    # Remove old path if we installed it.
    if _active_plugin_path is not None and _active_installed_by_us:
        _remove_path_from_syspath(_active_plugin_path)

    # Install new path and record it.
    _install_path_on_syspath(new_path)
    _active_plugin_path = new_path
    _active_installed_by_us = True


def clear_active_plugin_path() -> None:
    """
    Remove the active plugin directory from sys.path if this module installed it.
    Clears the active tracking regardless.
    """
    global _active_plugin_path, _active_installed_by_us

    if _active_plugin_path is not None and _active_installed_by_us:
        _remove_path_from_syspath(_active_plugin_path)

    _active_plugin_path = None
    _active_installed_by_us = False


def get_active_plugin_path() -> Optional[str]:
    """
    Return the currently active plugin directory (normalized absolute path),
    or None if no active path is set.
    """
    return _active_plugin_path


@atexit.register
def _cleanup_at_exit() -> None:
    """
    Ensure we don't leave a plugin directory on sys.path at interpreter shutdown.
    """
    # Only remove what we installed.
    clear_active_plugin_path()
