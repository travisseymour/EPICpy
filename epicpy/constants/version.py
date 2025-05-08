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

# year.month.version
__version__ = "2025.5.8.1"

__loglevel__ = "INFO"

"""
Level 	Numeric value
CRITICAL 	50
ERROR 	    40
WARNING 	30
INFO 	    20
DEBUG 	    10
NOTSET 	    0
"""

import requests
import re


def get_remote_version(owner: str, repo: str, branch: str = "main", path: str = "epicpy/constants/version.py") -> str:
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    response = requests.get(url)
    response.raise_for_status()

    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', response.text)
    if not match:
        raise ValueError("Could not find __version__ in remote version.py")
    return match.group(1)


def update_available() -> str:
    remote_version = get_remote_version("travisseymour", "EPICpy")
    if remote_version != __version__ and remote_version > __version__:
        return (
            f"----------------------------------------------"
            f"A NEW version of EPICpy is available ({remote_version}), you have version {__version__}. "
            f"To update, run\nuv tool upgrade epicpy\nin your terminal, and then press ENTER."
            f"----------------------------------------------"
        )
    else:
        return ""


if __name__ == "__main__":
    print(f'{__version__=}')
    print(f"{update_available()=}")
