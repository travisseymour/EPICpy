import sys
from pathlib import Path

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    pathEX = Path(sys._MEIPASS)
else:
    pathEX = Path(__file__).parent

