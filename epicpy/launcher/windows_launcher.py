import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Optional

if platform.system() == "Windows":
    try:
        import win32com.client
    except ImportError:
        print("Please install the 'pywin32' package to enable Windows shortcut creation.")
        sys.exit(1)


def get_app_path(app_name: str) -> str:
    """Finds the installed application path using shutil.which()."""
    app_path = shutil.which(app_name)
    if not app_path:
        print(f"Post-Install Error: '{app_name}' not found. The command 'uv tool install {app_name}' may have failed.")
        sys.exit(1)
    return app_path


def find_app_icon(app_name: str) -> Optional[Path]:
    """
    Unlike on other OSs, the windows path to our icon is determined.
    Thus, we can return it if it exists, otherwise fail
    """
    icon_path = Path(
        Path.home(),
        "AppData",
        "Roaming",
        "uv",
        "tools",
        app_name,
        "Lib",
        "site-packages",
        app_name,
        "resources",
        "icon.ico",
    )

    if icon_path.is_file():
        return icon_path
    else:
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
    and use icon.ico (if available) as its icon.
    """
    app_path = get_app_path(app_name)
    if not app_path:
        return

    start_menu_path = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs"
    start_menu_path.mkdir(parents=True, exist_ok=True)
    shortcut_file = start_menu_path / f"{app_name}.lnk"

    icon_path = find_app_icon(app_name)
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
