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

import pandas as pd

from epicpy.uifiles.epiclibsettingsui import Ui_DialogEPICLibSettings
from PyQt6.QtWidgets import QDialog, QMessageBox
from functools import partial
from epicpy.utils import config


# FIXME: This window needs update now that were are no longer using cppyy.
#        Because literally no one wants it, I am very unlikely to convert the pre 2015
#        versions to EPIClib to the new pybind11 approach (way too much work).
#        Thus, this code will stay here in limbo until I produce a newer version of EPICLib.
#        Only then will there be any need to allow the user to choose anything.


class EPICLibSettingsWin(QDialog):
    def __init__(self, epiclib_files: pd.DataFrame, epiclib_name: str):
        raise NotImplementedError("This Function Has Been Disabled")

        super(EPICLibSettingsWin, self).__init__()
        self.epiclib_files = epiclib_files
        self.epiclib_name = epiclib_name
        self.selection = None

        self.ui = Ui_DialogEPICLibSettings()
        self.ui.setupUi(self)

        self.ui.listWidgetOptions.itemClicked.connect(self.clicked_item)
        self.ui.listWidgetOptions.itemDoubleClicked.connect(
            partial(self.clicked_item, press_ok=True)
        )
        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)

        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )

        if "epiclibsettingswindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["epiclibsettingswindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

        # self.setLayout(self.ui.verticalLayout)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["epiclibsettingswindow"] = [
            self.width(),
            self.height(),
        ]
        super(EPICLibSettingsWin, self).resizeEvent(event)

    def clicked_item(self, press_ok: bool = False):
        # self.selection = [item.text().split(' | ')[0] for item in self.ui.listWidgetOptions.selectedItems()][0]
        self.selection = self.ui.listWidgetOptions.currentRow()
        if press_ok:
            self.clicked_ok_button()

    def setup_options(self):
        self.ui.listWidgetOptions.insertItem(0, "Use Latest Version")
        if config.device_cfg.epiclib_version == "":
            self.ui.listWidgetOptions.setCurrentRow(0)

        for i, info in self.epiclib_files.iterrows():
            """
            pandas df, event.g:
               mac_ver   libdate                     filename
            2     1013  20160628  libEPIC_20160628.dylib
            3     1013  20141117  libEPIC_20141117.dylib
            """

            dt = str(info.libdate)
            year = dt[:4]
            month = dt[5:6]
            day = dt[-2:]
            label = f"{year}/{month}/{day} | {info.filename}"
            self.ui.listWidgetOptions.insertItem(i + 1, label)
            if config.device_cfg.epiclib_version and str(
                config.device_cfg.epiclib_version
            ) == str(info.libdate):
                self.ui.listWidgetOptions.setCurrentRow(i + 1)

    def clicked_cancel_button(self):
        # we close instead of hide so there are never any stale references to previous devices
        self.close()

    def clicked_ok_button(self):
        if self.selection is None:
            self.close()
        else:
            if self.selection == 0:
                epiclib_version = ""
            else:
                epiclib_version = str(
                    self.epiclib_files.iloc[self.selection - 1].libdate
                )

            config.device_cfg.epiclib_version = epiclib_version

            QMessageBox.information(
                None,
                "Notice About EPIClib Version Change",
                "You have altered the EPIClib version. This change will take place after EPICpy "
                "is restarted.",
            )

            self.close()
