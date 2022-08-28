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

from PIL import Image
from pathlib import Path

"""
note: best practices for rescaling:
When sampling down: Use Lanczos or Spline filtering.
When sampling up: Use Bicubic or Lanczos filtering.
"""

icons_sizes = {
    "base": (16, 24, 32, 48, 64),
    "linux": (128, 256, 512, 1024),
    "mac": (128, 256, 512, 1024),
}

source_path = Path("../..", "icons", "Icon.png")
source = Image.open(source_path)
source_width = source.width

for folder, sizes in icons_sizes.items():
    for size in sizes:
        if size > source_width:
            sampler = Image.LANCZOS
        elif size < source_width:
            sampler = Image.BICUBIC
        else:
            sampler = 0
        target = source.resize((size, size), resample=sampler)
        target.save(Path("../..", "icons", folder, f"{size}.png"))
