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

from __future__ import annotations

from pathlib import Path
from typing import Optional
import re

import requests
from epicpy import __version__

# --- TOML parsing ---
try:
    import tomllib as toml  # Python 3.11+
except ModuleNotFoundError:  # Python 3.10
    import tomli as toml  # pip install tomli

# --- Version validation / comparison ---
try:
    from packaging.version import Version

    def _norm(v: str) -> str:
        # Validate PEP 440; raises if invalid
        _ = Version(v)
        return v

    def _is_newer(a: str, b: str) -> bool:
        return Version(a) > Version(b)

except Exception:
    # Fallback: best-effort string handling (not PEP 440–aware)
    def _norm(v: str) -> str:
        return v.strip()

    def _is_newer(a: str, b: str) -> bool:
        return a.strip() > b.strip()


_VERSION_RE = re.compile(r'^\s*(?P<var>__version__|VERSION)\s*=\s*["\'](?P<val>[^"\']+)["\']\s*$')


def _pick(v) -> Optional[str]:
    return v.strip() if isinstance(v, str) and v.strip() else None


def _read_version_from_file(root: Path, rel_path: str, var_name: str | None = None) -> Optional[str]:
    """Read a Python file and extract __version__ (or custom var) = 'x.y.z'."""
    src = (root / rel_path).read_text(encoding="utf-8", errors="ignore").splitlines()
    if var_name:
        rx = re.compile(rf'^\s*{re.escape(var_name)}\s*=\s*["\']([^"\']+)["\']\s*$')
        for line in src:
            m = rx.match(line)
            if m:
                return _norm(m.group(1))
        return None
    # default: look for __version__ or VERSION
    for line in src:
        m = _VERSION_RE.match(line)
        if m:
            return _norm(m.group("val"))
    return None


def extract_version_from_toml(path: str | Path) -> Optional[str]:
    """
    Return the project version from a pyproject.toml file (or None).

    Order:
      1) [project].version (PEP 621)
      2) [tool.poetry].version
      3) [tool.flit.metadata].version
      4) Hatchling dynamic-from-file:
         [tool.hatch.version] source="path"; path="pkg/__init__.py"; variable="__version__"
      5) setuptools_scm fallback (if configured): [tool.setuptools_scm].fallback_version
    """
    path = Path(path)
    root = path.parent
    data = toml.loads(path.read_text(encoding="utf-8"))

    # 1) PEP 621
    v = _pick((data.get("project") or {}).get("version"))
    if v:
        return _norm(v)

    # 2) Poetry
    v = _pick(((data.get("tool") or {}).get("poetry") or {}).get("version"))
    if v:
        return _norm(v)

    # 3) Flit (legacy)
    v = _pick((((data.get("tool") or {}).get("flit") or {}).get("metadata") or {}).get("version"))
    if v:
        return _norm(v)

    # 4) Hatchling dynamic via file
    hatch = ((data.get("tool") or {}).get("hatch") or {}).get("version") or {}
    if isinstance(hatch, dict) and hatch.get("source") == "path":
        rel = hatch.get("path")
        if isinstance(rel, str) and rel.strip():
            var = hatch.get("variable")  # optional; default __version__
            v = _read_version_from_file(root, rel.strip(), var_name=var)
            if v:
                return _norm(v)

    # 5) setuptools_scm: respect an explicit fallback if present
    scm = (data.get("tool") or {}).get("setuptools_scm") or {}
    v = _pick(scm.get("fallback_version"))
    if v:
        return _norm(v)

    return None


def extract_version_from_toml_text(text: str, *, base_dir: str | Path = ".") -> Optional[str]:
    """
    Same as above, but takes TOML text (e.g., from GitHub raw).
    If Hatchling path-source is used, 'base_dir' is where to resolve the path.
    """
    base = Path(base_dir)
    data = toml.loads(text)

    v = _pick((data.get("project") or {}).get("version"))
    if v:
        return _norm(v)

    v = _pick(((data.get("tool") or {}).get("poetry") or {}).get("version"))
    if v:
        return _norm(v)

    v = _pick((((data.get("tool") or {}).get("flit") or {}).get("metadata") or {}).get("version"))
    if v:
        return _norm(v)

    hatch = ((data.get("tool") or {}).get("hatch") or {}).get("version") or {}
    if isinstance(hatch, dict) and hatch.get("source") == "path":
        rel = hatch.get("path")
        if isinstance(rel, str) and rel.strip():
            var = hatch.get("variable")
            try:
                v = _read_version_from_file(base, rel.strip(), var_name=var)
            except FileNotFoundError:
                v = None
            if v:
                return _norm(v)

    scm = (data.get("tool") or {}).get("setuptools_scm") or {}
    v = _pick(scm.get("fallback_version"))
    if v:
        return _norm(v)

    return None


def get_remote_version(
    owner: str, repo: str, branch: str = "main", path: str = "pyproject.toml", *, timeout: float = 1.5
) -> str:
    """
    Fetch version from GitHub raw. Returns '' on any network error, timeout,
    non-200, or parse failure.
    """
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code != 200:
            return ""
        v = extract_version_from_toml_text(resp.text)
        return v or ""
    except requests.RequestException:
        # no internet / DNS / TLS / timeout -> treat as "no update info"
        return ""
    except Exception:
        return ""


def update_available() -> str:
    remote_version = get_remote_version("travisseymour", "EPICpy")
    if remote_version and (remote_version != __version__) and _is_newer(remote_version, __version__):
        return (
            "\n----------------------------------------------\n"
            f"A NEW version of EPICpy is available ({remote_version}), you have version {__version__}. "
            "To update, run\nuv tool upgrade epicpy\nin your terminal, and then press ENTER.\n"
            "----------------------------------------------\n"
        )
    else:
        return ""


if __name__ == "__main__":
    print(f"{__version__=}")
    print(f"{update_available()=}")
