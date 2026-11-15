# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

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
