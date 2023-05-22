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

os.environ["OUTDATED_IGNORE"] = "1"
# TODO: vvv On MacOS BigSur, need to fix problem, but not sure if needed now that we switched to PyQt5
os.environ["QT_MAC_WANTS_LAYER"] = "1"

import datetime
import ctypes.wintypes
import signal
import sys
import os
import platform
import re
import subprocess
from pathlib import Path
from loguru import logger as log

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import qInstallMessageHandler, QCoreApplication

from epicpy2.utils.apputils import get_resource, frozen
from epicpy2.utils import config

# some older versions of Linux won't be able to use epiccoder
try:
    from epicpy2.epiccoder.customeditor import CustomEditor
except ImportError:
    config.app_cfg.text_editor = ""
    config.save_app_config(True)


DONE = False


# def mog(msg:str):
#     global dragon
#     dragon.write_text(dragon.read_text() + '\n' + msg)
# dragon = Path('C:\\Users\\nogard\\Desktop\\mylog.txt')
# dragon.write_text(f'{datetime.datetime.now().ctime()}')


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


if OS in ('Linux', 'Darwin'):
    # Define the C function prototype
    handler_func_type = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_void_p)

    # Convert the Python signal handler to a C function pointer
    handler_func_ptr = handler_func_type(segfault_handler)

    # Get the underlying C handle for the SIGSEGV signal
    SIGSEGV = signal.SIGSEGV.value

    # Set the signal handler using ctypes
    if OS == 'Linux':
        output = subprocess.check_output(['ldd', '/bin/ls']).decode('utf-8')
        # Extract the path for libc.so.[version] using regular expression
        pattern = r'libc\.so\.\d+\s*=>\s*(.*?)\s'
        match = re.search(pattern, output)
        if match:
            try:
                libc_path = match.group(1)
                if not Path(libc_path).is_file():
                    raise FileExistsError
            except Exception as e:
                libc_path = ''
                log.warning(f"Extracted bad or unreadable libc path: {libc_path}: {e}. Unable to install SIGSEGV handler.")
        else:
            libc_path = ''
            log.warning("ERROR: Cannot find libc path. Unable to install SIGSEGV handler.")
    elif OS == 'Darwin':
        libc_path = '/usr/lib/libc.dylib'  # Update with the correct path on macOS
    else:
        # Unknown OS, do nothing
        libc_path = ''

    if libc_path:
        libc = ctypes.CDLL(libc_path)
        libc.signal(SIGSEGV, handler_func_ptr)
elif OS == 'Windows':
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

def start_ui(app: QApplication):
    global LIBNAME, HEADERPATH
    config.get_app_config()
    config.get_device_config(None)
    fontDatabase = QFontDatabase()
    fontDatabase.addApplicationFont(str(get_resource("fonts", "Consolas", "Consolas_Regular.ttf")))
    fontDatabase.addApplicationFont(str(get_resource("fonts", "Consolas", "Consolas_Bold.ttf")))
    fontDatabase.addApplicationFont(str(get_resource("fonts", "Consolas", "Consolas_Italic.ttf")))
    fontDatabase.addApplicationFont(str(get_resource("fonts", "Consolas", "Consolas_Bold_Italic.ttf")))

    fontDatabase.addApplicationFont(str(get_resource("fonts", "FiraCode", "FiraCode-Regular.ttf")))
    fontDatabase.addApplicationFont(str(get_resource("fonts", "FiraCode", "FiraCode-Bold.ttf")))
    fontDatabase.addApplicationFont(str(get_resource("fonts", "JetBrainsMono", "JetBrainsMono-Regular.ttf")))
    fontDatabase.addApplicationFont(str(get_resource("fonts", "JetBrainsMono", "JetBrainsMono-Bold.ttf")))

    from epicpy2.windows import mainwindow

    main_win = mainwindow.MainWin(app)
    app.lastWindowClosed.connect(shut_it_down)
    return app.exec_()


def shut_it_down():
    global DONE
    if DONE:
        return
    DONE = True
    config.save_config()
    config.save_app_config()
    sys.exit()


def main():
    import sys
    from pathlib import Path

    application = QApplication([])

    # ------------------------------------------------------
    # if frozen, send log messages to file in config folder
    # ------------------------------------------------------

    if frozen():
        # Ignore all the log messages I sprinkled throughout the code while developing
        log.remove(None)  # should disable all logs

        # However, go ahead and send any error log messages to a log file
        # in the config folder
        config_dir = Path("~", ".config", "epicpy").expanduser()

        try:
            config_dir.mkdir(exist_ok=True)
        except Exception as e:
            print(f"WARNING: Unable to create config folder at {str(config_dir)}: {e}")

        log_file = Path(config_dir, "epicpy.log")
        log.add(log_file, level="ERROR")
        print(
            f"NOTE: Logging errors to file ({log_file.name}) "
            f"in config_dir ({str(config_dir.resolve())})"
        )
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
