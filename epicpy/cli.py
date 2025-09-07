import argparse
import platform
from rich.console import Console

from epicpy.launcher.linux_launcher import linux_desktop_entry_exists, remove_linux_desktop_entry
from epicpy.launcher.macos_launcher import macos_launcher_exists, remove_macos_app_launcher
from epicpy.launcher.windows_launcher import windows_shortcut_exists, remove_windows_shortcut

_console = Console()


def do_cleanup(app_name: str) -> int:
    """Remove app launcher/shortcut for the current OS. Return 0 on success."""
    system = platform.system()
    try:
        if system == "Linux":
            if linux_desktop_entry_exists(app_name):
                remove_linux_desktop_entry(app_name)
                _console.print(f"[green]Removed Linux desktop entry for '{app_name}'.[/green]")
            else:
                _console.print(f"[yellow]No Linux desktop entry found for '{app_name}'.[/yellow]")
        elif system == "Darwin":
            if macos_launcher_exists(app_name):
                remove_macos_app_launcher(app_name)
                _console.print(f"[green]Removed macOS launcher for '{app_name}'.[/green]")
            else:
                _console.print(f"[yellow]No macOS launcher found for '{app_name}'.[/yellow]")
        elif system == "Windows":
            if windows_shortcut_exists(app_name):
                remove_windows_shortcut(app_name)
                _console.print(f"[green]Removed Windows shortcut for '{app_name}'.[/green]")
            else:
                _console.print(f"[yellow]No Windows shortcut found for '{app_name}'.[/yellow]")
        else:
            _console.print(f"[red]Unsupported OS: {system}[/red]")
            return 2
        return 0
    except Exception as e:
        _console.print(f"[red]Unable to cleanup application launcher:[/red] {e}")
        return 1


def build_parser(__version__: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="epicpy", description="EPICpy command-line interface")
    if __version__ is not None:
        parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (sets EPICPY_DEBUG=1 for this process).",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # cleanup subcommand
    p_clean = subparsers.add_parser("cleanup", help="Remove application launcher/shortcut.")
    p_clean.add_argument(
        "--name",
        default="epicpy",
        help="Application name used by the launcher/shortcut (default: %(default)s).",
    )

    return parser
