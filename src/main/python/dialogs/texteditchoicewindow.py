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
from pathlib import Path

from uifiles.texteditorui import Ui_TextEditorChooser
from PySide2.QtWidgets import QDialog, QMessageBox, QFileDialog
import config


class TextEditChoiceWin(QDialog):
    def __init__(self, context):
        super(TextEditChoiceWin, self).__init__()
        self.context = context
        self.ok = False

        self.ui = Ui_TextEditorChooser()
        self.ui.setupUi(self)

        self.ui.plainTextEditPath.setReadOnly(False)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)

        self.ui.checkBoxUseBuiltin.clicked.connect(self.clicked_checkbox)
        self.ui.toolButtonTextEditor.clicked.connect(self.clicked_dot_button)

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

        self.setLayout(self.ui.verticalLayout)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["texteditchoicewindow"] = [
            self.width(),
            self.height(),
        ]
        config.save_app_config(quiet=True)
        super(TextEditChoiceWin, self).resizeEvent(event)

    def setup_options(self):
        te_path = config.app_cfg.text_editor.strip()
        if te_path.lower() == "built-in":
            te_path = ""
        print(">>>", te_path)
        using_builtin = not te_path
        self.ui.checkBoxUseBuiltin.setChecked(using_builtin)
        self.ui.plainTextEditPath.setPlainText(te_path)

        self.ui.label.setEnabled(not using_builtin)
        self.ui.toolButtonTextEditor.setEnabled(not using_builtin)
        self.ui.plainTextEditPath.setEnabled(not using_builtin)

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        te_path = self.ui.plainTextEditPath.toPlainText().strip()

        if self.ui.checkBoxUseBuiltin.isChecked():
            config.app_cfg.text_editor = ""
            config.save_app_config(True)
            self.ok = True
            self.hide()
        elif te_path and Path(te_path).is_file():
            config.app_cfg.text_editor = te_path
            config.save_app_config(True)
            self.ok = True
            self.hide()
        else:
            self.ok = False
            ret = QMessageBox.critical(
                self,
                "Invalid Text Editor Path",
                f'"{te_path}" is not a valid text editor executable!\nEither choose '
                f"a new text editor, or choose the BUILT-IN text editor option.",
                QMessageBox.Ok,
            )

    def clicked_checkbox(self, event):
        self.ui.label.setEnabled(not event)
        self.ui.toolButtonTextEditor.setEnabled(not event)
        self.ui.plainTextEditPath.setEnabled(not event)

    def clicked_dot_button(self, event):
        start = self.ui.plainTextEditPath.toPlainText().strip()
        start = (
            start
            if Path(start).is_file() or Path(start).is_dir()
            else str(Path("~").expanduser().resolve())
        )
        file_name, o = QFileDialog.getOpenFileName(
            self, caption="Choose A Text Editor Executable", dir=start
        )
        if isinstance(file_name, (list, tuple)):
            file_name = file_name[0]

        if file_name:
            self.ui.plainTextEditPath.setPlainText(file_name)
