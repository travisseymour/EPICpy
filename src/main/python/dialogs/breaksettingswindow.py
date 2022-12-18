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

import config
from uifiles.breaksettingsui import Ui_DialogRuleBreak
from PyQt5.QtWidgets import QDialog, QCheckBox, QListWidgetItem

from apputils import LIBNAME, unpack_param_string
from cppinclude import epiclib_include
import cppyy

epiclib_include("Model-View Classes/Model.h")
epiclib_include("Utility Classes/Symbol.h")

from cppyy.gbl import Model
from cppyy.gbl import Symbol

class BreakSettingsWin(QDialog):
    def __init__(self, context, model):
        super(BreakSettingsWin, self).__init__()
        self.context = context
        self.model: Model = model
        self.ui = Ui_DialogRuleBreak()
        self.ui.setupUi(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)
        self.ui.checkBoxEnableRuleBreaks.stateChanged.connect(
            self.clicked_rule_break_checkbox
        )

        self.all_rules = [str(break_rule) for break_rule in self.model.get_rule_names()]
        self.break_rules = [
            str(break_rule) for break_rule in self.model.get_break_rule_names()
        ]

        self.setLayout(self.ui.verticalLayout)

        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )

        if "breaksettingswindow" in config.app_cfg.dialog_size:
            w, h = config.app_cfg.dialog_size["breaksettingswindow"]
            w = max(w, self.minimumWidth())
            w = min(w, self.maximumWidth())
            h = max(h, self.minimumHeight())
            h = min(h, self.maximumHeight())
            self.resize(w, h)

    def resizeEvent(self, event):
        # self.resized.emit()  # in case you want to send this signal somewhere else
        config.app_cfg.dialog_size["breaksettingswindow"] = [
            self.width(),
            self.height(),
        ]
        config.save_app_config(quiet=True)
        super(BreakSettingsWin, self).resizeEvent(event)

    def setup_options(self):

        for rule_name in self.all_rules:
            item = QListWidgetItem(self.ui.listWidgetRules)
            cb = QCheckBox(rule_name)
            cb.setChecked(rule_name in self.break_rules)
            self.ui.listWidgetRules.setItemWidget(item, cb)

        self.ui.checkBoxEnableRuleBreaks.setChecked(self.model.get_break_enabled())

    def clicked_rule_break_checkbox(self, state):
        self.ui.listWidgetRules.setEnabled(bool(state))
        self.model.set_break_enabled(bool(state))

    def clicked_cancel_button(self):
        self.close()

    def clicked_ok_button(self):
        self.ok = True
        states = [
            self.ui.listWidgetRules.itemWidget(
                self.ui.listWidgetRules.item(index)
            ).checkState()
            for index in range(self.ui.listWidgetRules.count())
        ]
        rule_states = list(zip(self.all_rules, states))
        for rule_name, state in rule_states:
            self.model.set_rule_break_state(Symbol(rule_name), bool(state))
        self.close()
