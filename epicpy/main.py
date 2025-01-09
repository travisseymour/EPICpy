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

import os
import platform
from importlib.resources import files, as_file

os.environ["OUTDATED_IGNORE"] = "1"
if platform.platform().split("-")[1].startswith("10."):
    os.environ["QT_MAC_WANTS_LAYER"] = "1"

# os.environ["QT_DEBUG_PLUGINS"] = "1" # for more info when there are plugin load errors


import datetime
import ctypes.wintypes
import signal
import sys
import os
import re
import subprocess
from pathlib import Path
from shutil import copyfile
from loguru import logger as log

from qtpy.QtGui import QFont
from qtpy.QtGui import QFontDatabase
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import qInstallMessageHandler, QCoreApplication

from epicpy.utils.apputils import get_resource, frozen
from epicpy.utils import config
from epicpy import set_app_font, set_app_font_bold

# epiclib name (epiclib.so) is same on mac and linux.
# just in case we were recently running on a different os,
# let's copy the right one for this system
try:
    # Determine the source file based on the platform
    if platform.system() == "Darwin":
        if platform.machine() == "x86_64":
            source = files("epicpy").joinpath(Path("epiclib") / "epiclib_macos.so")
        else:
            source = files("epicpy").joinpath(Path("epiclib") / "epiclib_macos_arm.so")
    elif platform.system() == "Linux":
        source = files("epicpy").joinpath(Path("epiclib") / "epiclib_linux.so")
    else:
        source = None

    if source:
        # Define the destination path
        destination = Path("epiclib") / "epiclib.so"

        # Safely copy the resource to the destination
        with as_file(source) as source_path:
            copyfile(source_path, destination)

except Exception as e:
    print(f"Error trying to reset epiclib.so for {platform.system()}: '{e}'")

DONE = False


# dragon = Path('C:\\Users\\nogard\\Desktop\\mylog.txt')
# dragon.write_text(f'{datetime.datetime.now().ctime()}')
# def mog(msg:str):
#     global dragon
#     dragon.write_text(dragon.read_text() + '\n' + msg)


def pyqt_warning_handler(msg_type, msg_log_content, msg_string):
    # https://stackoverflow.com/questions/25660597/
    # hide-critical-pyqt-warning-when-clicking-a-checkboc#25681472
    ...


# ==================================================
# ==========  SETUP SIGSEGV HANDLER ================
# ==================================================
# epiclib inevitably leads to segmentation fault on exit.
# all of this is to ignore that. It isn't really too
# consequential on Windows and Linux, but on Macos, not
# handling SIGSEGV causes EPICpy to hang, which requires
# the user to issue a force-quit to the application.
# When we port epiclib to Python, this will no longer be necessary.
# This is why it's getting a visual fence here

OS = platform.system()


# Define the C signal handler function
def segfault_handler(signal, frame):
    log.warning("Segmentation fault occurred")
    os._exit(1)
    sys.exit(1)


if OS in ("Linux", "Darwin"):
    # Define the C function prototype
    handler_func_type = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_void_p)

    # Convert the Python signal handler to a C function pointer
    handler_func_ptr = handler_func_type(segfault_handler)

    # Get the underlying C handle for the SIGSEGV signal
    SIGSEGV = signal.SIGSEGV.value

    # Set the signal handler using ctypes
    if OS == "Linux":
        output = subprocess.check_output(["ldd", "/bin/ls"]).decode("utf-8")
        # Extract the path for libc.so.[version] using regular expression
        pattern = r"libc\.so\.\d+\s*=>\s*(.*?)\s"
        match = re.search(pattern, output)
        if match:
            try:
                libc_path = match.group(1)
                if not Path(libc_path).is_file():
                    raise FileExistsError
            except Exception as e:
                libc_path = ""
                log.warning(
                    f"Extracted bad or unreadable libc path: {libc_path}: {e}. Unable to install SIGSEGV handler."
                )
        else:
            libc_path = ""
            log.warning("ERROR: Cannot find libc path. Unable to install SIGSEGV handler.")
    elif OS == "Darwin":
        libc_path = "/usr/lib/libc.dylib"  # Update with the correct path on macOS
    else:
        # Unknown OS, do nothing
        libc_path = ""

    if libc_path:
        libc = ctypes.CDLL(libc_path)
        libc.signal(SIGSEGV, handler_func_ptr)
elif OS == "Windows":
    # Define the C function prototype
    # handler_func_type = ctypes.CFUNCTYPE(ctypes.wintypes.BOOL, ctypes.c_ulong)
    handler_func_type = ctypes.CFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.DWORD)

    # Convert the Python signal handler to a C function pointer
    handler_func_ptr = handler_func_type(segfault_handler)

    # Set the signal handler using ctypes on Windows
    ctypes.windll.kernel32.SetConsoleCtrlHandler(handler_func_ptr, True)
else:
    # Unknown OS, do nothing
    ...

# To test on Linux or Macos, run this:
# ctypes.string_at(0)
# NOTE: I can't figure out how to test on Windows.
# string_at(0) doesn't handle anything on Windows.

# ==================================================
# ==================================================

# init config
config.app_cfg = config.AppConfig()
config.device_cfg = config.DeviceConfig()


def start_ui(app: QApplication):
    # load in any stored config data
    config.get_app_config()
    config.get_device_config(None)

    # prepare the default font
    font_id = QFontDatabase.addApplicationFont(str(get_resource("fonts", "FiraCode", "FiraCode-Regular.ttf").resolve()))
    font = QFont()
    if font_id:
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        font_family = font_families[0] if font_families else None
        if font_family:
            font.setFamily(font_family)
        else:
            font.setFamily(font.defaultFamily())
    else:
        font.setFamily(font.defaultFamily())
    font.setPointSize(12)

    # Set the font for the application
    QApplication.instance().setFont(font)

    # Store global fonts for later use
    set_app_font(font)
    font_bold = QFont(font)
    font_bold.setBold(True)
    set_app_font_bold(font_bold)

    from epicpy.windows import mainwindow

    _ = mainwindow.MainWin(app)
    app.lastWindowClosed.connect(shut_it_down)
    try:
        return app.exec()
    except AttributeError:
        return app.exec_()


def shut_it_down():
    global DONE
    if DONE:
        return
    DONE = True
    sys.exit()


def main():
    import sys
    from pathlib import Path

    print('Loading EPICpy, please wait...')

    application = QApplication([])

    # ------------------------------------------------------
    # if frozen, send log messages to file in config folder
    # ------------------------------------------------------

    if frozen():
        # Ignore all the log messages I sprinkled throughout the code while developing
        log.remove(None)  # should disable all logs

        # However, go ahead and send any error log messages to a log file in the config folder
        config_dir = config.get_config_dir()

        log_file = Path(config_dir, "epicpy.log")
        log.add(log_file, level="ERROR")
        print(f"NOTE: Logging errors to file ({log_file.name}) " f"in config_dir ({str(config_dir.resolve())})")
        # Disable pyqt warnings when not developing
        qInstallMessageHandler(pyqt_warning_handler)

    # -------------------------------------------------------------------------
    # init QSettings once so we can use default constructor throughout project
    # -------------------------------------------------------------------------
    QCoreApplication.setOrganizationName("TravisSeymour")
    QCoreApplication.setOrganizationDomain("travisseymour.com")
    QCoreApplication.setApplicationName("EPICpy")

    # ==============================
    # =====      Run App       =====
    # ==============================

    print("starting EPICpy at", datetime.datetime.now().ctime())
    exit_code = start_ui(application)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
