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
    scaling_factor = screen.devicePixelRatioF() if screen else 1.0

    # Convert physical coordinates to logical coordinates.
    logical_x = int(physical_rect.x() / scaling_factor)
    logical_y = int(physical_rect.y() / scaling_factor)
    logical_width = int(physical_rect.width() / scaling_factor)
    logical_height = int(physical_rect.height() / scaling_factor)

    logical_rect = QRect(logical_x, logical_y, logical_width, logical_height)
    widget.setGeometry(logical_rect)
