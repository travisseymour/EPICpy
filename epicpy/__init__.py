import sys
from pathlib import Path
from typing import Optional

from qtpy.QtGui import QFont

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    pathEX = Path(sys._MEIPASS)
else:
    pathEX = Path(__file__).parent

app_font: Optional[QFont] = None
app_font_bold: Optional[QFont] = None


def set_app_font(font: QFont):
    global app_font
    app_font = font


def set_app_font_bold(font: QFont):
    global app_font_bold
    app_font_bold = font
