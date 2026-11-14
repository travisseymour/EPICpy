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

import os
import platform
import shutil
from importlib.resources import as_file, files
from pathlib import Path
from typing import Optional

if platform.system() == "Windows":
    try:
        import win32com.client
    except ImportError:
        print("Please install the 'pywin32' package to enable Windows shortcut creation.")


def get_app_path(app_name: str) -> Optional[str]:
    """Finds the installed application path using shutil.which()."""
    app_path = shutil.which(app_name)
    if not app_path:
        return None
    return app_path


def find_app_icon() -> Optional[Path]:
    """Finds the icon file from the installed epicpy package resources."""
    try:
        # First try to find .ico file for Windows
        icon_resource = files("epicpy").joinpath("resources", "images", "appicon", "icon.ico")
        with as_file(icon_resource) as icon_path:
            if icon_path.is_file():
                return Path(icon_path).resolve()
    except Exception:
        pass

    try:
        # Fall back to PNG (Windows can use PNG for shortcuts too)
        icon_resource = files("epicpy").joinpath("resources", "images", "appicon", "icon_256.png")
        with as_file(icon_resource) as icon_path:
            if icon_path.is_file():
                return Path(icon_path).resolve()
    except Exception:
        pass
    return None


def windows_shortcut_exists(app_name: str) -> bool:
    """Checks if a Windows shortcut already exists in the Start Menu."""
    start_menu_path = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs"
    shortcut_file = start_menu_path / f"{app_name}.lnk"
    return shortcut_file.exists()


def create_windows_shortcut(app_name: str, app_title: Optional[str] = ""):
    """
    Creates a Windows shortcut (.lnk) in the current user's Start Menu Programs folder.

    The shortcut will point to the installed application's executable (found via get_app_path)
    and use Icon.ico (if available) as its Icon.
    """
    app_path = get_app_path(app_name)
    if not app_path:
        return

    start_menu_path = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs"
    start_menu_path.mkdir(parents=True, exist_ok=True)
    shortcut_file = start_menu_path / f"{app_name}.lnk"

    icon_path = find_app_icon()
    if icon_path:
        icon_path = str(icon_path.absolute())
    else:
        icon_path = ""  # If no icon is found, Windows will default to the app's icon.

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_file))
    shortcut.Targetpath = app_path
    shortcut.WorkingDirectory = str(Path(app_path).parent)
    shortcut.IconLocation = icon_path if icon_path else app_path
    shortcut.Description = app_title if app_title else app_name
    shortcut.save()

    print(f"'{app_name}' added to the Windows Start Menu as a launcher.")


def remove_windows_shortcut(app_name: str):
    """Removes the Windows shortcut (.lnk) from the Start Menu when the app is uninstalled."""
    start_menu_path = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs"
    shortcut_file = start_menu_path / f"{app_name}.lnk"

    if shortcut_file.exists():
        shortcut_file.unlink()
        print(f"Removed '{str(shortcut_file.absolute())}'")
    else:
        print(f"'{app_name}.lnk' not found, skipping removal.")
