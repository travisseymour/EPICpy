# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog

from epicpy import __version__
from epicpy.uifiles.about_ui import Ui_aboutDialog
from epicpy.utils.resource_utils import get_resource


class AboutWin(QDialog):
    def __init__(self, parent):
        super(AboutWin, self).__init__(parent=parent)

        self.ui = Ui_aboutDialog()
        self.ui.setupUi(self)

        self.ui.pushButtonClose.clicked.connect(self.close)

        html = self.ui.textBrowser.toHtml()
        html = html.replace("** EPICpy **", f"EPICpy v{__version__}")
        self.ui.textBrowser.setHtml(html)

        pic_file = str(get_resource("images", "EPIC_TINY.png"))
        pixmap = QPixmap(str(pic_file))
        self.ui.labelEPICicon.setPixmap(pixmap.scaled(self.ui.labelEPICicon.size()))
