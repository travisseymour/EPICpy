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

from pathlib import Path
import datetime
import sys
import os
import platform

from loguru import logger as log

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import qInstallMessageHandler, QCoreApplication

from fbs_runtime.application_context.PyQt5 import ApplicationContext

import apputils
import config

from cppyysetup import setup_cppyy

os.environ["OUTDATED_IGNORE"] = "1"

# TODO: On MacOS BigSur, need to fix problem, but not sure if needed now that we switched to PyQt5
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

        fontDatabase.addApplicationFont(self.get_resource("fonts", "Consolas", "Consolas_Regular.ttf"))
        fontDatabase.addApplicationFont(self.get_resource("fonts", "Consolas", "Consolas_Bold.ttf"))
        fontDatabase.addApplicationFont(self.get_resource("fonts", "Consolas", "Consolas_Italic.ttf"))
        fontDatabase.addApplicationFont(self.get_resource("fonts", "Consolas", "Consolas_Bold_Italic.ttf"))

        fontDatabase.addApplicationFont(self.get_resource("fonts", "FiraCode", "FiraCode-Regular.ttf"))
        fontDatabase.addApplicationFont(self.get_resource("fonts", "FiraCode", "FiraCode-Bold.ttf"))
        fontDatabase.addApplicationFont(self.get_resource("fonts", "JetBrainsMono", "JetBrainsMono-Regular.ttf"))
        fontDatabase.addApplicationFont(self.get_resource("fonts", "JetBrainsMono", "JetBrainsMono-Bold.ttf"))

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

        RUN_TESTS = True
        if RUN_TESTS:
            from cppinclude import epiclib_include

            epiclib_include("Utility Classes/Symbol.h")
            epiclib_include("Utility Classes/Output_tee.h")
            epiclib_include("Standard_Symbols.h")
            epiclib_include("PPS/PPS Interface classes/PPS_globals.h")

            from cppyy.gbl import Normal_out, Trace_out, PPS_out
            from cppyy.gbl import std
            from epiclibtests import run_tests
            run_tests()
            sys.exit()

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

    # -------------------------------------------------------------------------
    # init QSettings once so we can use default constructor throughout project
    # -------------------------------------------------------------------------
    # TODO: At the moment, this is underutilized and instead we're managing all settings manually in the config module
    #       However, it *is* being used, e.g., in the built-in editor.
    QCoreApplication.setOrganizationName("TravisSeymour")
    QCoreApplication.setOrganizationDomain("travisseymour.com")
    QCoreApplication.setApplicationName("EPICpy")

    # ==============================
    # =====      Run App       =====
    # ==============================


    print("starting EPICpy at", datetime.datetime.now().ctime())
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
