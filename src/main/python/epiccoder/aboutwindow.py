"""
EPICcoder is a minimal programmer's text editor created for use with the
EPIC, EPICpy and pyEPIC simulation environments.
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
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5.QtGui import QPixmap

from epiccoder.aboutui import Ui_aboutDialog
from PyQt5.QtWidgets import QDialog
from epiccoder.version import __version__


class AboutWin(QDialog):
    def __init__(self, parent, context):
        super(AboutWin, self).__init__(parent=parent)

        self.ui = Ui_aboutDialog()
        self.ui.setupUi(self)

        self.ui.pushButtonClose.clicked.connect(self.close)

        html = self.ui.textBrowser.toHtml()
        html = html.replace("** EPICcoder **", f"EPICcoder v{__version__}")
        self.ui.textBrowser.setHtml(html)

        pic_file = context.get_resource("uiicons", "app-icon.svg")
        pixmap = QPixmap(pic_file)
        self.ui.labelEPICicon.setPixmap(pixmap.scaled(self.ui.labelEPICicon.size()))
