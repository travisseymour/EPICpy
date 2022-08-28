"""
This file is part of EPICpy, Created by Travis L. Seymour, PhD.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with EPICpy.
If not, see <https://www.gnu.org/licenses/>.
"""

from PySide2.QtGui import QPixmap

from uifiles.aboutui import Ui_aboutDialog
from PySide2.QtWidgets import QDialog
import version


class AboutWin(QDialog):
    def __init__(self, parent, context):
        super(AboutWin, self).__init__(parent=parent)

        self.ui = Ui_aboutDialog()
        self.ui.setupUi(self)

        self.ui.pushButtonClose.clicked.connect(self.close)

        html = self.ui.textBrowser.toHtml()
        html = html.replace("** EPICpy **", f"EPICpy v{version.__version__}")
        self.ui.textBrowser.setHtml(html)

        pic_file = context.get_resource("images", "EPIC_TINY.png")
        pixmap = QPixmap(pic_file)
        self.ui.labelEPICicon.setPixmap(pixmap.scaled(self.ui.labelEPICicon.size()))
