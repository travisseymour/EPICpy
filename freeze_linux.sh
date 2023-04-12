#!/bin/bash

clear
rm -R ./dist_linux/
rm -R ./build/

#                                            --onedir
#                                            --onefile

pyinstaller "src/main.py" --clean --noconfirm --onefile --windowed --name "EPICpy" \
    --distpath "./dist_linux" \
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

rm EPICpy.spec
open ./dist_linux/

