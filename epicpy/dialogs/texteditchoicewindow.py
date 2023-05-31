"""
This file is part of the EPICpy source code. EPICpy is a tool for simulating 
human performance tasks using the EPIC computational cognitive architecture 
(David Kieras and David Meyer 1997a) using the Python programming language.
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
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from PyQt6.QtCore import QCoreApplication

from epicpy.uifiles.texteditorui import Ui_TextEditorChooser
from PyQt6.QtWidgets import QDialog
from epicpy.utils import config


class TextEditChoiceWin(QDialog):
    def __init__(self):
        super(TextEditChoiceWin, self).__init__()
        self.ok = False
        self.current_choice = ""

        self.ui = Ui_TextEditorChooser()
        self.ui.setupUi(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)

        self.ui.radioButtonBuiltIn.toggled.connect(self.radio_clicked)
        self.ui.radioButtonDefault.toggled.connect(self.radio_clicked)

        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )

        if "texteditchoicewindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["texteditchoicewindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        # self.setLayout(self.ui.verticalLayout)

        try:
            from epicpy.epiccoder.customeditor import CustomEditor
        except ImportError as e:
            print(f"ERROR accessing built-in editor modeule: {e}")
            self.ui.radioButtonBuiltIn.setEnabled(False)

    def radio_clicked(self):
        radio_button = self.sender()  # old way PyQt5?
        radio_button = QCoreApplication.sender(self)  # old PyQt5? self.sender()
        if radio_button.isChecked():
            if "built-in" in radio_button.text().lower():
                self.current_choice = "built-in"
                print("built-in chosen")
            else:
                self.current_choice = "default"
                print("default chosen")

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["texteditchoicewindow"] = [
            self.width(),
            self.height(),
        ]
        super(TextEditChoiceWin, self).resizeEvent(event)

    def setup_options(self):
        te_path = config.app_cfg.text_editor.strip().lower()
        self.current_choice = te_path

        if te_path == "built-in":
            self.ui.radioButtonBuiltIn.setChecked(True)
            self.ui.radioButtonDefault.setChecked(False)
        elif te_path == "default":
            self.ui.radioButtonBuiltIn.setChecked(False)
            self.ui.radioButtonDefault.setChecked(True)
        else:
            config.app_cfg.text_editor = "default"
            self.setup_options()

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        config.app_cfg.text_editor = self.current_choice
        self.ok = True
        self.hide()
