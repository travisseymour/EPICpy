import shutil
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QMessageBox


def get_app_path(app_name: str) -> str:
    """Finds the installed application path using shutil.which()."""
    app_path = shutil.which(app_name)
    if not app_path:
        print(f"Post-Install Error: '{app_name}' not found. The command 'uv tool install {app_name}' may have failed.")
        sys.exit(1)
    return app_path


def find_app_icon(app_name: str) -> Optional[Path]:
    """Finds the icon file for a uv-installed app (expects icon.icns)."""
    base_path = Path.home() / ".local/share/uv/tools" / app_name
    icon_paths = list(base_path.rglob("icon.icns"))
    if icon_paths:
        return icon_paths[0]
    else:
        print(f"No icon.icns found in {base_path}")
        return None


def macos_launcher_exists(app_name: str) -> bool:
    """Checks if a macOS app bundle already exists in the Applications or user Desktop folder."""
    app_bundles = (Path.home() / "Desktop" / f"{app_name}.app", Path("/Applications") / f"{app_name}.app")
    return any(bundle.exists() for bundle in app_bundles)


def create_macos_app_launcher(app_name: str, app_title: Optional[str] = ""):
    """
    Creates a simple macOS application bundle launcher on the user's Desktop folder.
    The bundle structure is:
        ~/Desktop/<app_name>.app/
            Contents/
                Info.plist
                MacOS/
                    <app_name>  (a wrapper executable script)
                Resources/
                    icon.icns (if available)
    """
    app_path = get_app_path(app_name)
    if not app_path:
        return

    # Define bundle paths
    app_bundle = Path.home() / "Desktop" / f"{app_name}.app"
    contents_dir = app_bundle / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"

    # Create necessary directories
    macos_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)

    # Handle icon: If an icon.icns exists, copy it as icon.icns.
    icon_path = find_app_icon(app_name)
    if icon_path:
        target_icon = resources_dir / "icon.icns"
        shutil.copy(str(icon_path), str(target_icon))
        icon_file_entry = "icon.icns"
    else:
        icon_file_entry = ""

    # Create Info.plist
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{app_title if app_title else app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{app_title if app_title else app_name}</string>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.uvtools.{app_name}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>"""
    if icon_file_entry:
        plist_content += f"""
    <key>CFBundleIconFile</key>
    <string>{icon_file_entry}</string>"""
    plist_content += """
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
"""
    info_plist_path = contents_dir / "Info.plist"
    info_plist_path.write_text(plist_content)

    # Create the executable launcher script
    launcher_script = macos_dir / app_name
    launcher_script_content = f"""#!/bin/sh
exec "{app_path}" "$@"
"""
    launcher_script.write_text(launcher_script_content)
    launcher_script.chmod(0o755)

    QMessageBox.information(
        None,
        "Launcher Application Created Successfully",
        f"{app_title} launcher application was added successfully to your Desktop.\n"
        "Consider moving it to your Applications folder.",
        QMessageBox.StandardButton.Ok,
    )


def remove_macos_app_launcher(app_name: str):
    """Removes the macOS application bundle launcher from the user's Desktop, or the  Applications folder."""
    app_bundles = (
        Path.home() / "Desktop" / f"{app_name}.app",
        Path("/Applications") / f"{app_name}.app",
        Path.home() / "Applications" / f"{app_name}.app",
    )

    for app_bundle in app_bundles:
        try:
            shutil.rmtree(app_bundle)
        except:
            ...

    if macos_launcher_exists(app_name):
        QMessageBox.information(
            None,
            "Launcher Application Removal Failed.",
            f"{app_name} launcher application was not removed successfully. "
            f"You can remove it manually by dragging it to the Trash.\n",
            QMessageBox.StandardButton.Ok,
        )
    else:
        QMessageBox.information(
            None,
            "Launcher Application Removed Successfully",
            f"The {app_name} launcher application was removed successfully.",
            QMessageBox.StandardButton.Ok,
        )
