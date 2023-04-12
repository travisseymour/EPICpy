cls
deltree /S/Q dist_windows
deltree /S/Q build

pyinstaller "src\main.py" --clean --noconfirm --onefile --windowed --name "EPICpy" ^
    --distpath "dist_windows" ^
    --workpath "build" ^
    --paths "src\dialogs;src\epiccoder;src\uifiles;src\views;src\epiclib" ^
    --icon "resources\base\uiicons\Icon.ico" ^
    --add-data "resources;resources" ^
    --exclude-module "FixTk" ^
    --exclude-module "tcl" ^
    --exclude-module "tk" ^
    --exclude-module "_tkinter" ^
    --exclude-module "tkinter" ^
    --exclude-module "Tkinter" ^
    --hidden-import "pingouin" ^
    --hidden-import "ulid2" ^
    --hidden-import="pandas" ^
    --hidden-import="pkg_resources.py2_warn" ^
    --hidden-import "PyQt5.QtPrintSupport"

del EPICpy.spec
explorer dist_windows
