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

import sys
from collections import OrderedDict
from pathlib import Path

from PySide6.QtGui import QCursor, Qt
from PySide6.QtWidgets import QApplication
from loguru import logger as log

import timeit
import datetime
import platform
from typing import Union, List
import re
import itertools

import warnings
from functools import wraps

from epicpy import pathEX

OS = platform.system()


# if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
#     pathEX = Path(sys._MEIPASS)
# else:
#     pathEX = Path(__file__).parent


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
            print(
                f'Timer Started at {datetime.datetime.now().strftime("%H:%M:%S")}'
            )  # add %f for microseconds
        self.start = timeit.default_timer()

    def __exit__(self, *args):
        self.stop = timeit.default_timer()
        self.duration = self.stop - self.start
        if self.verbose:
            print(f'Timer Ended at {datetime.datetime.now().strftime("%H:%M:%S")}')
        print(f"Duration: {self.duration:0.4f} sec ({self.duration * 1000:0.4f} msec)")


def unpack_param_string(
        pattern: str, delimiter: str = "|", left: str = "[", right: str = "]"
) -> List[str]:
    """
    Expand the brace-delimited possibilities in a string.
    E.g.: "10 Easy Dash" or "10 [Easy|Hard] Dash" or "10 [Easy|Hard] [Dash|HUD]"
    Based on solution from stackoverflow.com/MarekG Jan 2 22
    """
    seg_choices = (
        seg.strip(left + right).split(delimiter) if seg.startswith(left) else [seg]
        for seg in re.split(rf"(\{left}.*?\{right})", pattern)
    )

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


def fjoin(*elements):
    return Path(pathEX, *elements).resolve()


def get_resource(*args) -> Path:
    base_folder = Path(pathEX, "resources").resolve()

    target_path = Path(base_folder, *args)
    if target_path.exists():
        return target_path
    else:
        raise FileNotFoundError(f'Unable to locate resource "{str(target_path)}"')


def memoize_class_method(max_items=250):
    """
    Class method for an alternative lru_cache.
    Python's lru_cache has big issues with used on class methods.
    """
    cache = OrderedDict()

    def decorator(func):
        def memoized_func(instance, *args, **kwargs):
            if instance not in cache:
                cache[instance] = OrderedDict()
            if args not in cache[instance]:
                if len(cache[instance]) >= max_items:
                    # Remove the least recently used item from the cache
                    cache[instance].popitem(last=False)
                cache[instance][args] = func(instance, *args, **kwargs)
            return cache[instance][args]

        return memoized_func

    return decorator


def loading_cursor(normal_function):
    def decorated_function(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        normal_function(*args, **kwargs)

        QApplication.restoreOverrideCursor()

    return decorated_function


if __name__ == "__main__":
    print(f"{get_resource('fonts', 'Fira Mono', 'ATTRIBUTION.txt')=}")
    print(f"{get_resource('epiclib', 'EPIC_LICENSE.txt')=}")
    print(f"{get_resource('fake_file.txt')=}")
