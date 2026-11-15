# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from epicpy.utils import config
from epicpy.utils.app_utils import clear_font


class LoggingSettingsWin(QDialog):
    def __init__(self):
        super().__init__()
        self.ok = False
        self.setWindowTitle("Output Logging Settings")
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Master enable checkbox
        self.checkBoxEnableLogging = QCheckBox("Enable Logging")
        self.checkBoxEnableLogging.toggled.connect(self._on_master_toggled)
        layout.addWidget(self.checkBoxEnableLogging)

        # Indented output checkboxes
        outputs_layout = QVBoxLayout()
        outputs_layout.setContentsMargins(20, 0, 0, 0)

        self.checkBoxLogNormal = QCheckBox("Normal Output")
        self.checkBoxLogTrace = QCheckBox("Trace Output")
        self.checkBoxLogStats = QCheckBox("Stats Output")

        # Connect to update write mode enabled state
        self.checkBoxLogNormal.toggled.connect(self._update_write_mode_enabled)
        self.checkBoxLogTrace.toggled.connect(self._update_write_mode_enabled)
        self.checkBoxLogStats.toggled.connect(self._update_write_mode_enabled)

        outputs_layout.addWidget(self.checkBoxLogNormal)
        outputs_layout.addWidget(self.checkBoxLogTrace)
        outputs_layout.addWidget(self.checkBoxLogStats)
        layout.addLayout(outputs_layout)

        # Spacer
        layout.addSpacing(10)

        # Write mode section
        self.labelWriteMode = QLabel("Write Mode:")
        layout.addWidget(self.labelWriteMode)

        mode_layout = QHBoxLayout()
        mode_layout.setContentsMargins(20, 0, 0, 0)

        self.radioOverwrite = QRadioButton("Overwrite")
        self.radioAppend = QRadioButton("Append")

        self.writeModeGroup = QButtonGroup(self)
        self.writeModeGroup.addButton(self.radioOverwrite)
        self.writeModeGroup.addButton(self.radioAppend)

        mode_layout.addWidget(self.radioOverwrite)
        mode_layout.addWidget(self.radioAppend)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Spacer
        layout.addSpacing(10)

        # Output folder info
        self.labelOutputFolder = QLabel()
        self.labelOutputFolder.setWordWrap(True)
        self.labelOutputFolder.setStyleSheet("color: gray;")
        layout.addWidget(self.labelOutputFolder)

        # Stretch before buttons
        layout.addStretch()

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.pushButtonCancel = QPushButton("Cancel")
        self.pushButtonCancel.clicked.connect(self.clicked_cancel_button)
        button_layout.addWidget(self.pushButtonCancel)

        self.pushButtonOK = QPushButton("OK")
        self.pushButtonOK.setDefault(True)
        self.pushButtonOK.clicked.connect(self.clicked_ok_button)
        button_layout.addWidget(self.pushButtonOK)

        layout.addLayout(button_layout)

        # Apply application font
        clear_font(self)

    def _on_master_toggled(self, checked: bool):
        """Enable/disable and set sub-checkboxes when master is toggled."""
        self.checkBoxLogNormal.setEnabled(checked)
        self.checkBoxLogTrace.setEnabled(checked)
        self.checkBoxLogStats.setEnabled(checked)

        if checked:
            # When enabling, check all sub-checkboxes
            self.checkBoxLogNormal.setChecked(True)
            self.checkBoxLogTrace.setChecked(True)
            self.checkBoxLogStats.setChecked(True)

        self._update_write_mode_enabled()

    def _update_write_mode_enabled(self):
        """Enable write mode controls only if at least one output type is checked."""
        any_checked = (
            self.checkBoxLogNormal.isChecked()
            or self.checkBoxLogTrace.isChecked()
            or self.checkBoxLogStats.isChecked()
        )
        self.labelWriteMode.setEnabled(any_checked)
        self.radioOverwrite.setEnabled(any_checked)
        self.radioAppend.setEnabled(any_checked)

    def setup_options(self):
        """Load current config values into UI."""
        # Set master checkbox
        self.checkBoxEnableLogging.setChecked(config.device_cfg.log_enabled)

        # Set sub-checkboxes
        self.checkBoxLogNormal.setChecked(config.device_cfg.log_normal_out)
        self.checkBoxLogTrace.setChecked(config.device_cfg.log_trace_out)
        self.checkBoxLogStats.setChecked(config.device_cfg.log_stats_out)

        # Enable/disable based on master state
        enabled = config.device_cfg.log_enabled
        self.checkBoxLogNormal.setEnabled(enabled)
        self.checkBoxLogTrace.setEnabled(enabled)
        self.checkBoxLogStats.setEnabled(enabled)

        # Set write mode
        if config.device_cfg.log_write_mode == "append":
            self.radioAppend.setChecked(True)
        else:
            self.radioOverwrite.setChecked(True)

        # Update folder label
        if config.device_cfg.device_file:
            device_folder = Path(config.device_cfg.device_file).parent
            logging_folder = device_folder / "logging"
            self.labelOutputFolder.setText(f"Files saved to: {logging_folder}")
        else:
            self.labelOutputFolder.setText("Files saved to: {device_folder}/logging/")

        # Update write mode enabled state
        self._update_write_mode_enabled()

    def clicked_cancel_button(self):
        self.ok = False
        self.hide()

    def clicked_ok_button(self):
        self.ok = True

        # Save all settings to config
        config.device_cfg.log_enabled = self.checkBoxEnableLogging.isChecked()
        config.device_cfg.log_normal_out = self.checkBoxLogNormal.isChecked()
        config.device_cfg.log_trace_out = self.checkBoxLogTrace.isChecked()
        config.device_cfg.log_stats_out = self.checkBoxLogStats.isChecked()
        config.device_cfg.log_write_mode = "append" if self.radioAppend.isChecked() else "overwrite"

        self.hide()
