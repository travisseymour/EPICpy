import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def get_app_path(app_name: str) -> Optional[str]:
    """Finds the installed application path using shutil.which()."""
    app_path = shutil.which(app_name)
    if not app_path:
        return None
    return app_path


def find_app_icon(app_name: str) -> Path | None:
    """Finds the icon file for a uv-installed app."""
    base_path = Path.home() / ".local/share/uv/tools" / app_name
    # Recursively search for icon.png inside base_path
    icon_paths = list(base_path.rglob("icon.png"))

    if icon_paths:
        return icon_paths[0]  # Return the first match
    else:
        print(f"No icon.png found in {base_path}")
        return None


def linux_desktop_entry_exists(app_name: str) -> bool:
    app_path = get_app_path(app_name)
    if not app_path:
        return False
    desktop_file = Path.home() / ".local/share/applications" / f"{app_name}.desktop"
    return desktop_file.is_file()


def create_linux_desktop_entry(app_name: str, app_title: Optional[str] = ""):
    """Creates a .desktop launcher for Linux automatically after installation."""
    app_path = get_app_path(app_name)
    if not app_path:
        return

    desktop_file = Path.home() / ".local/share/applications" / f"{app_name}.desktop"
    icon_path = find_app_icon(app_name)
    if icon_path:
        icon_path = str(icon_path.absolute())
    else:
        icon_path = ""

    desktop_content = f"""[Desktop Entry]
Name={app_title if app_title else app_name}
Exec={app_path}
Terminal=false
Type=Application
Icon={icon_path}
Categories=Utility;
"""

    desktop_file.write_text(desktop_content)
    desktop_file.chmod(0o755)  # Make executable

    # Refresh application database
    subprocess.run(["update-desktop-database", str(desktop_file.parent)], check=False)

    print(f"'{app_name}' added to Linux application launcher.")


def remove_linux_desktop_entry(app_name: str):
    """Removes the .desktop file when the app is uninstalled."""
    desktop_file = Path.home() / ".local/share/applications" / f"{app_name.lower()}.desktop"

    if desktop_file.exists():
        desktop_file.unlink()
        print(f"🗑️ Removed '{str(desktop_file.absolute())}'")

        # Refresh desktop database
        os.system("update-desktop-database ~/.local/share/applications/")
        print("Desktop database updated.")
    else:
        print(f"'{app_name}.desktop' not found, skipping removal.")
