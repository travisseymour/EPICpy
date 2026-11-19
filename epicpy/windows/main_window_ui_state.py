# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Mixin class providing UI state management functionality for MainWin.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from epicpy import __version__
from epicpy.constants.state_constants import PAUSED, RUNNABLE, RUNNING, UNREADY

if TYPE_CHECKING:
    from epicpy.windows.main_window import MainWin


class UIStateMixin:
    """
    Mixin for MainWin providing UI state management functionality.

    Includes methods for:
    - Setting UI state based on simulation state (running, paused, not running)
    - Updating window title
    - Updating status bar
    """

    # Type hints for attributes that exist on MainWin
    if TYPE_CHECKING:
        self: "MainWin"

    def update_ui_status(self):
        if self.run_state == RUNNING:
            if self.simulation.has_device():
                msg = f" | {self.simulation.device.device_name} | {self.simulation.device.get_parameter_string()}"
            else:
                msg = ""
            self.statusBar().showMessage(f"Run State: Running{msg}")
            self.set_ui_running()
        elif self.run_state == PAUSED:
            self.statusBar().showMessage("Run State: Paused")
            self.set_ui_paused()
        else:
            self.statusBar().showMessage(f"Run State: {'UnReady' if self.run_state == UNREADY else 'Runnable'}")
            self.set_ui_not_running()

    def set_ui_running(self):
        self.actionStop.setEnabled(True)
        self.actionPause.setEnabled(True)

        self.actionRun_Normal.setEnabled(False)
        self.actionRun_One_Step.setEnabled(False)

        self.actionLoad_Device.setEnabled(False)
        self.actionLoad_Visual_Encoder.setEnabled(False)
        self.actionLoad_Auditory_Encoder.setEnabled(False)
        self.actionUnload_Visual_Encoder.setEnabled(False)
        self.actionUnload_Auditory_Encoder.setEnabled(False)
        self.actionCompile_Rules.setEnabled(False)
        self.actionRecompile_Rules.setEnabled(False)

        self.actionRun_Settings.setEnabled(False)
        self.actionRule_Break_Settings.setEnabled(False)
        self.actionDevice_Options.setEnabled(False)
        self.actionSound_Text_Settings.setEnabled(False)

        self.actionDisplay_Controls.setEnabled(True)
        self.actionTrace_Settings.setEnabled(True)

        # self.actionLogging.setEnabled(False)
        self.actionExport_Normal_Output.setEnabled(False)
        self.actionExport_Trace_Output.setEnabled(False)
        self.actionExport_Stats_Output.setEnabled(False)

        self.actionDelete_Datafile.setEnabled(False)

        for out in self.normalTextOutput, self.traceTextOutput, self.infoTextOutput:
            out.enable_command("Stop", True)
            out.enable_command("Clear", False)
            out.enable_command("Open Normal Output In Text Editor", False)
            out.enable_command("Edit Production Rule File", True)
            out.enable_command("Edit Data Output File", False)
            out.enable_command("Open Device Folder", True)
            out.enable_command("Quit", True)

    def set_ui_paused(self):
        has_rules = self.simulation and self.simulation.has_model() and self.simulation.model.get_prs_filename() != ""
        has_device = self.simulation and self.simulation.has_device()
        has_visual_encoder = self.simulation and self.simulation.has_visual_encoder()
        has_auditory_encoder = self.simulation and self.simulation.has_auditory_encoder()

        self.actionStop.setEnabled(True)
        self.actionPause.setEnabled(False)

        self.actionRun_Normal.setEnabled(True)
        self.actionRun_One_Step.setEnabled(True)

        self.actionLoad_Device.setEnabled(True)
        self.actionCompile_Rules.setEnabled(True)
        self.actionRecompile_Rules.setEnabled(has_rules)
        self.actionLoad_Visual_Encoder.setEnabled(has_device)
        self.actionLoad_Auditory_Encoder.setEnabled(has_device)
        self.actionUnload_Visual_Encoder.setEnabled(has_visual_encoder)
        self.actionUnload_Auditory_Encoder.setEnabled(has_auditory_encoder)

        self.actionRun_Settings.setEnabled(has_device)
        self.actionDevice_Options.setEnabled(has_device)
        self.actionRule_Break_Settings.setEnabled(has_device and has_rules)
        self.actionSound_Text_Settings.setEnabled(False)

        self.actionDisplay_Controls.setEnabled(True)
        self.actionTrace_Settings.setEnabled(True)
        # self.actionLogging.setEnabled(True)

        self.actionExport_Normal_Output.setEnabled(True)
        self.actionExport_Trace_Output.setEnabled(True)
        self.actionExport_Stats_Output.setEnabled(True)

        self.actionDelete_Datafile.setEnabled(False)

        for out in self.normalTextOutput, self.traceTextOutput, self.infoTextOutput:
            out.enable_command("Stop", False)
            out.enable_command("Clear", True)
            out.enable_command("Open Normal Output In Text Editor", True)
            out.enable_command("Edit Production Rule File", has_device)
            out.enable_command("Edit Data Output File", has_device)
            out.enable_command("Open Device Folder", has_device)
            out.enable_command("Quit", True)

    def set_ui_not_running(self):
        runnable = self.run_state == RUNNABLE

        has_rules = self.simulation and self.simulation.has_model() and self.simulation.model.get_prs_filename() != ""
        has_device = self.simulation and self.simulation.has_device()
        has_visual_encoder = self.simulation and self.simulation.has_visual_encoder()
        has_auditory_encoder = self.simulation and self.simulation.has_auditory_encoder()

        self.actionStop.setEnabled(False)
        self.actionPause.setEnabled(False)

        self.actionRun_Normal.setEnabled(runnable)
        self.actionRun_One_Step.setEnabled(runnable)

        self.actionLoad_Device.setEnabled(True)
        self.actionCompile_Rules.setEnabled(True)
        self.actionRecompile_Rules.setEnabled(has_rules)
        self.actionLoad_Visual_Encoder.setEnabled(has_device)
        self.actionLoad_Auditory_Encoder.setEnabled(has_device)
        self.actionUnload_Visual_Encoder.setEnabled(has_visual_encoder)
        self.actionUnload_Auditory_Encoder.setEnabled(has_auditory_encoder)

        self.actionRun_Settings.setEnabled(has_device)
        self.actionDevice_Options.setEnabled(has_device)
        self.actionRule_Break_Settings.setEnabled(has_device and has_rules)
        self.actionSound_Text_Settings.setEnabled(has_device)

        self.actionDisplay_Controls.setEnabled(has_device)
        self.actionTrace_Settings.setEnabled(has_device)
        self.actionLogging.setEnabled(has_device)

        self.actionExport_Normal_Output.setEnabled(has_device)
        self.actionExport_Trace_Output.setEnabled(has_device)
        self.actionExport_Stats_Output.setEnabled(has_device)

        self.actionDelete_Datafile.setEnabled(has_device)

        for out in self.normalTextOutput, self.traceTextOutput, self.infoTextOutput:
            out.enable_command("Stop", False)
            out.enable_command("Clear", True)
            out.enable_command("Open Normal Output In Text Editor", True)
            out.enable_command("Edit Production Rule File", has_device)
            out.enable_command("Edit Data Output File", has_device)
            out.enable_command("Open Device Folder", has_device)
            out.enable_command("Quit", True)

    def update_title(self):
        if self.simulation and self.simulation.has_device() and self.simulation.has_model():
            device_name = f"""DEVICE: {self.simulation.device.device_name}"""
        else:
            device_name = "DEVICE: None"
        rule_name = (
            f"RULES: {Path(self.simulation.rule_files[self.simulation.current_rule_index].rule_file).name}"
            if self.simulation and self.simulation.rule_files
            else "Rules: None"
        )

        epiclib_version = "EPICLIB: 06/28/2016"

        encoders = []
        if self.simulation and self.simulation.has_visual_encoder():
            encoders.append("Visual")
        if self.simulation and self.simulation.has_auditory_encoder():
            encoders.append("Auditory")
        if encoders:
            encoder_info = f"ENCODERS: [{', '.join(encoders)}]"
        else:
            encoder_info = "ENCODERS: None"

        self.setWindowTitle(f"EPICpy v{__version__} | {device_name} | {rule_name} | {epiclib_version} | {encoder_info}")
