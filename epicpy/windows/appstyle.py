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

import qdarkstyle

# from PySide6.QtGui import QPalette, QColor


def set_light_style(app_instance):
    app_instance.setStyle("Fusion")
    # palette = QPalette()
    # palette.setColor(QPalette.Window, QColor(240, 240, 240))
    # palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    # palette.setColor(QPalette.Base, QColor(255, 255, 255))
    # palette.setColor(QPalette.AlternateBase, QColor(233, 231, 227))
    # palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    # palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    # palette.setColor(QPalette.Text, QColor(0, 0, 0))
    # palette.setColor(QPalette.Button, QColor(240, 240, 240))
    # palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    # palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    # app_instance.setPalette(palette)
    # Clear any style sheet that might conflict.
    app_instance.setStyleSheet("")


def set_dark_style(app_instance):
    app_instance.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
