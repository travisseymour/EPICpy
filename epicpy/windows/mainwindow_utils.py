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

from PySide6.QtCore import QSize, QRect
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget


def usable_size_at_least(target_size: QSize) -> bool:
    return size_fits(target_size, get_desktop_usable_geometry())


def size_fits(small: QSize, big: QSize) -> bool:
    return small.width() <= big.width() and small.height() <= big.height()


def get_desktop_geometry() -> QSize:
    primary_screen = QGuiApplication.primaryScreen()
    geometry = primary_screen.geometry()

    return QSize(geometry.width(), geometry.height())


def get_desktop_usable_geometry() -> QSize:
    primary_screen = QGuiApplication.primaryScreen()
    available_geometry = primary_screen.availableGeometry()

    usable_width = available_geometry.width()
    usable_height = available_geometry.height()

    return QSize(usable_width, usable_height)


def set_unscaled_geometry(widget: QWidget, physical_rect: QRect):
    """
    Sets the geometry of the given widget so that its position and size match
    the provided physical (unscaled) pixel QRect. It converts the physical
    coordinates to logical coordinates using the primary screen's device pixel ratio.

    Parameters:
        widget (QWidget): The widget to resize and reposition.
        physical_rect (QRect): The desired geometry (position and size) in physical pixels.
    """
    screen = QGuiApplication.primaryScreen()
    scaling_factor = screen.devicePixelRatio() if screen else 1.0

    # Convert physical coordinates to logical coordinates.
    logical_x = int(physical_rect.x() / scaling_factor)
    logical_y = int(physical_rect.y() / scaling_factor)
    logical_width = int(physical_rect.width() / scaling_factor)
    logical_height = int(physical_rect.height() / scaling_factor)

    logical_rect = QRect(logical_x, logical_y, logical_width, logical_height)
    widget.setGeometry(logical_rect)
