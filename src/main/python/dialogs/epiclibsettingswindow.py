"""
This file is part of EPICpy, Created by Travis L. Seymour, PhD.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar.
If not, see <https://www.gnu.org/licenses/>.
"""

import pandas as pd

from uifiles.epiclibsettingsui import Ui_DialogEPICLibSettings
from PySide2.QtWidgets import QDialog, QMessageBox
from functools import partial
import config


class EPICLibSettingsWin(QDialog):
    def __init__(self, context, epiclib_files: pd.DataFrame, epiclib_name: str):
        super(EPICLibSettingsWin, self).__init__()
        self.context = context
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

        self.setLayout(self.ui.verticalLayout)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["epiclibsettingswindow"] = [
            self.width(),
            self.height(),
        ]
        config.save_app_config(quiet=True)
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
            pandas df, e.g:
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
