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

from pathlib import Path
from typing import Optional

import requests
from epicpy import __version__
import ast


def extract_version_from_toml(path: str | Path) -> Optional[str]:
    """Return the project version from pyproject.toml (or None).
    Checks PEP 621 [project].version, then common tool sections (Poetry, Flit).
    """
    try:
        import tomllib as toml  # 3.11+
    except ModuleNotFoundError:  # 3.10
        import tomli as toml  # pip install tomli

    data = toml.loads(Path(path).read_text(encoding="utf-8"))

    def _pick(v):
        return v.strip() if isinstance(v, str) and v.strip() else None

    # PEP 621
    v = _pick((data.get("project") or {}).get("version"))
    if v:
        return v
    # Poetry
    v = _pick(((data.get("tool") or {}).get("poetry") or {}).get("version"))
    if v:
        return v
    # Flit
    v = _pick((((data.get("tool") or {}).get("flit") or {}).get("metadata") or {}).get("version"))
    return v


def get_remote_version(owner: str, repo: str, branch: str = "main", path: str = "pyproject.toml") -> str:
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    response = requests.get(url)
    try:
        return extract_version_from_toml(response.text)
    except:
        return ""


def update_available() -> str:
    remote_version = get_remote_version("travisseymour", "EPICpy")
    if remote_version and (remote_version != __version__) and (remote_version > __version__):
        return (
            f"\n----------------------------------------------\n"
            f"A NEW version of EPICpy is available ({remote_version}), you have version {__version__}. "
            f"To update, run\nuv tool upgrade epicpy\nin your terminal, and then press ENTER.\n"
            f"----------------------------------------------\n"
        )
    else:
        return ""


if __name__ == "__main__":
    print(f"{__version__=}")
    print(f"{update_available()=}")
