#!/bin/bash

clear
rm -R ./dist_macos/
rm -R ./build/

# note: -windowed is REQuIreD on macos or you'll get that "framework" error
#                                            --onedir
#                                            --onefile

pyinstaller "src/main.py" --clean --noconfirm --onefile --windowed --name "EPICpy" \
    --distpath "./dist_macos" \
    --workpath "./build" \
    --paths "src/dialogs:src/epiccoder:src/uifiles:src/views:src/epiclib" \
    --icon "./resources/base/uiicons/Icon.ico" \
    --add-data "./resources:resources/" \
    --exclude-module "FixTk" \
    --exclude-module "tcl" \
    --exclude-module "tk" \
    --exclude-module "_tkinter" \
    --exclude-module "tkinter" \
    --exclude-module "Tkinter" \
    --hidden-import "cppyy_backend" \
    --hidden-import "pingouin" \
    --hidden-import "ulid2" \
    --hidden-import="pandas" \
    --hidden-import="pkg_resources.py2_warn" \
    --hidden-import "PyQt5.QtPrintSupport" \
    --osx-bundle-identifier "com.travisseymour.epicpy"

rm EPICpy.spec
open ./dist_macos/

