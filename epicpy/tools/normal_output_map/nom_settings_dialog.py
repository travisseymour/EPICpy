# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from epicpy.utils.app_utils import clear_font

from .parser import (
    DEFAULT_RESPONSE_CLAUSE,
    DEFAULT_STIMULUS_ONSET_CLAUSE,
    DEFAULT_TRIAL_START_RULE,
)


class NOMSettingsDialog(QDialog):
    """Dialog for configuring Normal Output Map parsing parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ok = False
        self.setWindowTitle("Normal Output Map Settings")
        self.setMinimumWidth(500)

        # Load saved settings
        self._settings = QSettings("EPICpy", "NormalOutputMap")

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Description
        desc = QLabel(
            "Configure the parsing parameters for the Normal Output Map.\n"
            "These patterns are used to identify trial boundaries, stimulus onset, and responses."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: gray;")
        layout.addWidget(desc)

        # Form layout for parameters
        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        # Trial start rule
        self.trial_start_rule_edit = QLineEdit()
        self.trial_start_rule_edit.setPlaceholderText(DEFAULT_TRIAL_START_RULE)
        form_layout.addRow("Trial Start Rule:", self.trial_start_rule_edit)

        trial_help = QLabel("Rule name that marks the start of each trial (e.g., TRIAL_mfg)")
        trial_help.setStyleSheet("color: gray; font-size: smaller;")
        form_layout.addRow("", trial_help)

        # Stimulus onset clause
        self.stimulus_onset_edit = QLineEdit()
        self.stimulus_onset_edit.setPlaceholderText(DEFAULT_STIMULUS_ONSET_CLAUSE)
        form_layout.addRow("Stimulus Onset Pattern:", self.stimulus_onset_edit)

        stim_help = QLabel("Regex pattern to detect stimulus appearance (e.g., visual detection)")
        stim_help.setStyleSheet("color: gray; font-size: smaller;")
        form_layout.addRow("", stim_help)

        # Response clause
        self.response_clause_edit = QLineEdit()
        self.response_clause_edit.setPlaceholderText(DEFAULT_RESPONSE_CLAUSE)
        form_layout.addRow("Response Pattern:", self.response_clause_edit)

        resp_help = QLabel("Regex pattern to detect response onset (e.g., motor action)")
        resp_help.setStyleSheet("color: gray; font-size: smaller;")
        form_layout.addRow("", resp_help)

        layout.addLayout(form_layout)

        # Reset to defaults button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        layout.addWidget(reset_btn)

        # Stretch before buttons
        layout.addStretch()

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

        # Apply application font
        clear_font(self)

        # Load saved values
        self._load_settings()

    def _load_settings(self):
        """Load settings from QSettings."""
        trial_rule = self._settings.value("trial_start_rule", DEFAULT_TRIAL_START_RULE)
        stimulus_clause = self._settings.value("stimulus_onset_clause", DEFAULT_STIMULUS_ONSET_CLAUSE)
        response_clause = self._settings.value("response_clause", DEFAULT_RESPONSE_CLAUSE)

        self.trial_start_rule_edit.setText(trial_rule)
        self.stimulus_onset_edit.setText(stimulus_clause)
        self.response_clause_edit.setText(response_clause)

    def _save_settings(self):
        """Save settings to QSettings."""
        self._settings.setValue("trial_start_rule", self.trial_start_rule)
        self._settings.setValue("stimulus_onset_clause", self.stimulus_onset_clause)
        self._settings.setValue("response_clause", self.response_clause)

    def _reset_to_defaults(self):
        """Reset all fields to default values."""
        self.trial_start_rule_edit.setText(DEFAULT_TRIAL_START_RULE)
        self.stimulus_onset_edit.setText(DEFAULT_STIMULUS_ONSET_CLAUSE)
        self.response_clause_edit.setText(DEFAULT_RESPONSE_CLAUSE)

    def _on_cancel(self):
        self.ok = False
        self.hide()

    def _on_ok(self):
        self.ok = True
        self._save_settings()
        self.hide()

    @property
    def trial_start_rule(self) -> str:
        """Get the trial start rule, using default if empty."""
        text = self.trial_start_rule_edit.text().strip()
        return text if text else DEFAULT_TRIAL_START_RULE

    @property
    def stimulus_onset_clause(self) -> str:
        """Get the stimulus onset clause, using default if empty."""
        text = self.stimulus_onset_edit.text().strip()
        return text if text else DEFAULT_STIMULUS_ONSET_CLAUSE

    @property
    def response_clause(self) -> str:
        """Get the response clause, using default if empty."""
        text = self.response_clause_edit.text().strip()
        return text if text else DEFAULT_RESPONSE_CLAUSE
