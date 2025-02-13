import sys
import time
from typing import Optional

from PySide6.QtWidgets import QApplication, QMainWindow, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, QTimer

from epicpy.utils import config
from epicpy.utils.apputils import get_resource


class AppLoader(QThread):
    """Background thread to simulate app loading."""

    def run(self):
        time.sleep(3)  # Simulate heavy initialization


class SplashScreen(QSplashScreen):
    """Custom splash screen that auto-closes when the main window is visible."""

    def __init__(self, main_window: Optional[QMainWindow] = None):
        original_pixmap = QPixmap(get_resource("images", "splash.png"))

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
