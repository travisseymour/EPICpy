#!/bin/bash

clear
rm -R build/
rm -R dist_linux/

# note: -windowed is REQuIreD on macos or you'll get that "framework" error
#--add-data="session.json:." \

pyinstaller addquiztogradesheet.py --clean --onefile --windowed --distpath="dist_linux" \
    --hidden-import="wxpython" \
    --hidden-import="pandas" \
    --hidden-import="pkg_resources.py2_warn" \
    --add-data="test_a/:test_a" \
    --add-data="test_b/:test_b" \
    --add-data="icon/:icon" \
    --exclude-module="tkinter" \
    --icon=structure_by_Eucalyp_at_flaticon.icns \

open dist_mac/addquiztogradesheet.app
#./dist_mac/addquiztogradesheet
