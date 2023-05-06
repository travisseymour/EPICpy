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

from epicpy2.utils import config
from epicpy2.uifiles.loggingui import Ui_DialogLoggingSettings
from PyQt5.QtWidgets import QDialog, QFileDialog
from pathlib import Path
from functools import partial


class LoggingSettingsWin(QDialog):
    def __init__(self):
        super(LoggingSettingsWin, self).__init__()
        self.ok = False
        self.ui = Ui_DialogLoggingSettings()
        self.ui.setupUi(self)

        self.device_stem = Path(config.device_cfg.device_file).stem

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)
        self.ui.toolButtonNormalOut.clicked.connect(
            partial(self.choose_log_file, file_type="normal")
        )
        self.ui.toolButtonTraceOut.clicked.connect(
            partial(self.choose_log_file, file_type="trace")
        )

        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )

        # self.setLayout(self.ui.verticalLayout)

    @staticmethod
    def default_log_filename(file_type: str) -> str:
        kind = file_type.lower().strip()
        assert kind in ("trace", "normal", "stats")

        assert config.device_cfg.device_file

        device_path = Path(config.device_cfg.device_file).resolve()

        if device_path.parent.is_dir():
            start_dir = device_path.parent
            start_file = f"{start_dir.stem}_{kind}_output.txt"
        else:
            start_dir = Path.home().expanduser()
            start_file = f"{kind}_output.txt"

        return str(Path(start_dir, start_file))

    def choose_log_file(self, file_type: str):
        kind = file_type.lower().strip()
        assert kind in ("trace", "normal")
        if kind == "normal":
            start_dir = Path(config.device_cfg.normal_out_file)
        else:
            start_dir = Path(config.device_cfg.trace_out_file)

        if start_dir.is_file():
            start_dir = start_dir.parent
        elif Path(config.device_cfg.device_file).is_file():
            start_dir = Path(config.device_cfg.device_file).parent
        else:
            start_dir = Path().home()

        file, _ = QFileDialog.getSaveFileName(
            self,
            f"Specify {kind.title()} Output File",
            str(start_dir),
            "Text files (*.txt);;All Files (*)",
            "Text files (*.txt)",
        )
        if file:
            if kind == "normal":
                config.device_cfg.normal_out_file = file
                self.ui.plainTextEditNormalOutFile.setPlainText(file)
            else:
                config.device_cfg.trace_out_file = file
                self.ui.plainTextEditTraceOutFile.setPlainText(file)

    def setup_options(self):
        if not config.device_cfg.normal_out_file:
            config.device_cfg.normal_out_file = self.default_log_filename("normal")

        if not config.device_cfg.trace_out_file:
            config.device_cfg.trace_out_file = self.default_log_filename("trace")

        self.ui.plainTextEditNormalOutFile.setPlainText(
            config.device_cfg.normal_out_file
        )
        self.ui.plainTextEditTraceOutFile.setPlainText(config.device_cfg.trace_out_file)

        self.ui.checkBoxLogNormalOut.setChecked(config.device_cfg.log_normal_out)
        self.ui.checkBoxLogTraceOut.setChecked(config.device_cfg.log_trace_out)

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True
        config.device_cfg.log_normal_out = self.ui.checkBoxLogNormalOut.isChecked()
        config.device_cfg.log_trace_out = self.ui.checkBoxLogTraceOut.isChecked()
        config.device_cfg.normal_out_file = (
            self.ui.plainTextEditNormalOutFile.toPlainText()
        )
        config.device_cfg.trace_out_file = (
            self.ui.plainTextEditTraceOutFile.toPlainText()
        )
        self.hide()
