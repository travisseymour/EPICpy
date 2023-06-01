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

from PySide6.QtGui import QColor, QColorConstants

from epicpy.utils.localmunch import Munch

"""
For more colors, consult https://cloford.com/resources/colours/500col.htm
"""

epic_colors = Munch(
    {
        "Aqua": QColor(
            0, 255, 255, 255
        ),  # aqua and cyan are synonymous? going with aquamarine
        "Black": QColorConstants.Black,
        "Blue": QColorConstants.Blue,
        "Brown": QColor(139, 69, 19, 255),
        "Chartreuse": QColor(127, 255, 0, 255),
        "Cyan": QColor(0, 238, 238),
        "DarkBlue": QColorConstants.DarkBlue,
        "DarkGray": QColorConstants.DarkGray,
        "DarkGreen": QColorConstants.DarkGreen,
        "DarkRed": QColorConstants.DarkRed,
        "DarkViolet": QColor(148, 0, 211, 255),
        "Gainsboro": QColor(220, 220, 220, 255),  # a very light gray
        "Green": QColorConstants.Green,
        "Gray": QColorConstants.Gray,
        "Fuchsia": QColor(255, 0, 255, 255),
        "Gold": QColor(255, 215, 0, 255),
        "GoldenRod": QColor(218, 165, 32, 255),
        "LightBlue": QColor(191, 239, 255, 255),
        "LightGray": QColor(211, 211, 211, 255),
        "Magenta": QColorConstants.Magenta,
        "Maroon": QColor(255, 52, 179, 255),
        "Navy": QColor(0, 0, 128, 255),
        "Olive": QColor(128, 128, 0, 255),
        "Pink": QColor(255, 192, 203, 255),
        "Purple": QColor(128, 0, 128, 255),
        "Red": QColorConstants.Red,
        "RoyalBlue": QColor(65, 105, 225, 255),
        "SlateGray": QColor(112, 128, 144, 255),
        "Teal": QColor(0, 128, 128, 255),
        "Turquoise": QColor(64, 224, 208, 255),
        "Violet": QColor(238, 130, 238, 255),
        "White": QColorConstants.White,
        "Yellow": QColorConstants.Yellow,
    }
)
