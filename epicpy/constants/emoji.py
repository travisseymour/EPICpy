# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

import platform

import ascii_frame

"""
Useful Emojis and ascii symbols
(for new ones, consult https://textkool.com/en/symbols/)
"""

# FIXME: Temporarily nerfing this functionality due to errors on windows when saving output windows to text

if platform.system().lower().startswith("win"):
    e_notepad = ""
    e_dark_bang = ""
    e_light_bang = ""
    e_light_check = ""
    e_dark_check = ""
    e_boxed_x = ""
    e_boxed_check = ""
    e_heavy_check = ""
    e_heavy_x = ""
    e_bangbang = ""
    e_graph = ""
    e_hourglass = ""
    e_230 = ""
    e_info = ""
    e_boxed_ok = ""
    e_warning = ""
    e_huge_x = ""
    e_huge_left_bracket = ""
    e_left_arrow = ""
    e_right_arrow = ""
    e_left_arrow2 = ""
    e_right_arrow2 = ""
    e_right_arrow3 = ""
else:
    e_notepad = "\U0001f4cb"
    e_dark_bang = "\u2757"
    e_light_bang = "\u2755"
    e_light_check = "\u2705"
    e_dark_check = "\u2714"
    e_boxed_x = "\u274e"
    e_boxed_check = "\u2611"
    e_heavy_check = "\u2714"
    e_heavy_x = "\u2716"
    e_bangbang = "\u203c"
    e_graph = "\U0001f4ca"
    e_hourglass = "\u23f3"
    e_230 = "\U0001f55d"
    e_info = "\u2139"
    e_boxed_ok = "\U0001f197"
    e_warning = "\u26a0"
    e_huge_x = "╳"
    e_huge_left_bracket = "〱"
    e_left_arrow = "⟶"
    e_right_arrow = "⟵"
    e_left_arrow2 = "⟸"
    e_right_arrow2 = "⟹"
    e_right_arrow3 = "⟹"


def emoji_box(text: str, width: int = 105, padding: int = 1, line="thin") -> str:
    """
    FIXME: Temporarily nerfing this functionality due to errors on windows when saving output windows to text
    """
    assert line in ("thin", "thick", "double")

    # pattern is UR, LR, LL, UL

    if platform.system().lower().startswith("win"):
        return text
        corners = {"thin": "****", "thick": "****", "double": "****"}[line]
        edges = {"thin": "-|", "thick": "-|", "double": "-|"}[line]
    else:
        corners = {"thin": "┐┘└┌", "thick": "┓┛┗┏", "double": "╗╝╚╔"}[line]
        edges = {"thin": "─│", "thick": "━┃", "double": "═║"}[line]

    wid, pad = width, padding
    try:
        assert wid > 0 and wid > pad
    except AssertionError:
        wid = 50
        pad = 1 if padding else 0

    longest = max(len(row) for row in text.splitlines())
    wid = min(wid + padding * 2, longest)
    if wid > 105:
        wid = 105
    lines = [
        line
        for line in ascii_frame.wrap(
            text.splitlines(keepends=False),
            width=wid + (pad * 2),
            padding=pad,
            corners=corners,
            edges=edges,
        )
        if line
    ]
    return "\n".join(lines)
