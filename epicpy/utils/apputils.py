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

import math
import os
import subprocess
import sys
import tempfile
import time
import zipfile
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from weakref import WeakKeyDictionary

from qtpy.QtGui import QPalette
from qtpy.QtWidgets import QWidget
from qtpy.QtCore import Qt, QEventLoop, QTimer
from qtpy.QtGui import QCursor
from qtpy.QtWidgets import QApplication
from loguru import logger as log

import timeit
import datetime
import platform
from typing import Union, List, Optional
import re
import itertools

import warnings
from functools import wraps

from epicpy import get_resource

OS = platform.system()
from dataclasses import dataclass as base_dataclass


class Point:
    """
    point class with property and iterable access
    """

    __slots__ = "x", "y"

    def __init__(self, x: Union[float, int], y: Union[float, int]):
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))

    def __str__(self):
        return f"Point({self.x},{self.y})"


class Size:
    """
    size class with property and iterable access
    """

    __slots__ = "w", "h"

    def __init__(self, w: Union[float, int], h: Union[float, int]):
        self.w = w
        self.h = h

    def __iter__(self):
        return iter((self.w, self.h))

    def __str__(self):
        return f"Size({self.w},{self.h})"


class Rect:
    """
    rect class with property and iterable access
    """

    __slots__ = "x", "y", "w", "h"

    def __init__(
        self,
        x: Union[float, int],
        y: Union[float, int],
        w: Union[float, int],
        h: Union[float, int],
    ):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __iter__(self):
        return iter((self.x, self.y, self.w, self.h))

    def __str__(self):
        return f"Rect(Point({self.x},{self.y}), Rect({self.w},{self.h}))"


def frozen() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


if frozen():
    log.level("INFO")


def addroot(currpath):
    main_file_location = Path(__file__).parent.absolute()
    return str(Path(main_file_location, currpath))


def ospath(path_str: str) -> str:
    if OS == "Windows":
        return str(Path(path_str).absolute())
    else:
        return path_str


def is_numeric(value) -> bool:
    try:
        _ = float(value)
        return True
    except ValueError:
        return False


def is_listy(value: str) -> bool:
    """
    accepts a string and returns True if it evals to a list or tuple, otherwise False
    """
    try:
        candidate = eval(value)
        isinstance(candidate, (tuple, list))
        return True
    except:
        return False


def tuplize(value: str) -> tuple:
    """
    accepts a string representation of a list or tuple and returns a tuple.
    there is no error checking here, so call is_listy(first)
    """
    return tuple(eval(value))


class Timer(object):
    """
    E.g.:
    import time
    with Timer('how long this code took='):
        for i in range(25):
            sleep(1)
    """

    def __init__(self, description="Elapsed Time"):
        self.description = description

    def __enter__(self):
        self.start = timeit.default_timer()

    def __exit__(self, type, value, traceback):
        self.end = timeit.default_timer()
        print(f"{self.description}: {self.end - self.start}")


class FancyTimer:
    """
    This is a context manager to time a code block
    """

    def __init__(self, msg: str = "", verbose=False):
        self.msg = msg
        self.verbose = verbose
        self.start = -1
        self.stop = -1
        self.duration = -1

    def __enter__(self):
        if self.msg:
            l = len(self.msg)
            print(f'\n{self.msg}\n{"=" * l if l < 50 else 50}')
        if self.verbose:
            print(f'Timer Started at {datetime.datetime.now().strftime("%H:%M:%S")}')  # add %f for microseconds
        self.start = timeit.default_timer()

    def __exit__(self, *args):
        self.stop = timeit.default_timer()
        self.duration = self.stop - self.start
        if self.verbose:
            print(f'Timer Ended at {datetime.datetime.now().strftime("%H:%M:%S")}')
        print(f"Duration: {self.duration:0.4f} sec ({self.duration * 1000:0.4f} msec)")


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


def ignore_warnings(f):
    # https://stackoverflow.com/questions/879173
    @wraps(f)
    def inner(*args, **kwargs):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("ignore")
            response = f(*args, **kwargs)
        return response

    return inner


class add_path:
    """
    Creates A Context Manager For Temporarily Adding Directory To System Path.
    E.g., see https://stackoverflow.com/questions/17211078
    """

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass


def memoize_class_method(max_items=250):
    """
    A class method decorator for an alternative LRU cache.
    This version:
    - Uses WeakKeyDictionary to avoid memory leaks.
    - Supports keyword arguments (`kwargs`).
    - Is thread-safe.
    """
    cache = WeakKeyDictionary()
    lock = Lock()

    def decorator(func):
        def memoized_func(instance, *args, **kwargs):
            key = (args, frozenset(kwargs.items()))  # Support for kwargs

            with lock:  # Thread safety
                if instance not in cache:
                    cache[instance] = OrderedDict()

                if key not in cache[instance]:
                    if len(cache[instance]) >= max_items:
                        cache[instance].popitem(last=False)  # LRU eviction
                    cache[instance][key] = func(instance, *args, **kwargs)

            return cache[instance][key]

        return memoized_func

    return decorator


@contextmanager
def loading_cursor_context():
    QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
    try:
        loop = QEventLoop()
        QTimer.singleShot(0, loop.quit)  # ensure one full UI tick
        loop.exec()
        yield
    finally:
        QApplication.restoreOverrideCursor()


def timeit_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {elapsed_time:.6f} seconds\n")
        return result

    return wrapper


def has_epiccoder() -> str:
    """
    Determines whether the application "epiccoder" is installed by checking for its
    executable using the appropriate command for the current platform.

    On macOS and Linux, it runs `which epiccoder`.
    On Windows, it runs `where epiccoder`.

    Returns:
        The full path to the "epiccoder" executable if it exists and is a local file;
        otherwise, returns an empty string.
    """
    try:
        # Choose the command based on the operating system.
        if platform.system() == "Windows":
            cmd = ["where", "epiccoder"]
        else:
            cmd = ["which", "epiccoder"]

        # Run the command and decode its output.
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        if not output:
            return ""
        # In case multiple paths are returned, use the first one.
        epiccoder_path = output.splitlines()[0].strip()
        # Verify that the path refers to a local file.
        if os.path.isfile(epiccoder_path):
            return epiccoder_path
        else:
            return ""
    except Exception:
        return ""


def run_without_waiting(exe_path: str, filename: str):
    try:
        # Ensure the executable path and filename are properly formatted
        filename = os.path.abspath(filename)

        # Use different process spawning methods based on the OS
        if sys.platform == "win32":
            # Windows: Use `creationflags=subprocess.DETACHED_PROCESS` to detach
            subprocess.Popen(
                [exe_path, filename], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            # macOS/Linux: Use `start_new_session=True` to detach
            subprocess.Popen([exe_path, filename], start_new_session=True)
    except Exception as e:
        print(f"Error starting process: {e}")


def default_run(file_path: Union[str, Path]) -> bool:
    """
    Opens the file specified by file_path using the current operating system's
    default command for launching files. The file is opened in the background.

    Parameters:
        file_path (Union[str, Path]): The path to the file to be opened.

    Returns:
        bool: True if the file was successfully launched, False otherwise.
    """
    try:
        # Convert to string if file_path is a Path object.
        if isinstance(file_path, Path):
            file_path = str(file_path)

        system = platform.system()

        if system == "Windows":
            # On Windows, use os.startfile (this opens the file with its default application).
            os.startfile(file_path)
        elif system == "Darwin":
            # On macOS, use the 'open' command.
            subprocess.Popen(["open", file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Linux":
            # On Linux, use 'xdg-open' which is desktop-environment agnostic.
            subprocess.Popen(["xdg-open", file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Unsupported operating system.
            return False

        return True
    except Exception:
        return False


def clear_font(widget: QWidget):
    """Recursively reset fonts for all child widgets."""
    widget.setFont(QApplication.instance().font())  # Set default app font
    for child in widget.findChildren(QWidget):
        child.setFont(QApplication.instance().font())


# Define a conditional dataclass decorator.
if sys.version_info >= (3, 10) and platform.system() != "Windows":

    def conditional_dataclass(cls):
        return base_dataclass(cls, slots=True)

else:
    # Either Python version is below 3.10 or we are on Windows.
    # In that case, just use the normal dataclass decorator.
    conditional_dataclass = base_dataclass


def is_dark_mode():
    palette = QApplication.palette()
    # Get the window background color from the palette.
    bg = palette.color(QPalette.ColorRole.Window)
    # Compute brightness using a standard luminance formula.
    brightness = math.sqrt(0.299 * bg.red() ** 2 + 0.587 * bg.green() ** 2 + 0.114 * bg.blue() ** 2)
    # Return True if brightness is below a threshold (e.g. 128)
    return brightness < 128


def print_tree(path: Path, prefix: str = ""):
    """Print a tree structure starting from a given Path."""
    contents = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    pointers = ["├── "] * (len(contents) - 1) + ["└── "]
    for pointer, item in zip(pointers, contents):
        print(prefix + pointer + item.name)
        if item.is_dir():
            extension = "│   " if pointer == "├── " else "    "
            print_tree(item, prefix + extension)


def extract_from_zip(zip_path: Path, target_path: Path, start_path: Optional[str] = None):
    """
    Extract files from a zip archive.

    - If start_path is None, acts like extractall().
    - Otherwise, extracts only the contents from start_path (and below),
      stripping start_path from the extracted paths.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            # If start_path is None, extract everything normally
            if start_path is None:
                zf.extract(member, path=target_path)
                continue

            # If member path starts with the start_path, we want to extract it
            if member.startswith(start_path.rstrip("/") + "/"):
                # Strip off the start_path part
                relative_path = member[len(start_path.rstrip("/") + "/") :]

                # If it's a directory entry, just ensure the directory exists
                if member.endswith("/"):
                    (target_path / relative_path).mkdir(parents=True, exist_ok=True)
                    continue

                # Otherwise, extract the file manually
                dest_file = target_path / relative_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as source, open(dest_file, "wb") as target_file:
                    target_file.write(source.read())


if __name__ == "__main__":
    print(f"{ get_resource('fonts', 'Fira Mono', 'ATTRIBUTION.txt')=}")
    print(f"{ get_resource('epiclib', 'EPIC_LICENSE.txt')=}")
    print(f"{ get_resource('fake_file.txt')=}")

    path = has_epiccoder()
    if path:
        print(f"epiccoder is installed at: {path}")
    else:
        print("epiccoder is not installed or its executable was not found.")

    temp = tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False)
    try:
        # Write the specified text to the file.
        temp.write("this is a temp file used for testing")
        temp.close()  # Close the file so that other processes can access it.

        print("Created temporary file:", temp.name)

        # Use default_run to open the temporary file.
        if default_run(temp.name):
            print("File launched successfully!")
        else:
            print("Failed to launch the file.")
    except Exception as e:
        print("An error occurred:", e)

    print(f"""{unpack_param_string("10 Easy Dash")=}\n\t➝ ['10 Easy Dash']""")

    print(f"""{unpack_param_string("10 [Easy|Hard] Dash")=}\n\t➝ ['10 Easy Dash', '10 Hard Dash']""")

    print(
        f"""{unpack_param_string("10 [Easy|Hard] [Dash|HUD]")=}\n\t➝ ['10 Easy Dash', '10 Easy HUD', '10 Hard Dash', '10 Hard HUD']"""
    )
