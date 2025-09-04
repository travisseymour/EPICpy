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

import platform
from functools import partial

from qtpy.QtGui import QAction


def setup_menu(window):
    menubar = window.menuBar()
    if platform.system().lower() == "darwin":
        menubar.setNativeMenuBar(False)
    menubar.setStyleSheet(
        f"QMenuBar, QMenu {{ font-family: '{window.font().family()}'; font-size: {window.font().pointSize()}pt; }}"
    )

    # --- File Menu ---
    file_menu = menubar.addMenu("File")
    window.actionLoad_Device = QAction("Load Device", window)
    file_menu.addAction(window.actionLoad_Device)

    window.actionCompile_Rules = QAction("Compile Rules", window)
    window.actionCompile_Rules.setEnabled(False)
    file_menu.addAction(window.actionCompile_Rules)

    window.actionRecompile_Rules = QAction("Recompile Rules", window)
    window.actionRecompile_Rules.setEnabled(False)
    file_menu.addAction(window.actionRecompile_Rules)
    file_menu.addSeparator()

    window.actionLoad_Visual_Encoder = QAction("Load Visual Encoder", window)
    window.actionLoad_Visual_Encoder.setEnabled(False)
    file_menu.addAction(window.actionLoad_Visual_Encoder)

    window.actionLoad_Auditory_Encoder = QAction("Load Auditory Encoder", window)
    window.actionLoad_Auditory_Encoder.setEnabled(False)
    file_menu.addAction(window.actionLoad_Auditory_Encoder)

    window.actionUnload_Visual_Encoder = QAction("Unload Visual Encoder", window)
    window.actionUnload_Visual_Encoder.setEnabled(False)
    file_menu.addAction(window.actionUnload_Visual_Encoder)

    window.actionUnload_Auditory_Encoder = QAction("Unload Auditory Encoder", window)
    window.actionUnload_Auditory_Encoder.setEnabled(False)
    file_menu.addAction(window.actionUnload_Auditory_Encoder)
    file_menu.addSeparator()

    window.actionReload_Session = QAction("Reload Last Session", window)
    file_menu.addAction(window.actionReload_Session)
    file_menu.addSeparator()

    window.actionRun_Simulation_Script = QAction("Run Simulation Script", window)
    file_menu.addAction(window.actionRun_Simulation_Script)
    file_menu.addSeparator()

    window.actionExport_Normal_Output = QAction("Export Normal Output", window)
    window.actionExport_Normal_Output.setEnabled(False)
    file_menu.addAction(window.actionExport_Normal_Output)

    window.actionExport_Trace_Output = QAction("Export Trace Output", window)
    window.actionExport_Trace_Output.setEnabled(False)
    file_menu.addAction(window.actionExport_Trace_Output)

    window.actionExport_Stats_Output = QAction("Export Stats Output", window)
    window.actionExport_Stats_Output.setEnabled(False)
    file_menu.addAction(window.actionExport_Stats_Output)
    file_menu.addSeparator()

    window.actionQuit = QAction("Quit", window)
    file_menu.addAction(window.actionQuit)

    # --- Find Menu ---
    find_menu = menubar.addMenu("Find")
    window.actionFind = QAction("Find", window)
    find_menu.addAction(window.actionFind)

    window.actionFindNext = QAction("Find Next", window)
    find_menu.addAction(window.actionFindNext)

    window.actionFindPrevious = QAction("Find Previous", window)
    find_menu.addAction(window.actionFindPrevious)

    # --- Settings Menu ---
    settings_menu = menubar.addMenu("Settings")
    window.actionTrace_Settings = QAction("Trace Settings", window)
    window.actionTrace_Settings.setEnabled(False)
    settings_menu.addAction(window.actionTrace_Settings)

    window.actionDisplay_Controls = QAction("Display Controls", window)
    window.actionDisplay_Controls.setEnabled(False)
    settings_menu.addAction(window.actionDisplay_Controls)

    window.actionRule_Break_Settings = QAction("Rule Break Settings", window)
    window.actionRule_Break_Settings.setEnabled(False)
    settings_menu.addAction(window.actionRule_Break_Settings)

    window.actionLogging = QAction("Logging", window)
    window.actionLogging.setEnabled(False)
    settings_menu.addAction(window.actionLogging)

    window.actionAudio_Settings = QAction("Audio Settings", window)
    window.actionAudio_Settings.setEnabled(False)
    window.actionAudio_Settings.setVisible(False)
    settings_menu.addAction(window.actionAudio_Settings)

    window.actionDevice_Options = QAction("Device Options", window)
    settings_menu.addAction(window.actionDevice_Options)

    settings_menu.addSeparator()
    window.actionSound_Text_Settings = QAction("Sound Text Settings", window)
    settings_menu.addAction(window.actionSound_Text_Settings)

    window.actionSet_Application_Font = QAction("Set Application Font", window)
    settings_menu.addAction(window.actionSet_Application_Font)

    # --- Run Menu ---
    run_menu = menubar.addMenu("Run")
    window.actionRun_Settings = QAction("Run Settings", window)
    window.actionRun_Settings.setEnabled(False)
    run_menu.addAction(window.actionRun_Settings)

    window.actionRunAll = QAction("Run", window)
    window.actionRunAll.setEnabled(False)
    run_menu.addAction(window.actionRunAll)

    window.actionRun_One_Step = QAction("Run One Step", window)
    window.actionRun_One_Step.setEnabled(False)
    run_menu.addAction(window.actionRun_One_Step)

    window.actionPause = QAction("Pause", window)
    window.actionPause.setEnabled(False)
    run_menu.addAction(window.actionPause)

    window.actionStop = QAction("Stop", window)
    window.actionStop.setEnabled(False)
    run_menu.addAction(window.actionStop)
    run_menu.addSeparator()

    window.actionDelete_Datafile = QAction("Delete Datafile", window)
    run_menu.addAction(window.actionDelete_Datafile)

    # --- Windows Menu ---
    windows_menu = menubar.addMenu("Windows")

    window.actionClear_Output_Windows = QAction("Clear Output Windows", window)
    windows_menu.addAction(window.actionClear_Output_Windows)
    windows_menu.addSeparator()

    window.actionRestore_Visual_Views = QAction("Restore Visual Views", window)
    window.actionRestore_Auditory_Views = QAction("Restore Auditory Views", window)
    window.actionRestore_Normal_Output = QAction("Restore Normal Output", window)
    window.actionRestore_Trace_Output = QAction("Restore Trace Output", window)
    window.actionRestore_Stats_Output = QAction("Restore Stats Output", window)
    windows_menu.addAction(window.actionRestore_Visual_Views)
    windows_menu.addAction(window.actionRestore_Auditory_Views)
    windows_menu.addAction(window.actionRestore_Normal_Output)
    windows_menu.addAction(window.actionRestore_Trace_Output)
    windows_menu.addAction(window.actionRestore_Stats_Output)
    windows_menu.addSeparator()

    window.actionReset_Layout = QAction("Restore Default Layout", window)
    windows_menu.addAction(window.actionReset_Layout)

    # window.actionRuleFlowTool.setEnabled(True)
    # window.actionSchematicTool.setEnabled(True)
    # window.actionProcessGraphTool.setEnabled(True)
    # window.actionBrainTool.setEnabled(True)

    # --- Tool Menu --
    tool_menu = menubar.addMenu("SimTools")

    window.actionSchematicTool = QAction("Schematic", window)
    tool_menu.addAction(window.actionSchematicTool)

    window.actionBrainTool = QAction("Brain", window)
    tool_menu.addAction(window.actionBrainTool)

    window.actionRuleFlowTool = QAction("RuleFlow", window)
    tool_menu.addAction(window.actionRuleFlowTool)

    window.actionProcessGraphTool = QAction("ProcessGraph", window)
    tool_menu.addAction(window.actionProcessGraphTool)

    # --- Help Menu ---
    help_menu = menubar.addMenu("Help")
    window.actionAbout = QAction("About", window)
    help_menu.addAction(window.actionAbout)

    window.actionHelp = QAction("Help", window)
    help_menu.addAction(window.actionHelp)
    help_menu.addSeparator()

    # Tests submenu under Help
    tests_menu = help_menu.addMenu("Tests")
    window.actionStandardRun = QAction("Standard Run", window)
    tests_menu.addAction(window.actionStandardRun)
    window.actionEncoderRun = QAction("Encoder Run", window)
    tests_menu.addAction(window.actionEncoderRun)
    window.actionAllRuns = QAction("All Runs", window)
    tests_menu.addAction(window.actionAllRuns)


def setup_menu_connections(window):
    # Connect menu actions to slots and set shortcuts

    # File menu actions
    window.actionQuit.triggered.connect(window.close)
    window.actionQuit.setShortcut("Ctrl+Q")
    window.actionLoad_Device.triggered.connect(window.on_load_device)
    window.actionLoad_Device.setShortcut("Ctrl+L")
    window.actionCompile_Rules.triggered.connect(window.choose_rules)
    window.actionCompile_Rules.setShortcut("Ctrl+K")
    window.actionRecompile_Rules.triggered.connect(window.recompile_rules)
    window.actionRecompile_Rules.setShortcut("Ctrl+Alt+K")
    window.actionLoad_Visual_Encoder.triggered.connect(partial(window.simulation.on_load_encoder, kind="Visual"))
    window.actionLoad_Auditory_Encoder.triggered.connect(partial(window.simulation.on_load_encoder, kind="Auditory"))
    window.actionUnload_Visual_Encoder.triggered.connect(partial(window.simulation.on_unload_encoder, kind="Visual"))
    window.actionUnload_Auditory_Encoder.triggered.connect(
        partial(window.simulation.on_unload_encoder, kind="Auditory")
    )

    # Run menu actions
    window.actionRun_Settings.triggered.connect(window.show_run_settings)
    window.actionRunAll.triggered.connect(window.run_all)
    window.actionRunAll.setShortcut("Ctrl+R")
    window.actionRun_One_Step.triggered.connect(window.run_one_step)
    window.actionRun_One_Step.setShortcut("Ctrl+O")
    window.actionStop.triggered.connect(window.halt_simulation)
    window.actionStop.setShortcut("Ctrl+.")
    window.actionPause.triggered.connect(window.pause_simulation)
    window.actionPause.setShortcut("Ctrl+Alt+P")
    window.actionDelete_Datafile.triggered.connect(window.delete_datafile)
    window.actionRun_Simulation_Script.setVisible(False)

    # Help menu actions
    window.actionAbout.triggered.connect(window.about_dialog)
    window.actionHelp.triggered.connect(window.open_help_file)
    window.actionStandardRun.triggered.connect(partial(window.run_tests, kind="StandardRun"))
    window.actionEncoderRun.triggered.connect(partial(window.run_tests, kind="EncoderRun"))
    window.actionAllRuns.triggered.connect(partial(window.run_tests, kind="AllRuns"))

    # Settings menu actions
    window.actionDisplay_Controls.triggered.connect(window.show_display_settings_dialogs)
    window.actionTrace_Settings.triggered.connect(window.show_trace_settings_dialogs)
    window.actionLogging.triggered.connect(window.show_log_settings_dialogs)
    window.actionRule_Break_Settings.triggered.connect(window.show_rule_break_settings_dialog)
    window.actionDevice_Options.triggered.connect(window.show_device_options_dialog)
    window.actionSound_Text_Settings.triggered.connect(window.show_sound_text_settings_dialog)
    window.actionSet_Application_Font.triggered.connect(window.set_application_font)

    # Windows menu actions
    window.actionClear_Output_Windows.triggered.connect(window.clear_output_windows)
    window.actionReset_Layout.triggered.connect(window.layout_reset)
    window.actionReload_Session.triggered.connect(partial(window.session_reload, quiet=False))

    window.actionRestore_Visual_Views.triggered.connect(partial(window.restore_ui_component, component="visual"))
    window.actionRestore_Auditory_Views.triggered.connect(partial(window.restore_ui_component, component="auditory"))
    window.actionRestore_Normal_Output.triggered.connect(partial(window.restore_ui_component, component="normal"))
    window.actionRestore_Trace_Output.triggered.connect(partial(window.restore_ui_component, component="trace"))
    window.actionRestore_Stats_Output.triggered.connect(partial(window.restore_ui_component, component="stats"))

    # Tools menu
    window.actionRuleFlowTool.setEnabled(True)
    window.actionSchematicTool.setEnabled(False)
    window.actionProcessGraphTool.setEnabled(False)
    window.actionBrainTool.setEnabled(False)

    window.actionRuleFlowTool.triggered.connect(partial(window.start_tool, tool_name="rule_flow"))
    window.actionSchematicTool.triggered.connect(partial(window.start_tool, tool_name="schematic"))
    window.actionProcessGraphTool.triggered.connect(partial(window.start_tool, tool_name="process_graph"))
    window.actionBrainTool.triggered.connect(partial(window.start_tool, tool_name="brain"))
