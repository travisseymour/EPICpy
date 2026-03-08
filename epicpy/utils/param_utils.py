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

"""
Pure utility functions for parameter string manipulation.

This module is intentionally Qt-free so it can be safely imported in
multiprocessing worker processes without triggering GUI initialization.
"""

import itertools
import re
from typing import List


def unpack_param_string(pattern: str, delimiter: str = "|", left: str = "[", right: str = "]") -> List[str]:
    """
    Expand the bracket-delimited possibilities in a string.
    E.g.: "10 Easy Dash" or "10 [Easy|Hard] Dash" or "10 [Easy|Hard] [Dash|HUD]"

    Based on solution from stackoverflow.com/MarekG Jan 2 22.
    """
    # Escape left/right brackets to avoid regex issues
    left_escaped = re.escape(left)
    right_escaped = re.escape(right)

    # Split pattern while keeping the brackets
    segments = re.split(rf"({left_escaped}.*?{right_escaped})", pattern)

    # Process each segment
    seg_choices = [seg.strip(left + right).split(delimiter) if seg.startswith(left) else [seg] for seg in segments]

    # Generate all possible combinations
    return ["".join(parts) for parts in itertools.product(*seg_choices)]
