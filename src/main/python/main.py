"""
This file is part of EPICpy, Created by Travis L. Seymour, PhD.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar.
If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
import datetime
import sys
import os
import platform

from loguru import logger as log

from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import qInstallMessageHandler

from fbs_runtime.application_context.PySide2 import ApplicationContext

import apputils
import config

from cppyysetup import setup_cppyy

os.environ["OUTDATED_IGNORE"] = "1"

# fix problem on mac starting with Big Sur (needed until I switch to pyside6)
os.environ["QT_MAC_WANTS_LAYER"] = "1"

apputils.CONTEXT = None

DONE = False


def handler(msg_type, msg_log_content, msg_string):
    # https://stackoverflow.com/questions/25660597/
    # hide-critical-pyqt-warning-when-clicking-a-checkboc#25681472
    ...


class AppContext(ApplicationContext):
    def __init__(self):
        super(AppContext, self).__init__()
        self.loading = None
        self.main_win = None

        apputils.CONTEXT = self

        config.get_app_config()
        config.get_device_config(None)

        fontDatabase = QFontDatabase()
        for font_file in (
            "Consolas_Regular.ttf",
            "Consolas_Bold.ttf",
            "Consolas_Italic.ttf",
            "Consolas_Bold_Italic.ttf",
        ):
            fontDatabase.addApplicationFont(
                self.get_resource("fonts", "Consolas", font_file)
            )

    def run(self):
        OS = platform.system()

        try:
            info, libname, headerpath, epiclib_files = setup_cppyy(self)
        except Exception as e:
            info, libname, headerpath, epiclib_files = None, None, None, None
            QMessageBox.critical(
                None,
                "Critical Library Error",
                f"Unable to locate or load the libEPIC shared library for OS Type "
                f'"{OS}" (epiclib/{libname}). EPICpy cannot start. \n[{e}]',
            )
            return 1

        import apputils

        apputils.LIBNAME = libname
        apputils.HEADERPATH = headerpath
        import mainwindow

        self.main_win = mainwindow.MainWin(self, epiclib_files, libname)
        self.app.lastWindowClosed.connect(shut_it_down)
        return self.app.exec_()


def shut_it_down():
    global DONE
    if DONE:
        return
    DONE = True
    config.save_config()
    config.save_app_config()
    sys.exit()


if __name__ == "__main__":

    # ------------------------------------------------------
    # if frozen, send log messages to file in config folder
    # ------------------------------------------------------

    if apputils.frozen():
        # Ignore all the log messages I sprinkled throughout the code while developing
        log.remove(None)  # should disable all logs

        # However, go ahead and send any error log messages to a log file
        # in the config folder
        config_dir = Path("~", ".config", "epicpy").expanduser()

        try:
            config_dir.mkdir(exist_ok=True)
        except Exception as e:
            print(f"WARNING: Unable to create config folder at {str(config_dir)}")

        log_file = Path(config_dir, "epicpy.log")
        log.add(log_file, level="ERROR")
        print(
            f"NOTE: Logging errors to file ({log_file.name}) "
            f"in config_dir ({str(config_dir.resolve())})"
        )

        # Disable pyqt warnings when not developing
        qInstallMessageHandler(handler)

    # ==============================
    # =====      Run App       =====
    # ==============================

    print("starting EPICpy at", datetime.datetime.now().ctime())
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
