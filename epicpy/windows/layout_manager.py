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

from collections.abc import Mapping

from qtpy.QtCore import QSize, Qt
from qtpy.QtWidgets import QDockWidget, QMainWindow, QSizePolicy

from epicpy.views.auditory_view_window import AuditoryViewWin
from epicpy.views.visual_view_window import VisualViewWin

# Bump when docks are added/removed/renamed to invalidate stale saved layouts
_LAYOUT_VERSION = 2


class HorizontalDockArea(QMainWindow):
    """
    A QMainWindow subclass that acts as a container for three dock widgets
    arranged horizontally. Each dock contains a label displaying a placeholder text.
    Each label has a minimum size of 392x342, an expanding size policy, and a visible border.
    Each dock is individually closable, movable, and floatable.
    """

    def __init__(
        self,
        widgets: Mapping[str, VisualViewWin | AuditoryViewWin],
        minimum_view_size: QSize,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Horizontal Dock Area")
        self.setDockNestingEnabled(True)

        docks = []
        for i, widget_name in enumerate(widgets):
            # Each label is wrapped in its own QDockWidget.
            dock = QDockWidget(widget_name, self)
            dock.setObjectName(f"HorizontalDock_{widget_name}_{i}")
            dock.setFloating(False)
            dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetClosable
                | QDockWidget.DockWidgetFeature.DockWidgetMovable
                | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )
            # Remove custom title bar styling; use default.
            widget = widgets[widget_name]
            widget.setMinimumSize(minimum_view_size)
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            widget.setStyleSheet("border: 1px solid #B9B8B6;")
            dock.setWidget(widget)
            docks.append(dock)

        # Arrange the three docks horizontally.
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, docks[0])
        self.splitDockWidget(docks[0], docks[1], Qt.Orientation.Horizontal)
        self.splitDockWidget(docks[1], docks[2], Qt.Orientation.Horizontal)
        self.resizeDocks([docks[0], docks[1], docks[2]], [1, 1, 1], Qt.Orientation.Horizontal)

        for d in docks:
            d.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)

    def get_custom_settings(self):
        settings = {}
        docks = self.findChildren(QDockWidget)
        for dock in docks:
            object_name = dock.objectName()
            if object_name:
                settings[object_name] = {"width": dock.width(), "visible": dock.isVisible()}
        return settings

    def apply_custom_settings(self, settings):
        group = []
        sizes = []
        for object_name, info in settings.items():
            dock = self.findChild(QDockWidget, object_name)
            if dock:
                if not info.get("visible", True):
                    dock.hide()
                else:
                    dock.show()
                group.append(dock)
                sizes.append(info.get("width", dock.width()))
        if group:
            self.resizeDocks(group, sizes, Qt.Orientation.Horizontal)


class LayoutMixin:
    """
    Mixin for MainWin providing layout save/load/reset functionality.
    """

    def layout_save(self, layout_name: str | None = ""):
        if layout_name:
            layout = layout_name
        else:
            layout = self.context
        # save settings
        self.window_settings.setValue(f"{layout}Geometry", self.saveGeometry())
        self.window_settings.setValue(f"{layout}WindowState", self.saveState())

        # save custom settings
        custom = {}
        outer = {}
        for name in ["dockTop", "dockMiddle", "dockNormal", "dockInfo", "dockTrace", "dockSide"]:
            dock = self.findChild(QDockWidget, name)
            if dock:
                outer[name] = {"width": dock.width(), "visible": dock.isVisible()}
        custom["outer"] = outer
        custom["topAreaInner"] = self.topAreaInner.get_custom_settings()
        custom["middleAreaInner"] = self.middleAreaInner.get_custom_settings()
        custom["version"] = _LAYOUT_VERSION
        self.window_settings.setValue(layout, custom)

        self.window_settings.sync()

    def layout_exists(self, layout_name: str | None = "") -> bool:
        if layout_name:
            layout = layout_name
        else:
            layout = self.context
        geometry = self.window_settings.value(f"{layout}Geometry")
        window_state = self.window_settings.value(f"{layout}WindowState")
        return bool(geometry or window_state)

    def layout_load(self, layout_name: str | None = ""):
        if layout_name:
            layout = layout_name
        else:
            layout = self.context
        geometry = self.window_settings.value(f"{layout}Geometry")
        if geometry:
            self.restoreGeometry(geometry)
        window_state = self.window_settings.value(f"{layout}WindowState")
        if window_state:
            self.restoreState(window_state)

        custom = self.window_settings.value(layout)
        if not custom or custom.get("version") != _LAYOUT_VERSION:
            return
        if "outer" in custom:
            for name, info in custom["outer"].items():
                dock = self.findChild(QDockWidget, name)
                if dock:
                    if not info.get("visible", True):
                        dock.hide()
                    else:
                        dock.show()
                    self.resizeDocks(
                        [dock],
                        [info.get("width", dock.width())],
                        Qt.Orientation.Horizontal,
                    )
        if "topAreaInner" in custom:
            self.topAreaInner.apply_custom_settings(custom["topAreaInner"])
        if "middleAreaInner" in custom:
            self.middleAreaInner.apply_custom_settings(custom["middleAreaInner"])

    def layout_reset(self):
        # Show all docks
        for dock in [self.dockTop, self.dockMiddle, self.dockInfo, self.dockNormal, self.dockTrace, self.dockSide]:
            dock.setFloating(False)
            dock.show()

        # Re-establish default tab order: Info, Normal, Trace
        self.tabifyDockWidget(self.dockInfo, self.dockNormal)
        self.tabifyDockWidget(self.dockNormal, self.dockTrace)
        self.dockInfo.raise_()

        # Make visual and auditory views square, extra vertical space to bottom dock
        view_h = self.dockTop.widget().sizeHint().width() // 3  # approximate square height
        min_h = self.minimum_view_size.height()
        remaining = self.height() - (view_h * 2)
        self.resizeDocks(
            [self.dockTop, self.dockMiddle, self.dockInfo],
            [max(view_h, min_h), max(view_h, min_h), max(remaining, 200)],
            Qt.Orientation.Vertical,
        )

        # Restore inner-dock defaults
        def force_visible(custom_dict):
            new_dict = {}
            for key, info in custom_dict.items():
                new_info = info.copy()
                new_info["visible"] = True
                new_dict[key] = new_info
            return new_dict

        self.topAreaInner.apply_custom_settings(force_visible(self.default_top_custom_settings))
        self.middleAreaInner.apply_custom_settings(force_visible(self.default_middle_custom_settings))
