#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "rich>=13.7",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.markup import escape

console = Console()

"""
Converts .ui files to .py for PySide6 or PyQt6, but only recompiles files that changed
(so git history stays clean).

Usage examples:
  python ui_build.py
  python ui_build.py --qt pyside6
  python ui_build.py --qt pyqt6
"""

# ----------------------------- helpers -----------------------------


def detect_qt_type(preferred: str | None = None) -> str:
    """
    Decide which binding to use.
    Priority:
      1) --qt flag if provided
      2) EPICPY_QT env var if set to pyside6/pyqt6
      3) Try to import PySide6, then PyQt6
    """
    if preferred in {"pyside6", "pyqt6"}:
        return preferred

    env_qt = os.environ.get("EPICPY_QT", "").strip().lower()
    if env_qt in {"pyside6", "pyqt6"}:
        return env_qt

    try:
        import PySide6  # noqa: F401

        return "pyside6"
    except Exception:
        pass

    try:
        import PyQt6  # noqa: F401

        return "pyqt6"
    except Exception:
        pass

    raise RuntimeError("Neither PySide6 nor PyQt6 is available.")


def resolve_uic_command(qt_type: str) -> Tuple[List[str], str]:
    """
    Return (base_command_list, human_readable_name) for running the converter.
    Prefers the CLI tool on PATH; falls back to `python -m ...` if not found.
    """
    if qt_type == "pyside6":
        tool = "pyside6-uic"
        if shutil.which(tool):
            return [tool], tool
        # fall back to module runner
        return [
            sys.executable,
            "-m",
            "PySide6.scripts.pyside6_uic",
        ], "python -m PySide6.scripts.pyside6_uic"

    # qt_type == "pyqt6"
    tool = "pyuic6"
    if shutil.which(tool):
        return [tool], tool
    # fall back to module runner
    return [sys.executable, "-m", "PyQt6.uic.pyuic"], "python -m PyQt6.uic.pyuic"


def needs_rebuild(ui: Path, py: Path) -> bool:
    return (not py.is_file()) or (ui.stat().st_mtime > py.stat().st_mtime)


def run_uic(cmd: List[str], ui: Path, py: Path) -> bool:
    """
    Execute the UI compiler. Returns True on success.
    """
    full_cmd = [*cmd, str(ui.resolve()), "-o", str(py.resolve())]
    proc = subprocess.run(
        full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if proc.returncode == 0:
        return True
    # show error details
    console.print(f"[bold red]ERROR:[/bold red] {escape(' '.join(full_cmd))}")
    if proc.stdout.strip():
        console.print("[red]stdout:[/red]\n" + proc.stdout)
    if proc.stderr.strip():
        console.print("[red]stderr:[/red]\n" + proc.stderr)
    return False


# ----------------------------- main -----------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile .ui files to .py (only if changed)."
    )
    parser.add_argument(
        "--qt", choices=["pyside6", "pyqt6"], help="Force binding (auto if omitted)."
    )
    parser.add_argument(
        "--dir", default=".", help="Directory to scan for .ui files (default: .)"
    )
    args = parser.parse_args()

    try:
        qt_type = detect_qt_type(args.qt)
    except Exception as e:
        console.print(f"[bold red]Cannot detect Qt binding:[/bold red] {e}")
        return 2

    cmd, cmd_name = resolve_uic_command(qt_type)

    root = Path(args.dir).resolve()
    ui_files: List[Path] = sorted(root.glob("*.ui"))

    if not ui_files:
        console.print("[bold yellow]No .ui files found… nothing to do.[/bold yellow]")
        return 0

    console.print(f"[bold yellow]Using {qt_type} ({cmd_name})[/bold yellow]")
    console.print(
        f"[bold yellow]Checking {len(ui_files)} .ui files for potential changes…[/bold yellow]"
    )

    changed_any = False
    for ui in ui_files:
        py = ui.with_suffix(".py")
        if needs_rebuild(ui, py):
            changed_any = True
            console.print(f"[cyan]Converting {ui.name} → {py.name}[/cyan]")
            ok = run_uic(cmd, ui, py)
            if ok:
                console.print("[green]\tSuccess![/green]")
            else:
                console.print("[bold red]\tFailed.[/bold red]")

    if not changed_any:
        console.print("[bold yellow]All files up to date. Nothing done.[/bold yellow]")

    console.print("[bold yellow]Finished.[/bold yellow]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
