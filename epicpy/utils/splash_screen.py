"""
This file is part of the EPICpy source code. EPICpy is a tool for simulating
human performance tasks using the EPIC computational cognitive architecture
(David Kieras and David Meyer 1997a) using the Python programming language.
Copyright (C) 2022-2026 Travis L. Seymour, PhD

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
import time
from typing import Optional

from qtpy.QtCore import Qt, QThread, QTimer
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QApplication, QMainWindow, QSplashScreen

from epicpy.utils import config
from epicpy.utils.resource_utils import get_resource


class AppLoader(QThread):
    """Background thread to simulate app loading."""

    def run(self):
        time.sleep(3)  # Simulate heavy initialization


class SplashScreen(QSplashScreen):
    """Custom splash screen that auto-closes when the main window is visible."""

    def __init__(self, main_window: Optional[QMainWindow] = None):
        original_pixmap = QPixmap(str(get_resource("images", "splash.png")))

        # Scale to 3/4 (75%) of original size
        scaled_pixmap = original_pixmap.scaled(
            int(original_pixmap.width() * 0.55),
            int(original_pixmap.height() * 0.55),
            Qt.AspectRatioMode.KeepAspectRatio,  # Ensures the aspect ratio is maintained
            Qt.TransformationMode.SmoothTransformation,  # Provides better quality scaling
        )

        super().__init__(scaled_pixmap, Qt.WindowType.WindowStaysOnTopHint)
        self.main_window = main_window
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_main_window if main_window is not None else self.check_app_ready)
        self.check_timer.start(100)  # Check every 100ms

    def check_main_window(self):
        if self.main_window.isVisible():
            self.check_timer.stop()  # Stop checking
            self.hide()
            self.close()  # Close splash screen once main window is ready

    def check_app_ready(self):
        if config.APP_READY:
            self.check_timer.stop()
            self.hide()
            self.close()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App")
        self.setGeometry(100, 100, 800, 600)


def main():
    app = QApplication(sys.argv)

    # Create and show the main window immediately
    main_window = MainWindow()

    # Create splash screen that will close itself when main window appears
    splash = SplashScreen(main_window)
    splash.show()

    # Start a background loading thread (simulating a long startup process)
    loader = AppLoader()
    loader.finished.connect(main_window.show)  # Show main window when loading is done
    loader.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
