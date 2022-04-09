"""
This file is part of EPICpy, Created by Travis L. Seymour, PhD.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar.
If not, see <https://www.gnu.org/licenses/>.
"""

"""
Useful Emojis and ascii symbols
(for new ones, consult https://textkool.com/en/symbols/)
"""
import ascii_frame

e_notepad = "\U0001f4cb"
e_dark_bang = "\u2757"
e_light_bang = "\u2755"
e_light_check = "\u2705"
e_dark_check = "\u2714"
e_boxed_x = "\u274E"
e_boxed_check = "\u2611"
e_heavy_check = "\u2714"
e_heavy_x = "\u2716"
e_bangbang = "\u203C"
e_graph = "\U0001f4ca"
e_hourglass = "\u23F3"
e_230 = "\U0001f55d"
e_info = "\u2139"
e_boxed_ok = "\U0001f197"
e_warning = "\u26A0"
e_huge_x = "╳"
e_huge_left_bracket = "〱"
e_left_arrow = "⟶"
e_right_arrow = "⟵"
e_left_arrow2 = "⟸"
e_right_arrow2 = "⟹"
e_right_arrow3 = "⟹"


def emoji_box(text: str, width: int = 105, padding: int = 1, line="thin") -> str:
    assert line in ("thin", "thick", "double")

    # pattern is UR, LR, LL, UL
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
    lines = [line for line in ascii_frame.wrap( text.splitlines(keepends=False), width=wid + (pad * 2), padding=pad, corners=corners, edges=edges) if line]
    return '\n'.join(lines)
