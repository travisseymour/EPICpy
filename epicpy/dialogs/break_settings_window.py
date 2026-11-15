# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from epiclibcpp.epiclib import Model, Symbol
from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QListWidgetItem

from epicpy.uifiles.break_settings_ui import Ui_DialogRuleBreak
from epicpy.utils import config
from epicpy.utils.app_utils import clear_font


class BreakSettingsWin(QDialog):
    def __init__(self, model):
        super(BreakSettingsWin, self).__init__()
        self.model: Model = model
        self.ui = Ui_DialogRuleBreak()
        self.ui.setupUi(self)

        clear_font(self)

        self.ui.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        self.ui.pushButtonOK.clicked.connect(self.clicked_ok_button)
        self.ui.checkBoxEnableRuleBreaks.stateChanged.connect(self.clicked_rule_break_checkbox)

        self.ok: bool = False

        self.all_rules = [break_rule.str() for break_rule in self.model.get_rule_names()]
        self.break_rules = [break_rule.str() for break_rule in self.model.get_break_rule_names()]

        # self.setLayout(self.ui.verticalLayout)

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
        super(BreakSettingsWin, self).resizeEvent(event)

    def setup_options(self):
        font = QApplication.instance().font()
        for rule_name in self.all_rules:
            item = QListWidgetItem(self.ui.listWidgetRules)
            item.setFont(font)
            cb = QCheckBox(rule_name)
            cb.setFont(font)
            cb.setChecked(rule_name in self.break_rules)
            self.ui.listWidgetRules.setItemWidget(item, cb)

        self.ui.checkBoxEnableRuleBreaks.setChecked(self.model.get_break_enabled())

    def clicked_rule_break_checkbox(self, state):
        self.ui.listWidgetRules.setEnabled(bool(state))
        self.model.set_break_enabled(bool(state))

    def clicked_cancel_button(self):
        self.ok = False
        self.close()

    def clicked_ok_button(self):
        self.ok = True
        states = [
            self.ui.listWidgetRules.itemWidget(self.ui.listWidgetRules.item(index)).checkState()
            for index in range(self.ui.listWidgetRules.count())
        ]
        rule_states = list(zip(self.all_rules, states))
        for rule_name, state in rule_states:
            self.model.set_rule_break_state(Symbol(rule_name), bool(state.value))
        self.close()
