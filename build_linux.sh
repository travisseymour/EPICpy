#!/bin/bash

clear
rm -R build/
rm -R dist_linux/

# note: -windowed is REQuIreD on macos or you'll get that "framework" error

#                                                                                                    --onedir
#                                                                                                    --onefile
pyinstaller "/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy/EPICpy/src/main.py" --clean --noconfirm --onedir --windowed --distpath="dist_linux" --name "EPICpy" \
    --icon "/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy/EPICpy/resources/base/uiicons/Icon.ico" \
    --splash "/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy/EPICpy/resources/base/uiicons/Icon.png" \

    --hidden-import="wxpython" \
    --hidden-import="pandas" \
    --hidden-import="pkg_resources.py2_warn" \
    
    --add-data "/home/nogard/Dropbox/Documents/EPICSTUFF/EPICpy/EPICpy/resources;resources/" \
    
    --exclude-module "FixTk" \
    --exclude-module "tcl" \
    --exclude-module "tk" \
    --exclude-module "_tkinter" \
    --exclude-module "tkinter" \
    --exclude-module "Tkinter" \
    
    --hidden-import "cppyy_backend" \
    --hidden-import "pingouin" \
    --hidden-import "PyQt5.QtPrintSupport" \
    

open dist_linux/EPICpy

# --osx-bundle-identifier "com.travisseymour.epicpy"