from __future__ import annotations

from importlib.metadata import (
    version as _dist_version,
    PackageNotFoundError,
    packages_distributions,
)

from typing import Optional
import os
import sys
from pathlib import Path
import faulthandler
import signal

from rich.console import Console

EPICPY_DEBUG = os.environ.get("EPICPY_DEBUG", "").lower() in (
    "1",
    "true",
    "yes",
    "debug",
)
if EPICPY_DEBUG:
    print("EPICPY_DEBUG mode is enabled")

_console = Console()


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@  SETUP VERSION ACCESS @@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


def _dist_name_for(package: str) -> str:
    # Map import package -> distribution name (handles dash/underscore differences)
    top = package.split(".")[0]
    return packages_distributions().get(top, [top])[0]


def _read_pyproject_version(start: Path) -> Optional[str]:
    cand = Path(__file__).parent.parent / "pyproject.toml"
    if cand.is_file():
        try:
            try:
                import tomllib as toml  # Python 3.11+
            except ModuleNotFoundError:  # Python 3.10
                import tomli as toml  # pip install tomli for dev/runtime
            with cand.open("rb") as fh:
                data = toml.load(fh)
            v = (data.get("project") or {}).get("version")
            if isinstance(v, str) and v.strip():
                return v.strip()
        except Exception:
            # Ignore and fall through
            pass
    _console.print("[red]UNABLE TO READ PYPROJECT VERSION![/red]")
    return None


def get_version(package: str) -> str:
    try:
        return _dist_version(_dist_name_for(package))
    except PackageNotFoundError:
        v = _read_pyproject_version(Path(__file__).resolve())
        return v or "0.0.0+local"


__version__ = get_version(__package__)
