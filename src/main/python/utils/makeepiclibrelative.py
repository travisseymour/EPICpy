"""
This file is part of EPICpy, Created by Travis L. Seymour, PhD.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with EPICpy.
If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
import re
import platform
import os.path

OS = platform.system()

path_prefix = Path("EPICLib").absolute()

epiclib_file_paths = [
    file for file in Path("EPICLib").glob("**/*.*") if file.suffix in (".h", ".cpp")
]
epiclib_file_names = [file.name for file in epiclib_file_paths]
epiclib_decoder = dict(
    zip(epiclib_file_names, [str(path) for path in epiclib_file_paths])
)

# include_pattern = re.compile(r'^#include \"(\w+\.h)\"')
include_pattern = re.compile(
    r"^#include \"([a-zA-Z0-9_/ -:]+\.h)\"", flags=re.MULTILINE
)


def expand(folder: str, debug: bool = False):
    try:
        shrink(folder)
    except:
        pass
    if not Path(folder).is_dir():
        print(f"ERROR: {folder} does not appear to be a valid folder path")
    file_paths = [
        file for file in Path(folder).glob("**/*.*") if file.suffix in (".h", ".cpp")
    ]
    for file in file_paths:
        print(f"Processing {file.name}...")
        code = file.read_text()
        includes = include_pattern.findall(code)
        if not includes:
            continue  # avoid file.write_text(code) if not needed!
        for include in set(includes):
            if include:
                _include = str(Path(include).name)
                try:
                    old, new = include, str(
                        Path(path_prefix, epiclib_decoder[_include])
                    )
                    new = new.replace("EPICLib/EPICLib", "EPICLib")
                    new = new.replace("EPICLib\\EPICLib", "EPICLib")
                    relative = os.path.relpath(Path(new), file)
                    parts = Path(relative).parts
                    if parts.count("..") > 0:
                        parts = parts[1:]
                    relative = str(Path(*parts))
                    print(f'\t{old} --{">" if not debug else "?"} {new}')
                    print(f'\t{old} --{">" if not debug else "?"} {relative}')
                    code = code.replace(old, relative)  # was old, new
                except KeyError:
                    pass
        if debug == False:
            file.write_text(code)


def shrink(folder: str, debug: bool = False):
    if not Path(folder).is_dir():
        print(f"ERROR: {folder} does not appear to be a valid folder path")
    file_paths = [
        file for file in Path(folder).glob("**/*.*") if file.suffix in (".h", ".cpp")
    ]
    for file in file_paths:
        print(f"Processing {file.name}...")
        code = file.read_text()
        includes = include_pattern.findall(code)
        if not includes:
            continue  # avoid file.write_text(code) if not needed!
        for include in set(includes):
            if include:
                _include = str(Path(include).name)
                old, new = include, _include
                # print(f'\t{old} --> {new}')
                code = code.replace(old, new)
        if debug == False:
            file.write_text(code)


if __name__ == "__main__":
    """
    Expects a folder called EPICLib to temporarily be in the same folder as this file.
    It will make the paths relative, then you can move it wherever you want.
    """
    # commented out to avoid accidental run
    # expand("EPICLib", debug=False)
    # expand("EPICLib/PPS", debug=False)
    print("\nYou should not need to re-run this! Otherwise, edit __main__\n")
