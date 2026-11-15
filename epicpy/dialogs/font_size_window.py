# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QFontDatabase, QShowEvent
from PySide6.QtWidgets import QApplication, QDialog

from epicpy.uifiles.font_size_ui import Ui_DialogFontSize
from epicpy.utils import config
from epicpy.utils.app_utils import clear_font


class FontSizeDialog(QDialog):
    def __init__(self):
        super(FontSizeDialog, self).__init__()
        self.ok = False
        self.ui = Ui_DialogFontSize()
        self.ui.setupUi(self)

        # replace designed font with application-wide font
        clear_font(self)

        font = QFont(QApplication.instance().font())
        self.ui.label_3.setText(
            f"<html>"
            f"<head/>"
            f"<body>"
            f"<p>"
            f'<span style=" font-size:20pt; font-weight:600;">'
            f"Application Font Name: {font.family()}"
            f"</span>"
            f"</p>"
            f"</body>"
            f"</html>"
        )

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)
        self.ui.spinBoxFontSize.valueChanged.connect(self.font_size_changed)

        if "fontsizewindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["fontsizewindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        # self.setLayout(self.ui.verticalLayout)

    def font_size_changed(self, change: int):
        self.setup_options(update_spin_box=False)

    def showEvent(self, event: QShowEvent) -> None:
        self.setup_options()
        super(FontSizeDialog, self).showEvent(event)

    def resizeEvent(self, event: QSize):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["fontsizewindow"] = [self.width(), self.height()]
        super(FontSizeDialog, self).resizeEvent(event)

    def setup_options(self, update_spin_box: bool = True):
        if update_spin_box:
            # usually called when dialog opened (pulls size from config)
            self.ui.spinBoxFontSize.setValue(int(config.app_cfg.font_size))
            font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
            font.setPixelSize(int(config.app_cfg.font_size))
            self.ui.plainTextEditFontSample.setFont(font)
        else:
            font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
            font.setPixelSize(self.ui.spinBoxFontSize.value())
            self.ui.plainTextEditFontSample.setFont(font)

        self.ui.plainTextEditFontSample.update()

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True
        config.app_cfg.font_size = self.ui.spinBoxFontSize.value()
        self.hide()
