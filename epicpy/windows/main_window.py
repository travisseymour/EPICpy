"""
This file is part of the EPICpy source code. EPICpy is a tool for simulating
human performance tasks using the EPIC computational cognitive architecture
(David Kieras and David Meyer 1997a) using the Python programming language.
Copyright (C) 2022-2026 Travis L. Seymour, PhD

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

import datetime
import importlib.metadata
import os
import platform
import re
import subprocess
import sys
import tempfile
import webbrowser
from functools import partial
from itertools import chain
from pathlib import Path
from typing import Literal, Optional

from loguru import logger as log
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView  # Linux might need `sudo apt install libnss3`
from qtpy.QtCore import QByteArray, QEvent, QPoint, QRect, QSettings, QSize, Qt, QTimer
from qtpy.QtGui import (
    QAction,
    QCloseEvent,
    QFontDatabase,
    QGuiApplication,
    QHideEvent,
    QIcon,
    QShowEvent,
)
from qtpy.QtWidgets import QApplication, QDockWidget, QFileDialog, QMainWindow, QWidget

from epicpy import EPICPY_DEBUG, __version__
from epicpy.constants.emoji import e_boxed_x, e_info, emoji_box
from epicpy.constants.state_constants import PAUSED, RUNNABLE, RUNNING, UNREADY
from epicpy.dialogs.about_window import AboutWin
from epicpy.dialogs.break_settings_window import BreakSettingsWin
from epicpy.dialogs.device_settings_window import DeviceOptionsWin
from epicpy.dialogs.display_controls_window import DisplayControlsWin
from epicpy.dialogs.font_size_window import FontSizeDialog
from epicpy.dialogs.logging_window import LoggingSettingsWin
from epicpy.dialogs.run_settings_window import RunSettingsWin
from epicpy.dialogs.snd_text_settings_window import SoundTextSettingsWin
from epicpy.dialogs.trace_settings_window import TraceSettingsWin
from epicpy.epic.epic_simulation import Simulation
from epicpy.epic.parallel_simulation import (
    OutputSettings,
    SimulationResult,
    create_sim_configs_from_permutations,
    expand_permutations,
    has_permutations,
    run_parallel_simulations,
)
from epicpy.epic.run_info import RunInfo
from epicpy.tools.process_viewer.process_viewer import ProcessViewerWindow
from epicpy.tools.rule_flow.rule_flow import RuleFlowWindow
from epicpy.utils import config, fitness
from epicpy.utils.app_utils import (
    clear_font,
    has_epiccoder,
    hcolor,
    loading_cursor_context,
    run_without_waiting,
)
from epicpy.utils.device_pyee_bridge import qt_events
from epicpy.utils.resource_utils import get_resource
from epicpy.utils.update_utils import update_available
from epicpy.views.auditory_view_window import AuditoryViewWin
from epicpy.views.epicpy_auditory_view import EPICAuditoryView
from epicpy.views.epicpy_visual_view import EPICVisualView
from epicpy.views.visual_view_window import VisualViewWin
from epicpy.widgets.custom_text_edit import CustomQTextEdit
from epicpy.widgets.mem_large_text_view import MemLargeTextView
from epicpy.widgets.stats_web_view import StatsWebView
from epicpy.windows import main_window_menu
from epicpy.windows.app_style import set_dark_style, set_light_style
from epicpy.windows.layout_manager import HorizontalDockArea, LayoutMixin
from epicpy.windows.main_window_utils import (
    get_desktop_geometry,
    get_desktop_usable_geometry,
)

epiclib_version = importlib.metadata.version("epiclibcpp")
print(f"Currently using epiclibcpp v{epiclib_version}")

from epiclibcpp.epiclib.output_tee_globals import (
    Debug_out,
    Device_out,
    Exception_out,
    Info_out,
    Normal_out,
    Stats_out,
    Trace_out,
)
from epiclibcpp.epiclib.pps_globals import PPS_out


class MainWin(LayoutMixin, QMainWindow):
    def __init__(self, app: QApplication):
        super(MainWin, self).__init__()
        self.app = app
        self.setObjectName("MainWindow")
        self.view_type = b"NormalOut"
        self.ok = False
        self.tmp_folder = tempfile.TemporaryDirectory()
        self.closing = False
        self._size_adjusted: bool = False

        self.setUnifiedTitleAndToolBarOnMac(True)  # doesn't appear to make a difference

        self.window_settings = QSettings("epicpy2", "WindowSettings")

        self.statusBar().showMessage("Run Status: UNREADY")

        self.context = "Main"

        self.run_state = UNREADY

        self.last_search_spec = None

        screen = QGuiApplication.primaryScreen()
        self.scaling_factor: float = screen.devicePixelRatio()

        # setup window dimensions
        self.desktop_size: QSize = get_desktop_geometry()
        self.raw_desktop_size: QSize = QSize(
            int(round(self.desktop_size.height() * self.scaling_factor)),
            int(round(self.desktop_size.width() * self.scaling_factor)),
        )
        self.usable_desktop_size: QSize = get_desktop_usable_geometry()

        if self.usable_desktop_size.height() >= 1280:
            """
            1440p
            usable_desktop_size: QSize(2560, 1440)
            default_window_size: QSize(2065, 1145)
            QSize(2272, 1260)
            """
            self.default_window_size = QSize(int(round(2271 / 1.1)), int(round(1260 / 1.1)))
        elif self.usable_desktop_size.height() >= 960:
            """
            FHD
            self.usable_desktop_size=qtpy.QtCore.QSize(1920, 1080)
            self.default_window_size=qtpy.QtCore.QSize(1557, 909)
            qtpy.QtCore.QSize(1713, 1000)
            """
            self.default_window_size = QSize(int(round(1713 / 1.1)), int(round(1000 / 1.1)))
        else:
            self.default_window_size = self.usable_desktop_size

        self.minimum_view_size = QSize(240, 186)

        self.setGeometry(QRect(QPoint(0, 0), self.default_window_size))
        QApplication.processEvents()

        # inits for layout save info
        self.default_geometry: Optional[QByteArray] = None
        self.default_state: Optional[QByteArray] = None
        self.default_top_custom_settings: dict = {}
        self.default_middle_custom_settings: dict = {}

        # add central widget and setup
        self.normalTextOutput = MemLargeTextView(self)
        self.normalTextOutput.setObjectName("NormalOutputWindow")

        # Attach relevant output tees to this window
        for ot in (Normal_out, Debug_out, Device_out, Exception_out, PPS_out):
            ot.add_py_stream(self.normalTextOutput)
            if EPICPY_DEBUG:
                ot.add_py_stream(sys.stdout)  # for debug
        Exception_out.add_py_stream(sys.stderr)  # NOTE: I'm not sure that this is needed

        update = update_available(html=True)
        update_msg = f"\n{update}\n" if update else "\n"
        self.normalTextOutput.write(f"Normal Out! ({datetime.datetime.now().strftime('%r')})\n")

        # to avoid having to load any epic stuff in trace_window.py, we go ahead and
        # connect Trace_out now
        self.traceTextOutput = MemLargeTextView(self)
        self.traceTextOutput.setObjectName("TraceOutputWindow")

        # Attach relevant output tees to this window
        Trace_out.add_py_stream(self.traceTextOutput)
        # Trace_out.add_py_stream(sys.stdout)  # for debug

        self.traceTextOutput.write(f"Trace Out! ({datetime.datetime.now().strftime('%r')})\n")

        # info output widget
        self.infoTextOutput = CustomQTextEdit(self)
        self.infoTextOutput.setObjectName("InfoOutputWindow")
        self.infoTextOutput.setReadOnly(True)
        self.infoTextOutput.write(
            f"Info Out! ({datetime.datetime.now().strftime('%r')})\n"
            f"Python: Using {platform.python_implementation()} {platform.python_version()}.\n"
            f"EPIClib: Using version {epiclib_version}.\n"
        )
        self.infoTextOutput.write(update_msg)

        Info_out.add_py_stream(self.infoTextOutput)
        # Info_out.add_py_stream(sys.stdout)  # for debug

        # add commands to output windows
        for out in self.normalTextOutput, self.infoTextOutput, self.traceTextOutput:
            out.set_commands(
                {
                    "Stop": self.stop_simulation,
                    "Clear": out.clear,
                    "Open Normal Output In Text Editor": partial(self.launchEditor, "NormalOut"),
                    "Edit Production Rule File": partial(self.launchEditor, "RuleFile"),
                    "Edit Data Output File": partial(self.launchEditor, "DataFile"),
                    "Open Device Folder": self.open_device_folder,
                    "Quit": self.close,
                }
            )
            out.disable_all_commands()
            out.enable_commands(["Clear", "Quit"])

        # stats widget
        self.stats_win = StatsWebView(self)
        self.stats_win.setObjectName("StatsOutputWindow")

        # init window properties
        self.visual_views: dict[str, VisualViewWin] = {}
        self.visual_physical_view: EPICVisualView
        self.visual_sensory_view: EPICVisualView
        self.visual_perceptual_view: EPICVisualView

        self.auditory_views: dict[str, AuditoryViewWin] = {}
        self.auditory_physical_view: EPICAuditoryView
        self.auditory_sensory_view: EPICAuditoryView
        self.auditory_perceptual_view: EPICAuditoryView

        self.simulation = Simulation(self)

        # type define settings dialog properties
        self.run_settings_dialog: RunSettingsWin
        self.display_settings_dialog: DisplayControlsWin
        self.trace_settings_dialog: TraceSettingsWin
        self.log_settings_dialog: LoggingSettingsWin
        self.rule_break_settings_dialog: BreakSettingsWin
        self.device_options_dialog: DeviceOptionsWin
        self.sound_text_settings_dialog: SoundTextSettingsWin
        self.font_size_dialog: FontSizeDialog

        # finally setup ui

        self.setup_views()
        self.setup_base_ui()
        qt_events.background_image.connect(self.set_view_background_image_from_signal)

        self.view_updater = QTimer()  # to single shot view updates that won't slow down main thread
        self.ui_timer = QTimer()  # for updating status bar and other stuff every second or so

        # Setup Menus
        # ===========

        # File Menu Actions
        self.actionLoad_Device: QAction
        self.actionCompile_Rules: QAction
        self.actionRecompile_Rules: QAction
        self.actionLoad_Visual_Encoder: QAction
        self.actionLoad_Auditory_Encoder: QAction
        self.actionUnload_Visual_Encoder: QAction
        self.actionUnload_Auditory_Encoder: QAction
        self.actionExport_Normal_Output: QAction
        self.actionExport_Trace_Output: QAction
        self.actionExport_Stats_Output: QAction
        self.actionQuit: QAction

        # Settings Menu Actions
        self.actionTrace_Settings: QAction
        self.actionDisplay_Controls: QAction
        self.actionRule_Break_Settings: QAction
        self.actionLogging: QAction
        self.actionAudio_Settings: QAction
        self.actionDevice_Options: QAction
        self.actionSound_Text_Settings: QAction
        self.actionSet_Application_Font: QAction

        # Run Menu Actions
        self.actionRun_Settings: QAction
        self.actionRun_Normal: QAction
        self.actionRun_One_Step: QAction
        self.actionPause: QAction
        self.actionStop: QAction
        self.actionDelete_Datafile: QAction

        # Help Menu Actions
        self.actionAbout: QAction
        self.actionHelp: QAction
        self.actionStandardRun: QAction
        self.actionEncoderRun: QAction
        self.actionAllRuns: QAction

        # Windows Menu Actions
        self.actionShow_All: QAction
        self.actionMinimize_All: QAction
        self.actionShow_Trace_Window: QAction
        self.actionShow_Stats_Window: QAction
        self.actionShow_Visual_Views: QAction
        self.actionShow_Auditory_Views: QAction
        self.actionClear_Output_Windows: QAction
        self.actionReset_Layout: QAction

        # Tools Menu Actions
        self.actionRuleFlowTool: QAction
        self.actionSchematicTool: QAction
        self.actionProcessViewerTool: QAction
        self.actionBrainTool: QAction

        self.rule_flow_window: QMainWindow | None = None
        self.schematic_window: QMainWindow | None = None
        self.process_viewer_window: QMainWindow | None = None
        self.brain_tool: QMainWindow | None = None

        main_window_menu.setup_menu(self)
        main_window_menu.setup_menu_connections(self)

        # Connect output content changes to update tool states
        self.normalTextOutput.content_changed.connect(self._update_ruleflow_tool_enabled)
        self.traceTextOutput.content_changed.connect(self._update_process_viewer_tool_enabled)

        # self.context_menu = QMenu(self)
        # self.context_items = {}
        # self.create_context_menu_items()

        self.default_palette = self.app.palette()
        self.update_theme()

        recent = self._get_recent_devices()
        if recent:
            Info_out(f"Recent devices available: {len(recent)} (File > Load Recent Device)\n")
        else:
            Info_out("No recent devices found.\n")

        self.update_title()

        # setup some ui timers
        self.ui_timer.timeout.connect(self.update_ui_status)
        self.ui_timer.start(1000)

        self.setWindowIcon(QIcon(str(get_resource("uiicons", "Icon.png"))))
        self.setWindowIconText("EPICpy")
        self.show()

    def setup_base_ui(self):
        # Use an empty central widget that occupies no horizontal space.
        central = QWidget(self)
        central.setMaximumWidth(0)
        self.setCentralWidget(central)

        # ----- Left Column Dock Widgets -----
        # Top Dock Area: Contains three inner docks.
        self.topAreaInner = HorizontalDockArea(self.visual_views, self.minimum_view_size, self)
        self.dockTop = QDockWidget("Visual Views", self)
        self.dockTop.setObjectName("dockTop")
        self.dockTop.setWidget(self.topAreaInner)
        self.dockTop.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.dockTop.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        # Middle Dock Area: Contains three inner docks.
        self.middleAreaInner = HorizontalDockArea(self.auditory_views, self.minimum_view_size, self)
        self.dockMiddle = QDockWidget("Auditory Views", self)
        self.dockMiddle.setObjectName("dockMiddle")
        self.dockMiddle.setWidget(self.middleAreaInner)
        self.dockMiddle.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.dockMiddle.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        # Bottom Dock Area: A plain text edit for Normal Output.
        self.dockNormal = QDockWidget("Normal Output", self)
        self.dockNormal.setObjectName("dockNormal")
        normalPlainText = self.normalTextOutput
        normalPlainText.setStyleSheet("border: 2px solid #B9B8B6;")
        self.dockNormal.setWidget(normalPlainText)
        self.dockNormal.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.dockNormal.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        # New: Trace Output dock.
        self.dockTrace = QDockWidget("Trace Output", self)
        self.dockTrace.setObjectName("dockTrace")
        tracePlainText = self.traceTextOutput
        tracePlainText.setStyleSheet("border: 2px solid #B9B8B6;")
        self.dockTrace.setWidget(tracePlainText)
        self.dockTrace.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.dockTrace.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        # Info Output dock.
        self.dockInfo = QDockWidget("Info Output", self)
        self.dockInfo.setObjectName("dockInfo")
        infoPlainText = self.infoTextOutput
        infoPlainText.setStyleSheet("border: 2px solid #B9B8B6;")
        self.dockInfo.setWidget(infoPlainText)
        self.dockInfo.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.dockInfo.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        # Stack the left column docks vertically.
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockTop)
        self.splitDockWidget(self.dockTop, self.dockMiddle, Qt.Orientation.Vertical)
        self.splitDockWidget(self.dockMiddle, self.dockInfo, Qt.Orientation.Vertical)
        # Tabify Info Output, Normal Output, and Trace Output so they share the same area.
        self.tabifyDockWidget(self.dockInfo, self.dockNormal)
        self.tabifyDockWidget(self.dockNormal, self.dockTrace)
        # Ensure Info Output is the active (front) tab.
        self.dockInfo.raise_()

        # Auto-focus the MemLargeTextView when its dock tab is selected,
        # so that keyboard shortcuts (Ctrl+F, etc.) route to the active tab.
        self.dockNormal.visibilityChanged.connect(lambda visible: visible and self.normalTextOutput.setFocus())
        self.dockInfo.visibilityChanged.connect(lambda visible: visible and self.infoTextOutput.setFocus())
        self.dockTrace.visibilityChanged.connect(lambda visible: visible and self.traceTextOutput.setFocus())

        # ----- Right Dock Widget (Side Dock Area) -----
        self.dockSide = QDockWidget("Statistics Output", self)
        self.dockSide.setObjectName("dockSide")
        plainTextEditSide = self.stats_win
        plainTextEditSide.setStyleSheet("border: 1px solid black;")
        self.dockSide.setWidget(plainTextEditSide)
        self.dockSide.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockSide.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockSide)

        self.setGeometry(QRect(QPoint(0, 0), self.default_window_size))

        if self.usable_desktop_size.height() < 776:
            self.dockMiddle.close()

            # Assume 'self' is your MainWindow instance and you have references to the dock widgets:
            min_top = self.dockTop.widget().minimumSizeHint().height()
            min_middle = self.dockMiddle.widget().minimumSizeHint().height()
            # Compute the available height in the main window minus what’s needed for the two upper docks.
            available_for_bottom = self.height() - (min_top + min_middle)

            # Now call resizeDocks with the vertical orientation.
            self.resizeDocks(
                [self.dockTop, self.dockMiddle, self.dockNormal],
                [
                    min_top,
                    min_middle,
                    max(
                        available_for_bottom,
                        self.dockNormal.widget().minimumSizeHint().height(),
                    ),
                ],
                Qt.Orientation.Vertical,
            )

        self.update()

    def restore_ui_component(self, component: str):
        components: dict[str, QDockWidget] = {
            "visual": self.dockTop,
            "auditory": self.dockMiddle,
            "normal": self.dockNormal,
            "info": self.dockInfo,
            "trace": self.dockTrace,
            "stats": self.dockSide,
        }
        if component in components:
            dock: QDockWidget = components[component]
            dock.show()
            for child in dock.children():
                widget: QDockWidget = child
                if hasattr(widget, "setVisible"):
                    widget.setVisible(True)
                if hasattr(widget, "show"):
                    widget.show()
                if hasattr(widget, "raise_"):
                    widget.raise_()

    # ==============================================================================
    # Delegates for methods of self.simulation. This is required because we may delete
    # and re-init self.simulation, and we don't want various menu items to then point
    # to nothing.
    # ==============================================================================

    def on_load_device(self, file: str = "", quiet: bool = False, auto_load_rules: bool = True) -> bool:
        config.device_cfg.stats_zoom_level = self.stats_win.save_zoom()
        self.layout_save()

        try:
            self.simulation.remove_views_from_model(
                self.visual_physical_view,
                self.visual_sensory_view,
                self.visual_perceptual_view,
                self.auditory_physical_view,
                self.auditory_sensory_view,
                self.auditory_perceptual_view,
            )
        except Exception:  # broad on purpose!
            ...

        self.clear_output_windows()

        if not file:
            if Path(config.device_cfg.device_file).is_file():
                start_dir = Path(config.device_cfg.device_file).parent
            elif Path(config.app_cfg.last_device_file).is_file():
                start_dir = Path(config.app_cfg.last_device_file).parent
            else:
                start_dir = str(Path.home())
            device_file, _ = QFileDialog.getOpenFileName(
                self,
                "Choose EPICpy Device File",
                str(start_dir),
                "Python Files (*.py)",
            )
        else:
            device_file = file

        with loading_cursor_context():
            self.simulation.on_load_device(device_file, quiet)

            # Model was reset, so we have to reconnect views and such
            if self.simulation and self.simulation.has_device() and self.simulation.has_model():
                self.simulation.add_views_to_model(
                    self.visual_physical_view,
                    self.visual_sensory_view,
                    self.visual_perceptual_view,
                    self.auditory_physical_view,
                    self.auditory_sensory_view,
                    self.auditory_perceptual_view,
                )
                self.simulation.update_model_output_settings()
                self.clear_ui(visual_views=True, auditory_views=True, normal_output=False, trace_output=True, info_output=False)

                self.context = "".join([c for c in self.simulation.device.device_name if c.isalnum()]).title()
                if self.layout_exists():
                    self.layout_load()
                else:
                    self.layout_load("Default")

                if auto_load_rules and config.device_cfg.rule_files:
                    self.simulation.choose_rules(config.device_cfg.rule_files)

                if self.simulation.has_device():
                    html = self.simulation.device.show_output_stats()
                    self.stats_win.setHtml(html)

                # Restore stats zoom level from device config
                self.stats_win.set_target_zoom(config.device_cfg.stats_zoom_level)

                # Ensure default tab order and raise Info tab
                self.tabifyDockWidget(self.dockInfo, self.dockNormal)
                self.tabifyDockWidget(self.dockNormal, self.dockTrace)
                self.dockInfo.raise_()

                # Sync parallel runs checkbox with loaded config.
                # Block signals to avoid the toggled handler writing the same value back
                # to config (and triggering a redundant disk save).
                self.actionAllow_Parallel_Runs.blockSignals(True)
                self.actionAllow_Parallel_Runs.setChecked(config.device_cfg.allow_parallel_runs)  # type: ignore[attr-defined]
                self.actionAllow_Parallel_Runs.blockSignals(False)

                # Track this device in recent devices list
                self._add_recent_device(device_file)

            else:
                return False

            return True

    def open_device_folder(self):
        operating_system = platform.system()
        if operating_system == "Linux":
            open_cmd = "xdg-open"
        elif operating_system == "Darwin":
            open_cmd = "open"
        elif operating_system == "Windows":
            open_cmd = "explorer"
        else:
            open_cmd = ""
            msg = f"ERROR: Opening project folder when OS=='{operating_system}' is not yet implemented!n"
            try:
                Exception_out(msg)
            except Exception:
                print(msg)
        if open_cmd and config.device_cfg.device_file:
            cmd = [
                open_cmd,
                str(Path(config.device_cfg.device_file).resolve().parent),
            ]
            subprocess.run(args=cmd)

    def choose_rules(self, rules: Optional[list] = None) -> bool:
        return self.simulation.choose_rules(rules)

    def recompile_rules(self):
        self.simulation.recompile_rules()

    def run_one_step(self):
        if self.run_state in (RUNNABLE, PAUSED):
            self.simulation.device.set_parameter_string(config.device_cfg.device_params)

            self.simulation.run_one_step()
        else:
            Info_out(hcolor("WARNING: Unable to complete RunOneStep action because run_state is not RUNNABLE\n", "gold"))

    def run_normal(self, parallel: bool = True):
        """
        Run all permutations of the currently loaded simulation.
        If parallel is True and the device parameter string has permutations like [Easy|Hard],
        then run all permutations in parallel using separate processes. Otherwise, use the
        existing sequential approach.
        """

        # Resume from paused state - just continue without resetting
        if self.run_state == PAUSED:
            self.simulation.run()
            return

        if self.run_state != RUNNABLE:
            Info_out(hcolor("ERROR: Unable to complete RunNormal action because run_state is not RUNNABLE<font>\n", "red"))
            return

        self.simulation.current_rule_index = 0
        rule_name = Path(self.simulation.rule_files[self.simulation.current_rule_index].rule_file).name
        Normal_out(emoji_box(f"RULE FILE: {rule_name}", line="thick") + "\n")

        # Determine the parameter string to use
        if self.simulation.rule_files[self.simulation.current_rule_index].parameter_string:
            param_string = self.simulation.rule_files[self.simulation.current_rule_index].parameter_string
        elif config.device_cfg.device_params:
            param_string = config.device_cfg.device_params
        else:
            param_string = self.simulation.device.get_parameter_string()

        # Check for permutations in parameter string
        # Use the checkbox state directly as the source of truth for the parallel decision,
        # rather than config.device_cfg.allow_parallel_runs which can get out of sync.
        allow_parallel = parallel and self.actionAllow_Parallel_Runs.isChecked()
        if allow_parallel and has_permutations(param_string):
            self._run_parallel(param_string)
            return

        # Sequential execution (normal serial run)
        param_count = 1 if not has_permutations(param_string) else len(expand_permutations(param_string))
        Info_out(hcolor(f"Running {param_count} parameter permutations serially...\n", bold=True))
        self.simulation.device.set_parameter_string(param_string)
        self.simulation.run()

    def _run_parallel(self, param_string: str) -> list[SimulationResult] | None:
        """
        Run all parameter permutations in parallel using separate processes.
        Parameter string are indicated with [option1|option2] syntax.
        """
        rule_file = self.simulation.rule_files[self.simulation.current_rule_index].rule_file
        device_file = config.app_cfg.last_device_file

        # Create configurations for each permutation
        sim_configs = create_sim_configs_from_permutations(
            device_file=device_file,
            rule_file=rule_file,
            base_param_string=param_string,
            output_settings=OutputSettings.from_device_config(config.device_cfg),
            run_command=config.device_cfg.run_command,
            run_command_value=int(config.device_cfg.run_command_value),
            visual_encoder_file=config.device_cfg.visual_encoder,
            auditory_encoder_file=config.device_cfg.auditory_encoder,
        )

        Info_out(hcolor(f"Running {len(sim_configs)} parameter permutations in parallel...\n", bold=True))
        for i, cfg in enumerate(sim_configs, 1):
            Info_out(f"  {i}. {cfg.parameter_string}\n")

        # Run all permutations in parallel **WARNING: Will Temporarily Re-Route All Output_tees to memory**
        # TODO: Consider running this in a background thread to avoid blocking the UI
        device_folder = Path(device_file).parent
        results = run_parallel_simulations(
            sim_configs=sim_configs,
            max_workers=min(len(sim_configs), os.cpu_count() or 4),
            device_folder=device_folder,
        )

        # Restore default Output_tee routing
        for ot in (Normal_out, Debug_out, Device_out, Exception_out, PPS_out):
            ot.clear_py_streams()
            ot.add_py_stream(self.normalTextOutput)
            if EPICPY_DEBUG:
                ot.add_py_stream(sys.stdout)  # for debug
        Exception_out.add_py_stream(sys.stderr)
        Trace_out.clear_py_streams()
        Trace_out.add_py_stream(self.traceTextOutput)

        # move cached output_tee contents where they belong
        if results:
            self._emit_outputs_from_parallel_run(results=tuple(results))

        # Report results
        Info_out("\nParallel execution complete. Results:\n")
        for result in results:
            status = hcolor("SUCCESS", "green", paragraph=False) if result.success else hcolor("FAILED", "red", paragraph=False)
            Info_out(f"  [{status}] {result.sim_config.parameter_string}")
            if result.success:
                Info_out(f" ➡️ Simulated time: {result.simulated_time_ms}ms, Wall time: {result.run_time_seconds:.2f}s\n")
            else:
                Info_out(f" ➡️ Error: {result.error_message}\n")

        # this one is special, don't restore until the above is done
        Info_out.clear_py_streams()
        Info_out.add_py_stream(self.infoTextOutput)
        Info_out("Parallel Run Finished!\n")

        # show updated graph
        try:
            html = self.simulation.device.show_output_stats()
            self.stats_win.setHtml(html)
        except Exception as e:
            msg = f"""
                <span style="color: red;">
                <h2>Unable to render analysis for 
                {self.simulation.device.get_name() if self.simulation.has_device else "Current Device"}
                </h2>:<br><b>{str(e)}</b>
                </span>
                """
            self.stats_win.setHtml(msg)
            Info_out(msg)

    def _emit_outputs_from_parallel_run(
        self, results: tuple[SimulationResult, ...], mode: Literal["All Runs", "Last Run"] = "Last Run"
    ):
        _mode = mode if mode in ["All Runs", "Last Run"] else "Last Run"
        from collections import deque
        from itertools import chain

        if _mode == "All Runs":
            start = 0  # All output
        else:
            start = -1  # Output from last run only

        self.normalTextOutput.load(deque(chain.from_iterable(result.outputs["Normal_out"] for result in results[start:])))
        self.traceTextOutput.load(deque(chain.from_iterable(result.outputs["Trace_out"] for result in results[start:])))

    def run_next_cycle(self):
        self.simulation.run_next_cycle()

    def pause_simulation(self):
        self.simulation.pause_simulation()

    def halt_simulation(self):
        self.simulation.halt_simulation(reason="user_stop", force=True)

    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # =========================================

    def _get_recent_devices(self) -> list[str]:
        devices = self.window_settings.value("recent_devices", [])
        if isinstance(devices, str):
            devices = [devices] if devices else []
        return devices

    def _add_recent_device(self, device_file: str):
        devices = self._get_recent_devices()
        if device_file in devices:
            devices.remove(device_file)
        devices.insert(0, device_file)
        devices = devices[:10]
        self.window_settings.setValue("recent_devices", devices)
        self._refresh_recent_devices_menu()

    def _refresh_recent_devices_menu(self):
        menu = self.recent_devices_menu
        menu.clear()
        devices = self._get_recent_devices()

        # One-time migration: seed from last_device_file if no recent devices yet
        if not devices and config.app_cfg.last_device_file and Path(config.app_cfg.last_device_file).is_file():
            devices = [config.app_cfg.last_device_file]
            self.window_settings.setValue("recent_devices", devices)

        if devices:
            for path in devices:
                action = menu.addAction(path)
                action.triggered.connect(partial(self.session_reload, device_file=path, quiet=False))
        else:
            action = menu.addAction("(No Recent Devices)")
            action.setEnabled(False)

        menu.addSeparator()
        clear_action = menu.addAction("Clear Recent Devices")
        clear_action.triggered.connect(self._clear_recent_devices)

    def _clear_recent_devices(self):
        self.window_settings.remove("recent_devices")
        self._refresh_recent_devices_menu()

    def session_reload(self, device_file: str, quiet: bool = True):
        if Path(device_file).is_file():
            self.on_load_device(device_file, quiet)
        else:
            Info_out(hcolor(f"Unable to reload session: Device file not found:\n{device_file}", "red"))

        if self.simulation and self.simulation.has_device():
            if config.device_cfg.rule_files:
                Info_out(f"{len(config.device_cfg.rule_files)} rule files recovered from previous device session: \n")
                for i, rule_file in enumerate(config.device_cfg.rule_files):
                    p = Path(rule_file)
                    if p.is_file():
                        status = hcolor("(Found)", "green", paragraph=False)
                    else:
                        status = hcolor("(Missing)", "red", paragraph=False)
                    Info_out(f"   {p.name} ({status})\n")
                Info_out("\n")
                config.device_cfg.rule_files = [
                    rule_file for rule_file in config.device_cfg.rule_files if Path(rule_file).is_file()
                ]
                # self.simulation.rule_files = config.device_cfg.rule_files

                self.simulation.rule_files = [
                    RunInfo(False, "", str(Path(item).resolve()), "", False, False) for item in config.device_cfg.rule_files
                ]

                self.simulation.current_rule_index = 0
            else:
                self.simulation.rule_files = []
                self.simulation.current_rule_index = 0

            if self.simulation.rule_files:
                Info_out(
                    f'Attempting to compile first rule in ruleset list ("{Path(self.simulation.rule_files[0].rule_file).name}")\n'
                )
                self.simulation.compile_rule(self.simulation.rule_files[0].rule_file)

            try:
                assert Path(config.device_cfg.visual_encoder).is_file()
                vis_encoder = Path(config.device_cfg.visual_encoder)
            except AssertionError:
                vis_encoder = None
                config.device_cfg.visual_encoder = ""

            try:
                assert Path(config.device_cfg.auditory_encoder).is_file()
                aud_encoder = Path(config.device_cfg.auditory_encoder)
            except AssertionError:
                aud_encoder = None
                config.device_cfg.auditory_encoder = ""

            # NOTE: we're currently ignoring setting:
            #        config.device_cfg.auto_load_last_encoders
            #        and always loading encoders if they are defined.
            #        If modeller doesn't want an encoder, they should just unload it.

            if aud_encoder:
                self.simulation.on_load_encoder(
                    kind="Auditory",
                    file=config.device_cfg.auditory_encoder,
                    quiet=False,
                )

            if vis_encoder:
                self.simulation.on_load_encoder(
                    kind="Visual",
                    file=config.device_cfg.visual_encoder,
                    quiet=False,
                )

    def setup_views(self):
        self.visual_views = {
            "Visual Physical": VisualViewWin(
                "Visual Physical",
                "Visual Physical",
            ),
            "Visual Sensory": VisualViewWin(
                "Visual Sensory",
                "Visual Sensory",
            ),
            "Visual Perceptual": VisualViewWin(
                "Visual Perceptual",
                "Visual Perceptual",
            ),
        }
        self.visual_physical_view = EPICVisualView(self.visual_views["Visual Physical"])
        self.visual_sensory_view = EPICVisualView(self.visual_views["Visual Sensory"])
        self.visual_perceptual_view = EPICVisualView(self.visual_views["Visual Perceptual"])

        self.auditory_views = {
            "Auditory Physical": AuditoryViewWin(
                "Auditory Physical",
                "Auditory Physical",
            ),
            "Auditory Sensory": AuditoryViewWin(
                "Auditory Sensory",
                "Auditory Sensory",
            ),
            "Auditory Perceptual": AuditoryViewWin(
                "Auditory Perceptual",
                "Auditory Perceptual",
            ),
        }
        self.auditory_physical_view = EPICAuditoryView(self.auditory_views["Auditory Physical"])
        self.auditory_sensory_view = EPICAuditoryView(self.auditory_views["Auditory Sensory"])
        self.auditory_perceptual_view = EPICAuditoryView(self.auditory_views["Auditory Perceptual"])

        for win in (
            self.visual_physical_view,
            self.visual_sensory_view,
            self.visual_perceptual_view,
            self.auditory_physical_view,
            self.auditory_sensory_view,
            self.auditory_perceptual_view,
        ):
            win.set_changed()

    def stop_simulation(self):
        if isinstance(self.simulation, Simulation):
            self.simulation.halt_simulation(reason="user_stop")

    def close_output_files(self):
        # FIXME: Revisit this when we figure out how to re=do text output
        # if Normal_out.is_present(self.normal_out_fs):
        #     Normal_out.remove_stream(self.normal_out_fs)
        # if Trace_out.is_present(self.trace_out_fs):
        #     Trace_out.remove_stream(self.trace_out_fs)
        ...

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

    def closeEvent(self, event: QCloseEvent):
        if self.closing:
            print("0. got duplicate close event")
            event.ignore()
            return

        self.closing = True

        def debug_print(txt: str, alt_txt: str = ""):
            if EPICPY_DEBUG:
                print(txt)
            elif alt_txt:
                print(alt_txt)

        debug_print("[DEBUG] Shutting Down EPICpy:", "Shutting Down EPICpy...")
        debug_print("---------------------")

        debug_print("1. Stopping simulation...")
        if self.run_state == RUNNING:
            self.halt_simulation()

        debug_print("2. ---")

        debug_print("3. Saving layout...")
        config.device_cfg.stats_zoom_level = self.stats_win.save_zoom()
        self.layout_save()  # save under current context (device name or "Main")

        debug_print("4. Closing stats window...")
        # self.stats_win.can_close = True
        self.stats_win.close()  # destroy()

        debug_print("5. Closing views...")
        try:
            for view in chain(self.visual_views.values(), self.auditory_views.values()):
                view.can_close = True
                view.close()  # destroy()
        except Exception:
            debug_print("\tWARNING: Unable to successfully close all views.")

        debug_print("6. Closing output files...")
        self.close_output_files()

        debug_print("7. Removing views from model...")
        try:
            self.simulation.remove_views_from_model(
                self.visual_physical_view,
                self.visual_sensory_view,
                self.visual_perceptual_view,
                self.auditory_physical_view,
                self.auditory_sensory_view,
                self.auditory_perceptual_view,
            )
        except Exception:
            debug_print("\tWARNING: Unable to cleanly release views from model.")

        debug_print("8. Pausing and stopping simulation -- seems redundant, halted above...")
        if self.simulation:
            try:
                self.simulation.pause_simulation()
                if self.simulation.has_model():
                    self.simulation.model.stop()
                if self.simulation.has_device():
                    self.simulation.device.stop_simulation()
                if self.simulation.has_coordinator():
                    self.simulation.instance.shutdown_simulation()
            except Exception as e:
                log.warning(f"Unable to stop and shutdown simulation: {e}")

        debug_print("9. Shutting down Output_tee instances...")
        ot_info = zip(
            (
                "Normal_out",
                "Trace_out",
                "Exception_out",
                "Debug_out",
                "Device_out",
                "PPS_out",
                "Stats_out",
            ),
            (
                Normal_out,
                Trace_out,
                Exception_out,
                Debug_out,
                Device_out,
                PPS_out,
                Stats_out,
            ),
        )

        for ot_name, ot in ot_info:
            debug_print(f"\t{ot_name}...")
            ot.py_flush()
            ot.clear_py_streams()
            ot.py_close()

        debug_print("10. Closing application window.")
        super().closeEvent(event)

        print("Done.")

    def update_theme(self):
        try:
            scheme = QGuiApplication.styleHints().colorScheme()
            if scheme == Qt.ColorScheme.Dark:
                set_dark_style(QApplication.instance())
            else:
                set_light_style(QApplication.instance())
        except AttributeError:
            ...

        # Update MemLargeTextView widgets which do custom painting
        if hasattr(self, "normalTextOutput"):
            self.normalTextOutput.update_theme()
        if hasattr(self, "traceTextOutput"):
            self.traceTextOutput.update_theme()

        # Update QWebEngineView (stats window) dark mode
        if hasattr(self, "stats_win"):
            try:
                is_dark = QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
                self.stats_win.settings().setAttribute(QWebEngineSettings.WebAttribute.ForceDarkMode, is_dark)
            except AttributeError:
                pass  # Older Qt versions may not support this

    def changeEvent(self, event):
        if event.type() == QEvent.Type.ThemeChange:
            self.update_theme()
        super().changeEvent(event)

    def hideEvent(self, event: QHideEvent) -> None:
        QMainWindow.hideEvent(self, event)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)

        config.set_ready(True)

        # Only adjust once
        if not self.layout_exists("Default"):
            self.layout_save("Default")
            self.default_top_custom_settings = self.topAreaInner.get_custom_settings()
            self.default_middle_custom_settings = self.middleAreaInner.get_custom_settings()
        else:
            self.layout_load("Main")  # regular and custom

    def set_view_background_image_from_signal(self, bd_info: dict):
        self.set_view_background_image(
            view_type=bd_info["view_type"],
            img_filename=bd_info["img_filename"],
            scaled=bd_info["scaled"],
        )

    def set_view_background_image(self, view_type: str, img_filename: str, scaled: bool = True):
        if not config.device_cfg.allow_device_images:
            return

        _view_type = view_type.lower()
        try:
            assert _view_type in (
                "visual",
                "auditory",
            ), "view_type must be in ('visual', 'auditory')"
            assert Path(img_filename).is_file(), f"{img_filename} is not a valid image file"
            if _view_type == "visual":
                views = self.visual_views
            elif _view_type == "auditory":
                views = self.auditory_views
            else:
                raise ValueError(f"set_view_background_image: Got bad view_type ({_view_type}), should be in (visual, auditory)")

            for view in views.values():
                view.set_background_image(img_filename, scaled=scaled)
        except Exception as e:
            log.error(f"Unable to set view background image [{e}]")

    def enable_view_updates(self, enable: bool = True):
        for view in (*self.visual_views.values(), *self.auditory_views.values()):
            view.allow_updates(enable)

    def set_view_batch_mode(self, enable: bool = True):
        """
        Enable/disable batch mode on all views. When enabled, views accumulate
        state changes without triggering repaints until force_view_display is called.
        """
        for view in (*self.visual_views.values(), *self.auditory_views.values()):
            view.set_batch_mode(enable)

    def force_view_display(self, model_time: float):
        """Force all views to repaint, regardless of batch mode."""
        for view in (*self.visual_views.values(), *self.auditory_views.values()):
            view.current_time = model_time
            view.force_display()

    def clear_ui(
        self,
        visual_views: bool = True,
        auditory_views: bool = True,
        normal_output: bool = True,
        info_output: bool = True,
        trace_output: bool = True,
        stats_output: bool = True,
    ):
        if visual_views:
            for view in self.visual_views.values():
                view.clear()
        if auditory_views:
            for view in self.auditory_views.values():
                view.clear()
        if normal_output:
            self.normalTextOutput.clear()
        if info_output:
            self.infoTextOutput.clear()
        if trace_output:
            self.traceTextOutput.clear()
        if stats_output:
            self.stats_win.setHtml("<html><body></body></html>")

    def update_views(self, model_time: float):
        # if visual_views:
        for view in self.visual_views.values():
            view.current_time = model_time
            view.can_draw = True
        # if auditory_views:
        for view in self.auditory_views.values():
            view.current_time = model_time
            view.can_draw = True

    def update_text_outputs(self):
        self.normalTextOutput.update_display()
        self.traceTextOutput.update_display()

    def clear(self):
        self.normalTextOutput.clear()

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
        # self.actionLogging.setEnabled(has_device)

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

    def toggle_allow_parallel_runs(self, checked: bool):
        """Toggle the allow_parallel_runs setting."""
        config.device_cfg.allow_parallel_runs = checked

    def show_run_settings(self):
        if not self.simulation or not self.simulation.has_device():
            Info_out(hcolor("WARNING: Unable to open run settings, load a device first.\n", "gold"))
            return

        # ---- Because of device parameter settings, we're just recreating this every
        #      time. So first, let's cleanly close the dialog if it was previously created

        if hasattr(self, "run_settings_dialog"):
            self.run_settings_dialog.close()

        # ----- Fill in Device Parameters and then Show Dialog

        if self.simulation and self.simulation.has_device() and self.simulation.has_model():
            if hasattr(self.simulation.device, "delete_data_file"):
                delete_data_func = self.simulation.device.delete_data_file
            else:
                delete_data_func = None

            if hasattr(self.simulation.device, "data_file_info"):
                data_info_func = self.simulation.device.data_file_info
            else:
                data_info_func = None
        else:
            delete_data_func, data_info_func = None, None

        self.run_settings_dialog = RunSettingsWin(
            self.simulation.default_device_parameters,
            delete_data_func,
            data_info_func,
            self.simulation,
        )
        self.run_settings_dialog.ui.pushButtonDeleteData.setEnabled(delete_data_func is not None)

        self.run_settings_dialog.ui.lineEditDeviceParameters.setText("")
        if config.device_cfg.device_params:
            self.run_settings_dialog.ui.lineEditDeviceParameters.setText(config.device_cfg.device_params)
            Info_out(f'Device parameters "{config.device_cfg.device_params}" set from previous device session.\n')
        else:
            device_params = self.simulation.device.get_parameter_string()
            self.run_settings_dialog.ui.lineEditDeviceParameters.setText(device_params)
            config.device_cfg.device_params = device_params

        self.run_settings_dialog.setup_options()

        self.run_settings_dialog.setModal(True)
        self.run_settings_dialog.exec()  # needed to make it modal?!

        # ----- Dialog Closed, deal with any changes

        if self.run_settings_dialog.ok:
            Info_out("Settings changes accepted.\n")
            config.device_cfg.device_params = self.run_settings_dialog.ui.lineEditDeviceParameters.text()
            self.simulation.device.set_parameter_string(config.device_cfg.device_params)
        else:
            Info_out("Settings changes ignored.\n")
            config.device_cfg.rollback()

    def show_display_settings_dialogs(self):
        try:
            self.display_settings_dialog.close()
        except Exception:
            ...

        self.display_settings_dialog = DisplayControlsWin()

        self.display_settings_dialog.setup_options()
        self.display_settings_dialog.setModal(True)
        self.display_settings_dialog.exec()  # needed to make it modal?!

        if self.display_settings_dialog.ok:
            Info_out("Display controls changes accepted.\n")
            if self.simulation and self.simulation.has_device() and self.simulation.has_model():
                self.simulation.update_model_output_settings()
        else:
            Info_out("Display controls changes ignored.\n")
            config.device_cfg.rollback()

    def show_trace_settings_dialogs(self):
        if hasattr(self, "trace_settings_dialog"):
            self.trace_settings_dialog.setModal(True)
            self.trace_settings_dialog.exec()  # needed to make it modal?!
        else:
            self.trace_settings_dialog = TraceSettingsWin()
            self.trace_settings_dialog.setup_options()
            self.trace_settings_dialog.setModal(True)
            self.trace_settings_dialog.exec()  # needed to make it modal?!

        if self.trace_settings_dialog.ok:
            Info_out(f"{e_info} Trace Settings changes accepted.\n")
            self.simulation.update_model_output_settings()
        else:
            Info_out(f"{e_info} Trace Settings changes ignored.\n")
            config.device_cfg.rollback()

    def show_log_settings_dialogs(self):
        raise NotImplementedError("logging from this dialog is not currently supported!")

        if hasattr(self, "log_settings_dialog"):
            self.log_settings_dialog.close()

        self.log_settings_dialog = LoggingSettingsWin()
        self.log_settings_dialog.setup_options()
        self.log_settings_dialog.setModal(True)
        self.log_settings_dialog.exec()  # needed to make it modal?!

        if self.log_settings_dialog.ok:
            Info_out("Log Settings changes saved.\n")
            self.simulation.update_model_output_settings()
            self.update_output_logging()
        else:
            Info_out("Log Settings changes ignored.\n")
            config.device_cfg.rollback()

    def show_rule_break_settings_dialog(self):
        if not self.simulation or not self.simulation.has_model():
            return

        if hasattr(self, "rule_break_settings_dialog"):
            self.rule_break_settings_dialog.close()

        self.rule_break_settings_dialog = BreakSettingsWin(self.simulation.model)
        self.rule_break_settings_dialog.setup_options()
        self.rule_break_settings_dialog.setModal(True)
        self.rule_break_settings_dialog.exec()  # needed to make it modal?!

    def show_device_options_dialog(self):
        if not self.simulation or not self.simulation.has_device():
            return

        if hasattr(self, "device_options_dialog"):
            self.device_options_dialog.close()

        self.device_options_dialog = DeviceOptionsWin(self.simulation.device)
        self.device_options_dialog.setup_options()
        self.device_options_dialog.setModal(True)
        self.device_options_dialog.exec()  # needed to make it modal?!

    def show_sound_text_settings_dialog(self):
        if not self.simulation or not self.simulation.has_device():
            return

        if hasattr(self, "sound_text_settings_dialog"):
            self.sound_text_settings_dialog.close()

        self.sound_text_settings_dialog = SoundTextSettingsWin()
        self.sound_text_settings_dialog.setup_options()
        self.sound_text_settings_dialog.setModal(True)
        self.sound_text_settings_dialog.exec()  # needed to make it modal?!

    def set_application_font(self):
        # keeping the unused code from below just in case someone complains that they
        #  can't change the font family

        if hasattr(self, "font_size_dialog"):
            self.font_size_dialog.close()

        self.font_size_dialog = FontSizeDialog()
        self.font_size_dialog.setup_options(True)
        self.font_size_dialog.setModal(True)
        self.font_size_dialog.exec()  # needed to make it modal?!

        if self.font_size_dialog.ok:
            config.app_cfg.font_size = self.font_size_dialog.ui.spinBoxFontSize.value()
            config.app_cfg.save_config()

            Info_out(
                f"Application font size changed to {config.app_cfg.font_size} "
                f"pt). NOTE: Some font changes may only take place after application restart.\n"
            )

            font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
            font.setPixelSize(config.app_cfg.font_size)
            QApplication.instance().setFont(font)

            clear_font(self)
            for win in self.visual_views.values():
                win.reset_font()
            for win in self.auditory_views.values():
                win.reset_font()

        else:
            Info_out("No changes made to application font size.\n")
            config.app_cfg.rollback()

    def clear_output_windows(self):
        self.normalTextOutput.clear()
        self.traceTextOutput.clear()
        self.infoTextOutput.clear()
        self.stats_win.setHtml("<html><body></body></html>")

    def about_dialog(self):
        about_window = AboutWin(self)
        about_window.show()

    def run_tests(self, kind: str):
        try:
            config.SAVE_CONFIG_ON_UPDATE = False
            if kind == "StandardRun":
                if fitness.setup_test_device_folder(self):
                    fitness.clear_results()
                    fitness.run_model_test(self, load_encoders=False, close_on_finish=False)
            elif kind == "EncoderRun":
                if fitness.setup_test_device_folder(self):
                    fitness.clear_results()
                    fitness.run_model_test(self, load_encoders=True, close_on_finish=False)
            elif kind == "AllRuns":
                if fitness.setup_test_device_folder(self):
                    fitness.clear_results()
                    # faulthandler.dump_traceback_later(1.0, repeat=True)
                    fitness.run_all_model_tests(self, close_on_finish=False)
                    # faulthandler.cancel_dump_traceback_later()
        finally:
            config.SAVE_CONFIG_ON_UPDATE = True

    def open_help_file(self):
        url = "https://travisseymour.github.io/EPICpyDocs/"
        if webbrowser.open(url):
            Info_out(f"Opened {url} in default web browser.\n")
        else:
            Info_out(hcolor(f"ERROR: Unable to open {url} in default web browser.\n", "red"))

    @staticmethod
    def choose_log_file(file_type: str, ext: str = ".txt") -> str:
        kind = file_type.title()
        assert kind in ("Trace", "Normal", "Stats")

        if kind == "Normal":
            start_file = config.device_cfg.normal_out_file
        elif kind == "Trace":
            start_file = config.device_cfg.trace_out_file
        elif kind == "Stats":
            start_file = config.device_cfg.stats_out_file
            if start_file.endswith(".txt"):
                start_file = start_file.replace(".txt", ".html")
        else:
            start_file = ""

        if not start_file:
            if Path(config.device_cfg.device_file).parent.is_dir():
                start_dir = Path(config.device_cfg.device_file).parent
            else:
                start_dir = Path().home().expanduser()
            start_file = f"{start_dir.stem}_{kind}_output.html" if kind == "Stats" else f"{start_dir.stem}_{kind}_output.txt"
            start_file = str(Path(start_dir, start_file).with_suffix(ext).resolve())

        if kind == "Stats":
            _filter = "HTML-Files (*.html);;Text files (*.txt);;Markdown files (*.md);;ODF files (*.odt);;All Files (*)"
            initial_filter = "HTML-Files (*.html)"
        else:
            _filter = "Text files (*.txt);;HTML-Files (*.html);;Markdown files (*.md);;ODF files (*.odt);;All Files (*)"
            initial_filter = "Text files (*.txt)"

        file_dialog = QFileDialog()
        if platform.system() == "Linux" and kind == "Stats":
            # if we don't do this on linux, initial filename won't have correct extension!
            # it's pretty ugly!
            file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        file, _ = file_dialog.getSaveFileName(
            parent=None,
            caption=f"Specify {kind} Output File",
            dir=str(start_file),
            filter=_filter,
            selectedFilter=initial_filter,
        )

        return file

    def export_output(self, source: MemLargeTextView | QWebEngineView, name: str):
        default_exts = {"Normal": ".txt", "Trace": ".txt", "Stats": ".html"}
        try:
            ext = default_exts[str(name).title()]
        except (ValueError, NameError, IndexError):
            ext = ".txt"

        out_file = self.choose_log_file(name, ext)
        if not out_file:
            Info_out(hcolor(f"WARNING: {name.title()} window text export abandoned.\n", "gold"))
            return

        out_path = Path(out_file)
        if out_path.suffix.lower() not in (".txt", ".html", ".htm"):
            out_path = out_path.with_suffix(ext)

        if isinstance(source, QWebEngineView):
            # Stats output: export HTML asynchronously
            def on_html_ready(html: str):
                try:
                    out_path.write_text(html, encoding="utf-8")
                    Info_out(f"{name.title()} Output window text written to {out_path}\n")
                except OSError as e:
                    Info_out(
                        hcolor(
                            f"ERROR: Unable to write output from '{name.title()}' to '{out_path}': {e}\n",
                            "red",
                        )
                    )

            source.page().toHtml(on_html_ready)
        else:
            # Normal/Trace output: use MemLargeTextView.save()
            success = source.save(out_path)
            if success:
                Info_out(f"{name.title()} Output window text written to {out_path}\n")
            else:
                Info_out(
                    hcolor(
                        f"ERROR: Unable to write output text from '{name.title()}' to '{out_path}'.\n",
                        "red",
                    )
                )

    def delete_datafile(self):
        if self.simulation and self.simulation.has_device() and self.simulation.has_model():
            if hasattr(self.simulation.device, "delete_data_file"):
                self.simulation.device.delete_data_file()

    # =============================================
    # Context Menu Behavior
    # =============================================

    def launchEditor(self, which_file: str = "NormalOut"):
        if which_file == "NormalOut":
            file_id = datetime.datetime.now().strftime("%m%d%y_%H%M%S")
            file_path = Path(self.tmp_folder.name, f"EPICpy_NormalOut_{file_id}.txt")
            if not self.normalTextOutput.save(file_path):
                Exception_out(f"Unable to save {which_file} content to {str(file_path)}. Editor launch abandoned.\n")
        elif which_file == "RuleFile":
            if self.simulation.rule_files:
                if self.simulation.current_rule_index < len(self.simulation.rule_files):
                    file_path = Path(self.simulation.rule_files[self.simulation.current_rule_index].rule_file)
                else:
                    file_path = Path(self.simulation.rule_files[self.simulation.current_rule_index - 1].rule_file)
            else:
                file_path = Path()
                Info_out(
                    hcolor(
                        "ERROR: Unable to open production rules in external text "
                        "editor: [There are possibly no rules currently loaded.]\n",
                        "red",
                    )
                )
        elif which_file == "DataFile":
            try:
                file_path = Path(self.simulation.device.data_filepath)
                assert file_path.is_file()
                err_msg = ""
            except AttributeError:
                file_path = Path()
                err_msg = f"{e_boxed_x} ERROR: Device instance does not appear have expected data_filepath attribute."
            except FileNotFoundError:
                file_path = Path()
                err_msg = (
                    f"ERROR: Device data file does not appear to exist on disk,\n"
                    f"or is not readable:\n"
                    f"{str(self.simulation.device.data_filepath)}"
                )
            except Exception as e:
                file_path = Path()
                err_msg = (
                    f"ERROR: Unexpected error during attempt to open data file"
                    f"\n{str(self.simulation.device.data_filepath)}:\n{e}\n"
                )
            if err_msg:
                Info_out(hcolor(err_msg, "red"))
        else:
            file_path = Path()

        if file_path is not Path():
            try:
                # user has specified the system default editor
                ec_path = has_epiccoder()
                _os = platform.system()
                if (
                    which_file != "DataFile"
                    and hasattr(config.app_cfg, "text_editor")
                    and (config.app_cfg.text_editor.lower() not in ("", "default"))
                    and (Path(config.app_cfg.text_editor).resolve().is_file())
                ):
                    open_cmd = config.app_cfg.text_editor
                elif (
                    which_file != "DataFile"
                    and hasattr(config.app_cfg, "text_editor")
                    and (config.app_cfg.text_editor.lower() in ("", "default"))
                    and ec_path
                ):
                    open_cmd = "epiccoder"  # ec_path
                elif _os == "Linux":
                    open_cmd = "xdg-open"
                elif _os == "Darwin":
                    open_cmd = "open"
                elif _os == "Windows":
                    open_cmd = "start"
                else:
                    open_cmd = ""
                    err_msg = (
                        f"ERROR: EPICpy can only open system default editor on\n"
                        f"Linux, Darwin, and Windows based operating systems.\n"
                        f"It does not currently support your operating system type ({_os}).\n"
                    )
                    Info_out(hcolor(err_msg, "red"))
                if open_cmd:
                    if _os == "Windows":
                        os.startfile(str(file_path.resolve()))
                    else:
                        # subprocess.run([open_cmd, str(file_path.resolve())])
                        run_without_waiting(open_cmd, str(file_path.resolve()))
            except Exception as e:
                Info_out(
                    hcolor(f"ERROR: Unable to open {which_file} file\n{file_path.name} in external text editor\n: {e}\n", "red")
                )

    def start_tool(self, tool_name: Literal["rule_flow", "schematic", "process_viewer", "brain"]):
        match tool_name:
            case "rule_flow":
                try:
                    self.rule_flow_window.close()
                except Exception:
                    ...
                self.rule_flow_window = RuleFlowWindow(trace_widget=self.normalTextOutput)
                self.rule_flow_window.show()
                self.rule_flow_window.update_graph_edges()
                self.rule_flow_window.update_graph()
            case "process_viewer":
                try:
                    self.process_viewer_window.close()
                except Exception:
                    ...
                self.process_viewer_window = ProcessViewerWindow(trace_widget=self.traceTextOutput)
                self.process_viewer_window.show()
            case _:
                Exception_out(f'Tool "{tool_name}" has not been implemented\n')

    # =============================================
    # Keyboard Button Handler
    # =============================================

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    # =============================================
    # Output Text Helpers
    # =============================================

    def get_stats_text(self) -> str:
        """Get plain text from stats window (blocking)."""
        from PySide6.QtCore import QEventLoop

        result: list[str] = []
        loop = QEventLoop()

        def callback(text: str):
            result.append(text)
            loop.quit()

        self.stats_win.page().toPlainText(callback)
        loop.exec()
        return result[0] if result else ""

    # =============================================
    # Device Helpers
    # =============================================

    @property
    def trace_device(self) -> bool:
        return config.device_cfg.trace_device

    def _update_ruleflow_tool_enabled(self, _line_count: int = 0):
        """Enable RuleFlow tool only when normalTextOutput contains cycle data."""
        # Check if any line matches the pattern \d+:Cycle
        has_cycle_data = any(re.match(r"\d+:Cycle", line) for line in self.normalTextOutput.lines)
        self.actionRuleFlowTool.setEnabled(has_cycle_data)

    def _update_process_viewer_tool_enabled(self, _line_count: int = 0):
        """Enable Process Viewer tool only when traceTextOutput contains Human processor data."""
        # Check if any line matches the pattern \d+:Human
        has_human_data = any(re.match(r"\d+:Human", line) for line in self.traceTextOutput.lines)
        self.actionProcessViewerTool.setEnabled(has_human_data)
