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


def emoji_box(text: str, width: int = 0, line="thin") -> str:
    assert line in ("thin", "thick", "double")
    symbols = {
        "thin": {
            "v_line": "│",
            "h_line": "─",
            "ul": "┌",
            "ur": "┐",
            "ll": "└",
            "lr": "┘",
        },
        "thick": {
            "v_line": "┃",
            "h_line": "━",
            "ul": "┏",
            "ur": "┓",
            "ll": "┗",
            "lr": "┛",
        },
        "double": {
            "v_line": "║",
            "h_line": "═",
            "ul": "╔",
            "ur": "╗",
            "ll": "╚",
            "lr": "╝",
        },
    }
    v_line, h_line, ul, ur, ll, lr = symbols[line].values()

    gap = 4
    output = ""
    string_list = text.strip().splitlines()
    box_width = width if width else max([len(aline) for aline in string_list]) + gap

    output += f"{ul}{h_line * (box_width - gap // 2)}{ur}\n"
    for line in string_list:
        output += f"{v_line} {line:<{box_width - gap}} {v_line}\n"
    output += f"{ll}{h_line * (box_width - gap // 2)}{lr}\n"

    return output


if __name__ == "__main__":
    for emoji in (
        e_notepad,
        e_dark_bang,
        e_light_bang,
        e_light_check,
        e_dark_check,
        e_boxed_x,
        e_boxed_check,
        e_heavy_check,
        e_heavy_x,
        e_bangbang,
        e_graph,
        e_hourglass,
        e_230,
        e_info,
        e_boxed_ok,
    ):
        print(emoji, end=" ")
    print()
    s = """
        This is some text for you to ponder. This text is long and should be taken 
        quite seriously. Then again, you can take it as seriously as you think you 
        should. Bye now.
        """
    print(emoji_box(s))
    print()
    print(emoji_box(s, 25))
    print()

    s2 = """
        One two three four
        fix size seven eight
        """
    print(emoji_box(s2))

    print()
    print(emoji_box("RULE FILE: choicetask_rules_VM.prs", line="double"))
