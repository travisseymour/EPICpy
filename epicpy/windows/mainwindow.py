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

import os
import platform
import sys

from itertools import chain
from textwrap import dedent

from qtpy.QtCore import QRect, QEvent
from qtpy.QtGui import QHideEvent, QShowEvent, QIcon
from qtpy.QtWidgets import QDockWidget, QWidget, QSizePolicy

from epicpy.tools.rule_flow.rule_flow import RuleFlowWindow
from epicpy.utils import fitness, config
from epicpy.dialogs.aboutwindow import AboutWin
from epicpy.dialogs.fontsizewindow import FontSizeDialog
from epicpy.epic.runinfo import RunInfo
from epicpy.dialogs.sndtextsettingswindow import SoundTextSettingsWin
from epicpy.utils.apputils import clear_font, run_without_waiting, has_epiccoder, loading_cursor_context
from epicpy import get_resource
from epicpy.utils.defaultfont import get_default_font
from epicpy.utils.update_utils import update_available
from epicpy.widgets.largetextview import LargeTextView, CustomLargeTextView
from epicpy.windows import mainwindow_menu
from epicpy.windows.appstyle import set_dark_style, set_light_style
from epicpy.windows.mainwindow_utils import get_desktop_usable_geometry, get_desktop_geometry
from epicpy.windows.statswidget import StatsWidget

from qtpy.QtGui import (
    QTextDocumentWriter,
    QCloseEvent,
    QGuiApplication,
    QAction,
)

from qtpy.QtCore import (
    QTimer,
    QByteArray,
    Qt,
    QSettings,
    QPoint,
    QSize,
)
from qtpy.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMenu,
    QApplication,
    QPlainTextEdit,
)

from pathlib import Path
from epicpy.dialogs.runsettingswindow import RunSettingsWin
from epicpy.dialogs.tracesettingswindow import TraceSettingsWin
from epicpy.dialogs.displaycontrolswindow import DisplayControlsWin
from epicpy.dialogs.breaksettingswindow import BreakSettingsWin
from epicpy.dialogs.devicesettingswindow import DeviceOptionsWin
from epicpy.dialogs.loggingwindow import LoggingSettingsWin
from epicpy.views.visualviewwindow import VisualViewWin
from epicpy.views.auditoryviewwindow import AuditoryViewWin
from epicpy.epic.encoderpassthru import NullVisualEncoder, NullAuditoryEncoder
import datetime
from epicpy.constants.version import __version__
import tempfile
import webbrowser
from loguru import logger as log
from epicpy.epic.epicsimulation import Simulation
from epicpy.constants.stateconstants import *
from epicpy.constants.emoji import *
from typing import Optional, Union, Literal

from epicpy.views.epicpy_textview import EPICTextViewCachedWrite
from epicpy.views.epicpy_visualview import EPICVisualView
from epicpy.views.epicpy_auditoryview import EPICAuditoryView

from epicpy.epiclib.epiclib.pps_globals import PPS_out
from epicpy.epiclib.epiclib.output_tee_globals import (
    Normal_out,
    Trace_out,
    Exception_out,
    Debug_out,
    Device_out,
    Stats_out,
)


class HorizontalDockArea(QMainWindow):
    """
    A QMainWindow subclass that acts as a container for three dock widgets
    arranged horizontally. Each dock contains a label displaying a placeholder text.
    Each label has a minimum size of 392x342, an expanding size policy, and a visible border.
    Each dock is individually closable, movable, and floatable.
    """

    def __init__(
        self, widgets: dict[str, Union[VisualViewWin, AuditoryViewWin]], minimum_view_size: QSize, parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle("Horizontal Dock Area")
        self.setDockNestingEnabled(True)

        docks = []
        for i, widget_name in enumerate(widgets):
            # Each label is wrapped in its own QDockWidget.
            dock = QDockWidget(widget_name, self)
            dock.setObjectName(f"HorizontalDock_{widget_name}_{i}")
            dock.setFloating(False)
            dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetClosable
                | QDockWidget.DockWidgetFeature.DockWidgetMovable
                | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )
            # Remove custom title bar styling; use default.
            widget = widgets[widget_name]
            widget.setMinimumSize(minimum_view_size)
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            widget.setStyleSheet("border: 1px solid #B9B8B6;")
            dock.setWidget(widget)
            docks.append(dock)

        # Arrange the three docks horizontally.
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, docks[0])
        self.splitDockWidget(docks[0], docks[1], Qt.Orientation.Horizontal)
        self.splitDockWidget(docks[1], docks[2], Qt.Orientation.Horizontal)
        self.resizeDocks([docks[0], docks[1], docks[2]], [1, 1, 1], Qt.Orientation.Horizontal)

        for d in docks:
            d.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)

    def get_custom_settings(self):
        settings = {}
        docks = self.findChildren(QDockWidget)
        for dock in docks:
            objname = dock.objectName()
            if objname:
                settings[objname] = {"width": dock.width(), "visible": dock.isVisible()}
        return settings

    def apply_custom_settings(self, settings):
        group = []
        sizes = []
        for objname, info in settings.items():
            dock = self.findChild(QDockWidget, objname)
            if dock:
                if not info.get("visible", True):
                    dock.hide()
                else:
                    dock.show()
                group.append(dock)
                sizes.append(info.get("width", dock.width()))
        if group:
            self.resizeDocks(group, sizes, Qt.Orientation.Horizontal)


class MainWin(QMainWindow):
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
        self.normalPlainTextEditOutput = CustomLargeTextView(parent=self, enable_shortcuts=False)
        self.normalPlainTextEditOutput.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.normalPlainTextEditOutput.setObjectName("MainWindow")  # "plainTextEditOutput"
        self.normalPlainTextEditOutput.customContextMenuRequested.connect(
            self.normalPlainTextEditOutput.contextMenuEvent
        )
        self.normal_out_view = EPICTextViewCachedWrite(text_widget=self.normalPlainTextEditOutput)

        # Attach relevant output tees to this window
        for ot in (Normal_out, Debug_out, Device_out, Exception_out, PPS_out):
            ot.add_py_stream(self.normal_out_view)
            # ot.add_py_stream(sys.stdout)  # for debug

        update = update_available()
        update_msg = f"\n{update}\n" if update else ""
        self.normalPlainTextEditOutput.write(
            f'Normal Out! ({datetime.datetime.now().strftime("%r")} - '
            f"Running on {platform.python_implementation()} {platform.python_version()})"
            f"{update_msg}"
        )

        # to avoid having to load any epic stuff in tracewindow.py, we go ahead and
        # connect Trace_out now
        self.tracePlainTextEditOutput = LargeTextView(self)
        self.tracePlainTextEditOutput.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tracePlainTextEditOutput.setObjectName("TraceWindow")
        self.tracePlainTextEditOutput.customContextMenuRequested.connect(self.tracePlainTextEditOutput.contextMenuEvent)
        self.trace_out_view = EPICTextViewCachedWrite(text_widget=self.tracePlainTextEditOutput)

        # Attach relevant output tees to this window
        Trace_out.add_py_stream(self.trace_out_view)
        # Trace_out.add_py_stream(sys.stdout)  # for debug

        self.tracePlainTextEditOutput.write(f'Trace Out! ({datetime.datetime.now().strftime("%r")})\n')

        # Also, attach std error to exception out in case information is printed before ui crashes
        Exception_out.add_py_stream(sys.stderr)

        # stats widget
        self.stats_win = StatsWidget(self)
        Stats_out.add_py_stream(self.stats_win)

        # init output logging
        self.normal_file_output_never_updated = True
        self.trace_file_output_never_updated = True
        self.update_output_logging()

        # init window properties
        self.visual_views: Optional[dict[str, VisualViewWin]] = None
        self.visual_physical_view: Optional[EPICVisualView] = None
        self.visual_sensory_view: Optional[EPICVisualView] = None
        self.visual_perceptual_view: Optional[EPICVisualView] = None
        self.auditory_views: Optional[dict[str, AuditoryViewWin]] = None
        self.auditory_physical_view: Optional[EPICAuditoryView] = None
        self.auditory_sensory_view: Optional[EPICAuditoryView] = None
        self.auditory_perceptual_view: Optional[EPICAuditoryView] = None

        self.simulation = Simulation(self)

        # init settings dialog properties
        self.run_settings_dialog = None
        self.display_settings_dialog = None
        self.trace_settings_dialog = None
        self.log_settings_dialog = None
        self.rule_break_settings_dialog = None
        self.device_options_dialog = None
        self.epiclib_settings_dialog = None
        self.sound_text_settings_dialog = None
        self.font_size_dialog = None
        self.text_editor_dialog = None

        # finally setup ui

        self.setup_views()
        self.setup_base_ui()

        self.view_updater = QTimer()  # to singleshot view updates that won't slow down main thread
        self.ui_timer = QTimer()  # for updating status bar and other stuff every second or so

        # Setup Menus
        # ===========

        # File Menu Actions
        self.actionLoad_Device: Optional[QAction] = None
        self.actionCompile_Rules: Optional[QAction] = None
        self.actionRecompile_Rules: Optional[QAction] = None
        self.actionLoad_Visual_Encoder: Optional[QAction] = None
        self.actionLoad_Auditory_Encoder: Optional[QAction] = None
        self.actionUnload_Visual_Encoder: Optional[QAction] = None
        self.actionUnload_Auditory_Encoder: Optional[QAction] = None
        self.actionReload_Session: Optional[QAction] = None
        self.actionRun_Simulation_Script: Optional[QAction] = None
        self.actionExport_Normal_Output: Optional[QAction] = None
        self.actionExport_Trace_Output: Optional[QAction] = None
        self.actionExport_Stats_Output: Optional[QAction] = None
        self.actionQuit: Optional[QAction] = None

        # Settings Menu Actions
        self.actionTrace_Settings: Optional[QAction] = None
        self.actionDisplay_Controls: Optional[QAction] = None
        self.actionRule_Break_Settings: Optional[QAction] = None
        self.actionLogging: Optional[QAction] = None
        self.actionAudio_Settings: Optional[QAction] = None
        self.actionDevice_Options: Optional[QAction] = None
        self.actionSound_Text_Settings: Optional[QAction] = None
        self.actionSet_Application_Font: Optional[QAction] = None

        # Run Menu Actions
        self.actionRun_Settings: Optional[QAction] = None
        self.actionRunAll: Optional[QAction] = None
        self.actionRun_One_Step: Optional[QAction] = None
        self.actionPause: Optional[QAction] = None
        self.actionStop: Optional[QAction] = None
        self.actionDelete_Datafile: Optional[QAction] = None

        # Help Menu Actions
        self.actionAbout: Optional[QAction] = None
        self.actionHelp: Optional[QAction] = None
        self.actionStandardRun: Optional[QAction] = None
        self.actionEncoderRun: Optional[QAction] = None
        self.actionAllRuns: Optional[QAction] = None

        # Windows Menu Actions
        self.actionShow_All: Optional[QAction] = None
        self.actionMinimize_All: Optional[QAction] = None
        self.actionShow_Trace_Window: Optional[QAction] = None
        self.actionShow_Stats_Window: Optional[QAction] = None
        self.actionShow_Visual_Views: Optional[QAction] = None
        self.actionShow_Auditory_Views: Optional[QAction] = None
        self.actionClear_Output_Windows: Optional[QAction] = None
        self.actionReset_Layout: Optional[QAction] = None

        # Find Menu Actions
        self.actionFind: Optional[QAction] = None
        self.actionFindNext: Optional[QAction] = None
        self.actionFindPrevious: Optional[QAction] = None

        # Tools Menu Actions
        self.actionRuleFlowTool: Optional[QAction] = None
        self.actionSchematicTool: Optional[QAction] = None
        self.actionProcessGraphTool: Optional[QAction] = None
        self.actionBrainTool: Optional[QAction] = None

        self.rule_flow_window: QMainWindow | None = None
        self.schematic_window: QMainWindow | None = None
        self.process_graph_window: QMainWindow | None = None
        self.brain_tool: QMainWindow | None = None

        mainwindow_menu.setup_menu(self)
        mainwindow_menu.setup_menu_connections(self)

        self.context_menu = QMenu(self)
        self.context_items = {}
        self.create_context_menu_items()

        # connect other ui signals
        # self.normalPlainTextEditOutput.customContextMenuRequested.connect(self.normal_search_context_menu)

        self.default_palette = self.app.palette()
        self.update_theme()

        # notify user if there is a previous session that can be loaded with reload_session?
        exists = Path(config.app_cfg.last_device_file).is_file()
        device = config.app_cfg.last_device_file if config.app_cfg.last_device_file else "None"
        last_session_notice = f"Last Device Loaded: {device} [{exists=}]"
        Normal_out(dedent(last_session_notice))

        self.update_title()
        self.actionReload_Session.setEnabled(Path(config.device_cfg.device_file).is_file())

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
        self.dockBottom = QDockWidget("Normal Output", self)
        self.dockBottom.setObjectName("dockBottom")
        normalPlainText = self.normalPlainTextEditOutput
        normalPlainText.setStyleSheet("border: 2px solid #B9B8B6;")
        self.dockBottom.setWidget(normalPlainText)
        self.dockBottom.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.dockBottom.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        # New: Trace Output dock.
        self.dockTrace = QDockWidget("Trace Output", self)
        self.dockTrace.setObjectName("dockTrace")
        tracePlainText = self.tracePlainTextEditOutput
        tracePlainText.setStyleSheet("border: 2px solid #B9B8B6;")
        self.dockTrace.setWidget(tracePlainText)
        self.dockTrace.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.dockTrace.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        # Stack the left column docks vertically.
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockTop)
        self.splitDockWidget(self.dockTop, self.dockMiddle, Qt.Orientation.Vertical)
        self.splitDockWidget(self.dockMiddle, self.dockBottom, Qt.Orientation.Vertical)
        # Tabify Normal Output and Trace Output so they share the same area.
        self.tabifyDockWidget(self.dockBottom, self.dockTrace)
        # Ensure Normal Output is the active tab.
        self.dockBottom.raise_()

        # ----- Right Dock Widget (Side Dock Area) -----
        self.dockSide = QDockWidget("Statistics Output", self)
        self.dockSide.setObjectName("dockSide")
        plainTextEditSide = self.stats_win
        plainTextEditSide.setStyleSheet("border: 2px solid #B9B8B6;")
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
                [self.dockTop, self.dockMiddle, self.dockBottom],
                [min_top, min_middle, max(available_for_bottom, self.dockBottom.widget().minimumSizeHint().height())],
                Qt.Orientation.Vertical,
            )

        self.update()

    def restore_ui_component(self, component: str):
        components = {
            "visual": self.dockTop,
            "auditory": self.dockMiddle,
            "normal": self.dockBottom,
            "trace": self.dockTrace,
            "stats": self.dockSide,
        }
        if component in components:
            dock = components[component]
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
            if self.simulation and self.simulation.device and self.simulation.model:
                self.simulation.add_views_to_model(
                    self.visual_physical_view,
                    self.visual_sensory_view,
                    self.visual_perceptual_view,
                    self.auditory_physical_view,
                    self.auditory_sensory_view,
                    self.auditory_perceptual_view,
                )
                self.simulation.update_model_output_settings()
                self.update_output_logging()
                self.clear_ui(
                    visual_views=True,
                    auditory_views=True,
                    normal_output=False,
                    trace_output=True,
                )

                self.context = "".join([c for c in self.simulation.device.device_name if c.isalnum()]).title()
                self.layout_load()

                if auto_load_rules and config.device_cfg.rule_files:
                    self.simulation.choose_rules(config.device_cfg.rule_files)

                # if os.environ["EPICPY_DEBUG"] == "1":
                try:
                    self.simulation.device.show_output_stats()
                except Exception:
                    ...

            else:
                return False

    def choose_rules(self, rules: Optional[list] = None) -> bool:
        return self.simulation.choose_rules(rules)

    def recompile_rules(self):
        self.simulation.recompile_rules()

    def run_one_step(self):
        if self.run_state == RUNNABLE:
            self.simulation.device.set_parameter_string(config.device_cfg.device_params)

        self.simulation.run_one_step()

    def run_all(self):
        self.simulation.current_rule_index = 0
        rule_name = Path(self.simulation.rule_files[self.simulation.current_rule_index].rule_file).name
        Normal_out(emoji_box(f"RULE FILE: {rule_name}", line="thick"))

        if not self.simulation.rule_files[self.simulation.current_rule_index].parameter_string:
            # if not running from script, need to set the param string, otherwise it's already
            # handled elsewhere
            self.simulation.device.set_parameter_string(
                config.device_cfg.device_params
                if config.device_cfg.device_params
                else self.simulation.device.get_parameter_string()
            )

        self.simulation.run_all()

    def run_next_cycle(self):
        self.simulation.run_next_cycle()

    def pause_simulation(self):
        self.simulation.pause_simulation()

    def halt_simulation(self):
        self.simulation.halt_simulation()

    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # =========================================

    def session_reload(self, quiet: bool = True):
        if Path(config.app_cfg.last_device_file).is_file():
            self.on_load_device(config.app_cfg.last_device_file, quiet)
        else:
            Normal_out(
                emoji_box(
                    f"ERROR: Unable to reload last session: No previous device found in settings.",
                    line="thick",
                )
            )

        if self.simulation and self.simulation.device:
            if config.device_cfg.rule_files:
                Normal_out(
                    f"{len(config.device_cfg.rule_files)} rule files recovered from " f"previous device session: "
                )
                for i, rule_file in enumerate(config.device_cfg.rule_files):
                    p = Path(rule_file)
                    if p.is_file():
                        status = f"({e_boxed_check} Found)"
                    else:
                        status = f"({e_boxed_x} Missing)"
                    Normal_out(f"   {p.name} ({status})")
                config.device_cfg.rule_files = [
                    rule_file for rule_file in config.device_cfg.rule_files if Path(rule_file).is_file()
                ]
                # self.simulation.rule_files = config.device_cfg.rule_files

                self.simulation.rule_files = [
                    RunInfo(False, "", str(Path(item).resolve()), "", False, False)
                    for item in config.device_cfg.rule_files
                ]

                self.simulation.current_rule_index = 0
            else:
                self.simulation.rule_files = []
                self.simulation.current_rule_index = 0

            if self.simulation.rule_files:
                Normal_out(
                    f"{e_info} Attempting to compile first rule in ruleset list "
                    f'("{Path(self.simulation.rule_files[0].rule_file).name}")'
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

    def remove_file_loggers(self):
        if self.normal_out_view.file_writer.enabled:
            self.normal_out_view.file_writer.close()
        if self.trace_out_view.file_writer.enabled:
            self.trace_out_view.file_writer.close()

    def update_output_logging(self):
        self.remove_file_loggers()

        if config.device_cfg.log_normal_out and config.device_cfg.normal_out_file:
            if self.normal_file_output_never_updated:
                p = Path(config.device_cfg.normal_out_file)
                p.unlink(missing_ok=True)
                self.normal_file_output_never_updated = False

            try:
                self.normal_out_view.file_writer.open(Path(config.device_cfg.normal_out_file))
                Normal_out(f"{e_boxed_check} Normal Output logging set to " f"{config.device_cfg.normal_out_file}")
            except Exception as e:
                Normal_out(
                    emoji_box(
                        f"ERROR: Unable to set Normal Output logging to\n"
                        f"{config.device_cfg.normal_out_file}:\n"
                        f"{e}",
                        line="thick",
                    )
                )

        if config.device_cfg.log_trace_out and config.device_cfg.trace_out_file:
            if self.trace_file_output_never_updated:
                p = Path(config.device_cfg.trace_out_file)
                p.unlink(missing_ok=True)
                self.trace_file_output_never_updated = False

            try:
                self.trace_out_view.file_writer.open(Path(config.device_cfg.trace_out_file))
                Normal_out(f"{e_boxed_check} Trace Output logging set to " f"{config.device_cfg.trace_out_file}")
            except Exception as e:
                Normal_out(
                    emoji_box(
                        f"ERROR: Unable to set Trace Output logging to\n"
                        f"{config.device_cfg.trace_out_file}:\n"
                        f"{e}",
                        line="thick",
                    )
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

    def close_output_files(self):
        # FIXME: Revisit this when we figure out how to re=do text output
        # if Normal_out.is_present(self.normal_out_fs):
        #     Normal_out.remove_stream(self.normal_out_fs)
        # if Trace_out.is_present(self.trace_out_fs):
        #     Trace_out.remove_stream(self.trace_out_fs)
        ...

    def update_ui_status(self):
        if self.run_state == RUNNING:
            self.statusBar().showMessage(f"Run State: Running")
            self.set_ui_running()
        elif self.run_state == PAUSED:
            self.statusBar().showMessage(f"Run State: Paused")
            self.set_ui_paused()
        else:
            self.statusBar().showMessage(f'Run State: {"UnReady" if self.run_state == UNREADY else "Runnable"}')
            self.set_ui_not_running()

    def closeEvent(self, event: QCloseEvent):
        if self.closing:
            print("0. got duplicate close event")
            event.ignore()
            return

        self.closing = True

        print("[DEBUG] Shutting Down EPICpy:")
        print("---------------------")

        print("1. Stopping simulation...")
        if self.run_state == RUNNING:
            self.halt_simulation()

        print("2. Removing file loggers...")
        self.remove_file_loggers()

        print("3. Saving layout...")
        self.layout_save()  # regular and custom

        print("4. Closing stats window...")
        self.stats_win.can_close = True
        self.stats_win.close()  # destroy()

        print("5. Closing views...")
        try:
            for view in chain(self.visual_views.values(), self.auditory_views.values()):
                view.can_close = True
                view.close()  # destroy()
        except Exception as e:
            print(f"\tWARNING: Unable to successfully close all views.")

        print("6. Closing output files...")
        self.close_output_files()

        print("7. Removing views from model...")
        try:
            self.simulation.remove_views_from_model(
                self.visual_physical_view,
                self.visual_sensory_view,
                self.visual_perceptual_view,
                self.auditory_physical_view,
                self.auditory_sensory_view,
                self.auditory_perceptual_view,
            )
        except Exception as e:
            print(f"\tWARNING: Unable to cleanly release views from model.")

        print("8. Pausing and stopping simulation -- seems redundant, halted above...")
        if self.simulation:
            try:
                self.simulation.pause_simulation()
                if self.simulation.model:
                    self.simulation.model.stop()
                if self.simulation.device:
                    self.simulation.device.stop_simulation()
                self.simulation.instance.shutdown_simulation()
            except Exception as e:
                log.warning(f"Unable to stop and shutdown simulation: {e}")

        print("9. Shutting down Output_tee instances...")
        ot_info = zip(
            ("Normal_out", "Trace_out", "Exception_out", "Debug_out", "Device_out", "PPS_out", "Stats_out"),
            (Normal_out, Trace_out, Exception_out, Debug_out, Device_out, PPS_out, Stats_out),
        )

        for ot_name, ot in ot_info:
            print(f"\t{ot_name}...")
            ot.py_flush()
            ot.clear_py_streams()
            ot.py_close()

        print("10. Closing application window.")
        super().closeEvent(event)

    @staticmethod
    def update_theme():
        try:
            scheme = QGuiApplication.styleHints().colorScheme()
            if scheme == Qt.ColorScheme.Dark:
                set_dark_style(QApplication.instance())
            else:
                set_light_style(QApplication.instance())
        except AttributeError:
            ...

    def changeEvent(self, event):
        if event.type() == QEvent.Type.ThemeChange:
            self.update_theme()
        super().changeEvent(event)

    def hideEvent(self, event: QHideEvent) -> None:
        self.normalPlainTextEditOutput.enable_updates = False
        QMainWindow.hideEvent(self, event)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)

        config.set_ready(True)
        self.normalPlainTextEditOutput.enable_updates = True

        # Only adjust once
        if not self.layout_exists("Default"):
            self.layout_save("Default")
        else:
            self.layout_load("Main")  # regular and custom

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
                raise ValueError(
                    f"set_view_background_image: Got bad view_type ({_view_type}), " f"should be in (visual, auditory)"
                )

            for view in views.values():
                view.set_background_image(img_filename, scaled=scaled)
        except Exception as e:
            log.error(f"Unable to set view background image [{e}]")

    def enable_view_updates(self, enable: bool = True):
        for view in (*self.visual_views.values(), *self.auditory_views.values()):
            view.allow_updates(enable)  # determines whether anything is actually done

        # NOTE: The above seems unnecessary if we're adding/removing views from model.
        #       On Linux the above is unnecessary, but on mac, somehow the time updates
        #       are getting through causing a massive slowdown just when user has asked
        #       for max speed. (March 2022 -- is this still the case?)

    def enable_text_updates(self, enable: bool = True):
        if enable:
            self.normalPlainTextEditOutput.resume_writes()
            self.tracePlainTextEditOutput.resume_writes()
            self.normalPlainTextEditOutput.flush()
            self.tracePlainTextEditOutput.flush()
        else:
            self.normalPlainTextEditOutput.pause_writes()
            self.tracePlainTextEditOutput.pause_writes()

    def clear_ui(
        self,
        visual_views: bool = True,
        auditory_views: bool = True,
        normal_output: bool = True,
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
            self.normalPlainTextEditOutput.clear()
        if trace_output:
            self.tracePlainTextEditOutput.clear()
        if stats_output:
            self.stats_win.clear()

    def update_views(self, model_time: float):
        # if visual_views:
        for view in self.visual_views.values():
            view.current_time = model_time
            view.can_draw = True
        # if auditory_views:
        for view in self.auditory_views.values():
            view.current_time = model_time
            view.can_draw = True

    def clear(self):
        self.normalPlainTextEditOutput.clear()

    def set_ui_running(self):
        self.actionStop.setEnabled(True)
        self.actionPause.setEnabled(True)

        self.actionRunAll.setEnabled(False)
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

        self.actionLogging.setEnabled(False)
        self.actionExport_Normal_Output.setEnabled(False)
        self.actionExport_Trace_Output.setEnabled(False)
        self.actionExport_Stats_Output.setEnabled(False)
        self.actionReload_Session.setEnabled(False)

        self.actionDelete_Datafile.setEnabled(False)

        # self.actionRun_Simulation_Script.setEnabled(False)

    def set_ui_paused(self):
        has_rules = (
            True
            if self.simulation and self.simulation.model and self.simulation.model.get_prs_filename() != ""
            else False
        )
        has_device = True if self.simulation and self.simulation.device is not None else False

        has_visual_encoder = (
            self.simulation
            and (self.simulation.visual_encoder is not None)
            and (not hasattr(self.simulation.visual_encoder, "is_null_encoder"))
        )
        has_auditory_encoder = (
            self.simulation
            and (self.simulation.auditory_encoder is not None)
            and (not hasattr(self.simulation.auditory_encoder, "is_null_encoder"))
        )

        self.actionStop.setEnabled(True)
        self.actionPause.setEnabled(False)

        self.actionRunAll.setEnabled(True)
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
        self.actionLogging.setEnabled(True)

        self.actionExport_Normal_Output.setEnabled(True)
        self.actionExport_Trace_Output.setEnabled(True)
        self.actionExport_Stats_Output.setEnabled(True)
        self.actionReload_Session.setEnabled(True)

        self.actionDelete_Datafile.setEnabled(False)

        # self.actionRun_Simulation_Script.setEnabled(True)

    def set_ui_not_running(self):
        runnable = self.run_state == RUNNABLE
        has_rules = (
            True
            if self.simulation and self.simulation.model and self.simulation.model.get_prs_filename() != ""
            else False
        )
        has_device = True if self.simulation and self.simulation.device is not None else False

        has_visual_encoder = (
            self.simulation
            and (self.simulation.visual_encoder is not None)
            and (not hasattr(self.simulation.visual_encoder, "is_null_encoder"))
        )
        has_auditory_encoder = (
            self.simulation
            and (self.simulation.auditory_encoder is not None)
            and (not hasattr(self.simulation.auditory_encoder, "is_null_encoder"))
        )

        self.actionStop.setEnabled(False)
        self.actionPause.setEnabled(False)

        self.actionRunAll.setEnabled(runnable)
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
        self.actionReload_Session.setEnabled(True)

        self.actionDelete_Datafile.setEnabled(has_device)

        # self.actionRun_Simulation_Script.setEnabled(True)

    def update_title(self):
        if self.simulation and self.simulation.device and self.simulation.model:
            device_name = f"""DEVICE: {self.simulation.device.device_name}"""
        else:
            device_name = "DEVICE: None"
        rule_name = (
            f"RULES: " f"{Path(self.simulation.rule_files[self.simulation.current_rule_index].rule_file).name}"
            if self.simulation and self.simulation.rule_files
            else "Rules: None"
        )

        # epiclib = Path(self.epiclib_name).stem.split("_")[-1]
        # year = epiclib[0:4]
        # month = epiclib[4:6]
        # day = epiclib[-2:]
        # epiclib_version = f"EPICLIB: {month}/{day}/{year}"
        epiclib_version = "EPICLIB: 06/28/2016"

        encoders = []
        if self.simulation.visual_encoder and not isinstance(self.simulation.visual_encoder, NullVisualEncoder):
            encoders.append("Visual")
        if self.simulation.auditory_encoder and not isinstance(self.simulation.auditory_encoder, NullAuditoryEncoder):
            encoders.append("Auditory")
        if encoders:
            encoder_info = f'ENCODERS: [{", ".join(encoders)}]'
        else:
            encoder_info = f"ENCODERS: None"

        self.setWindowTitle(
            f"EPICpy v{__version__} | {device_name} | {rule_name} | {epiclib_version} " f"| {encoder_info}"
        )

    def show_run_settings(self):
        if not self.simulation or not self.simulation.device:
            Normal_out(f"{e_boxed_x} Unable to open run settings, load a device first.")
            return

        # ---- Because of device parameter settings, we're just recreating this every
        #      time. So first, let's cleanly close the dialog if it was previously created

        if self.run_settings_dialog is not None:
            self.run_settings_dialog.close()
            self.run_settings_dialog = None

        # ----- Fill in Device Parameters and then Show Dialog

        if self.simulation.device and self.simulation.model:
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
            self.simulation.default_device_parameters, delete_data_func, data_info_func, self.simulation
        )
        self.run_settings_dialog.ui.pushButtonDeleteData.setEnabled(delete_data_func is not None)

        self.run_settings_dialog.ui.lineEditDeviceParameters.setText("")
        if config.device_cfg.device_params:
            self.run_settings_dialog.ui.lineEditDeviceParameters.setText(config.device_cfg.device_params)
            Normal_out(f'Device parameters "{config.device_cfg.device_params}" set from ' f"previous device session.")
        else:
            device_params = self.simulation.device.get_parameter_string()
            self.run_settings_dialog.ui.lineEditDeviceParameters.setText(device_params)
            config.device_cfg.device_params = device_params

        self.run_settings_dialog.setup_options()

        self.run_settings_dialog.setModal(True)
        self.run_settings_dialog.exec()  # needed to make it modal?!

        # ----- Dialog Closed, deal with any changes

        if self.run_settings_dialog.ok:
            Normal_out(f"{e_info} Settings changes accepted.")
            config.device_cfg.device_params = self.run_settings_dialog.ui.lineEditDeviceParameters.text()
            self.simulation.device.set_parameter_string(config.device_cfg.device_params)
        else:
            Normal_out(f"{e_info} Settings changes ignored.")
            config.device_cfg.rollback()

    def show_display_settings_dialogs(self):
        if self.display_settings_dialog is None:
            self.display_settings_dialog = DisplayControlsWin()

        self.display_settings_dialog.setup_options()
        self.display_settings_dialog.setModal(True)
        self.display_settings_dialog.exec()  # needed to make it modal?!

        if self.display_settings_dialog.ok:
            Normal_out(f"{e_info} Display controls changes accepted.")
            if self.simulation and self.simulation.device and self.simulation.model:
                self.update_output_logging()
                self.simulation.update_model_output_settings()
        else:
            Normal_out(f"{e_info} Display controls changes ignored.")
            config.device_cfg.rollback()

    def show_trace_settings_dialogs(self):
        if self.trace_settings_dialog is not None:
            self.trace_settings_dialog.setModal(True)
            self.trace_settings_dialog.exec()  # needed to make it modal?!
        else:
            self.trace_settings_dialog = TraceSettingsWin()
            self.trace_settings_dialog.setup_options()
            self.trace_settings_dialog.setModal(True)
            self.trace_settings_dialog.exec()  # needed to make it modal?!

        if self.trace_settings_dialog.ok:
            Normal_out(f"{e_info} Trace Settings changes accepted.")
            self.simulation.update_model_output_settings()
            self.update_output_logging()
        else:
            Normal_out(f"{e_info} Trace Settings changes ignored.")
            config.device_cfg.rollback()

    def show_log_settings_dialogs(self):
        if self.log_settings_dialog is not None:
            self.log_settings_dialog.setup_options()  # yes, re-setup every time!
            self.log_settings_dialog.setModal(True)
            self.log_settings_dialog.exec()  # needed to make it modal?!
        else:
            self.log_settings_dialog = LoggingSettingsWin()
            self.log_settings_dialog.setup_options()
            self.log_settings_dialog.setModal(True)
            self.log_settings_dialog.exec()  # needed to make it modal?!

        if self.log_settings_dialog.ok:
            Normal_out(f"{e_info} Log Settings changes saved.")
            self.simulation.update_model_output_settings()
            self.update_output_logging()
        else:
            Normal_out(f"{e_info} Log Settings changes ignored.")
            config.device_cfg.rollback()

    def show_rule_break_settings_dialog(self):
        if not self.simulation or not self.simulation.model:
            return
        self.rule_break_settings_dialog = BreakSettingsWin(self.simulation.model)
        self.rule_break_settings_dialog.setup_options()
        self.rule_break_settings_dialog.setModal(True)
        self.rule_break_settings_dialog.exec()  # needed to make it modal?!

    def show_device_options_dialog(self):
        if not self.simulation or not self.simulation.device:
            return
        self.device_options_dialog = DeviceOptionsWin(self.simulation.device)
        self.device_options_dialog.setup_options()
        self.device_options_dialog.setModal(True)
        self.device_options_dialog.exec()  # needed to make it modal?!

    def show_sound_text_settings_dialog(self):
        if not self.simulation or not self.simulation.device:
            return
        self.sound_text_settings_dialog = SoundTextSettingsWin()
        self.sound_text_settings_dialog.setup_options()
        self.sound_text_settings_dialog.setModal(True)
        self.sound_text_settings_dialog.exec()  # needed to make it modal?!

    def set_application_font(self):
        # keeping the unused code from below just in case someone complains that they
        #  can't change the font family

        if self.font_size_dialog is None:
            self.font_size_dialog = FontSizeDialog()
            self.font_size_dialog.setup_options(True)
        self.font_size_dialog.setModal(True)
        self.font_size_dialog.exec()  # needed to make it modal?!

        if self.font_size_dialog.ok:
            config.app_cfg.font_size = self.font_size_dialog.ui.spinBoxFontSize.value()
            Normal_out(
                f"{e_info} Application font size changed to {config.app_cfg.font_size} "
                f"pt). NOTE: Some font changes may only take place after application restart."
            )

            new_font = get_default_font(family=config.app_cfg.font_family, size=config.app_cfg.font_size)
            QApplication.instance().setFont(new_font)
            clear_font(self)
            for win in self.visual_views.values():
                win.reset_font()
            for win in self.auditory_views.values():
                win.reset_font()

        else:
            Normal_out(f"{e_info} No changes made to application font size.")
            config.app_cfg.rollback()

    def clear_output_windows(self):
        self.normalPlainTextEditOutput.clear()
        self.tracePlainTextEditOutput.clear()
        self.stats_win.clear()

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
                    fitness.run_all_model_tests(self, close_on_finish=False)
        finally:
            config.SAVE_CONFIG_ON_UPDATE = True

    def open_help_file(self):
        url = "https://travisseymour.github.io/EPICpyDocs/"
        if webbrowser.open(url):
            Normal_out(f"Opened {url} in default web browser.")
        else:
            Normal_out(f"Error opening {url} in default web browser.")

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
            start_file = (
                f"{start_dir.stem}_{kind}_output.html" if kind == "Stats" else f"{start_dir.stem}_{kind}_output.txt"
            )
            start_file = str(Path(start_dir, start_file).with_suffix(ext).resolve())

        if kind == "Stats":
            _filter = (
                "HTML-Files (*.html);;Text files (*.txt);;" "Markdown files (*.md);;ODF files (*.odt);;All Files (*)"
            )
            initial_filter = "HTML-Files (*.html)"
        else:
            _filter = (
                "Text files (*.txt);;HTML-Files (*.html);;" "Markdown files (*.md);;ODF files (*.odt);;All Files (*)"
            )
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

    def export_output(self, source: QPlainTextEdit, name: str):
        default_exts = {"Normal": ".txt", "Trace": ".txt", "Stats": ".html"}
        try:
            ext = default_exts[str(name).title()]
        except (ValueError, NameError, IndexError):
            ext = ".txt"

        # TODO: integrate this better
        # For now, let StatsWindow handle it's own export
        if name.title() == "Stats":
            self.stats_win.export_contents(self)
            return

        out_file = self.choose_log_file(name, ext)
        if not out_file:
            Normal_out(f"{e_info} {name.title()} window text export abandoned.")
            return

        formats = {
            ".html": b"HTML",
            ".htm": b"HTML",
            ".odf": b"ODF",
            ".markdown": b"markdown",
            ".md": b"markdown",
            ".txt": b"plaintext",
        }

        if Path(out_file).suffix.lower() not in formats:
            out_file = str(Path(out_file).with_suffix(ext))
        writer_format = QByteArray(formats[Path(out_file).suffix.lower()])
        source.document().setModified(True)
        writer = QTextDocumentWriter(out_file)
        writer.setFormat(writer_format)
        success = writer.write(source.document())
        if success:
            source.document().setModified(False)
            Normal_out(f"{e_boxed_check} {name.title()} Output window text written to {out_file}")
        else:
            Normal_out(
                emoji_box(
                    f"ERROR: Unable to write output text from " f"{name.title()} " f"to" f"{out_file})",
                    line="thick",
                )
            )

    def export_output_txt(self, source: LargeTextView, name: str):
        default_exts = {"Normal": ".txt", "Trace": ".txt"}
        try:
            ext = default_exts[str(name).title()]
        except (ValueError, NameError, IndexError):
            ext = ".txt"

        out_file = self.choose_log_file(name, ext)
        if not out_file:
            Normal_out(f"{e_info} {name.title()} window text export abandoned.")
            return

        try:
            Path(out_file).write_text(source.get_text(), encoding="utf-8")
            success = True
            error = ""
        except Exception as e:
            success = False
            error = str(e)

        if success:
            Normal_out(f"{e_boxed_check} {name.title()} Output window text written to {out_file}")
        else:
            Normal_out(
                emoji_box(
                    f"ERROR: Unable to write output text from '{name.title()}' to '{out_file}' ({error})",
                    line="thick",
                )
            )

    def delete_datafile(self):
        if self.simulation.device and self.simulation.model:
            if hasattr(self.simulation.device, "delete_data_file"):
                self.simulation.device.delete_data_file()

    # =============================================
    # Layout Save/Restore
    # =============================================

    def layout_save(self, layout_name: Optional[str] = ""):
        if layout_name:
            layout = layout_name
        else:
            layout = self.context
        # save settings
        self.window_settings.setValue(f"{layout}Geometry", self.saveGeometry())
        self.window_settings.setValue(f"{layout}WindowState", self.saveState())

        # save custom settings
        custom = {}
        outer = {}
        for name in ["dockTop", "dockMiddle", "dockBottom", "dockSide", "dockTrace"]:
            dock = self.findChild(QDockWidget, name)
            if dock:
                outer[name] = {"width": dock.width(), "visible": dock.isVisible()}
        custom["outer"] = outer
        custom["topAreaInner"] = self.topAreaInner.get_custom_settings()
        custom["middleAreaInner"] = self.middleAreaInner.get_custom_settings()
        self.window_settings.setValue(layout, custom)

        self.window_settings.sync()

    def layout_exists(self, layout_name: Optional[str] = "") -> bool:
        if layout_name:
            layout = layout_name
        else:
            layout = self.context
        geometry = self.window_settings.value(f"{layout}Geometry")
        window_state = self.window_settings.value(f"{layout}WindowState")
        return geometry or window_state

    def layout_load(self, layout_name: Optional[str] = ""):
        if layout_name:
            layout = layout_name
        else:
            layout = self.context
        geometry = self.window_settings.value(f"{layout}Geometry")
        if geometry:
            self.restoreGeometry(geometry)
        window_state = self.window_settings.value(f"{layout}WindowState")
        if window_state:
            self.restoreState(window_state)

        custom = self.window_settings.value(layout)
        if not custom:
            return
        if "outer" in custom:
            for name, info in custom["outer"].items():
                dock = self.findChild(QDockWidget, name)
                if dock:
                    if not info.get("visible", True):
                        dock.hide()
                    else:
                        dock.show()
                    self.resizeDocks([dock], [info.get("width", dock.width())], Qt.Orientation.Horizontal)
        if "topAreaInner" in custom:
            self.topAreaInner.apply_custom_settings(custom["topAreaInner"])
        if "middleAreaInner" in custom:
            self.middleAreaInner.apply_custom_settings(custom["middleAreaInner"])

    def layout_reset(self):
        # settings = QSettings()
        # settings.remove(f"{self.context}Geometry")
        # settings.remove(f"{self.context}WindowState")
        # settings.remove(self.context)
        #
        # self.restoreGeometry(self.default_geometry)
        # self.restoreState(self.default_state)
        # self.update()
        # self.showMaximized()
        # QTest.qWait(100)
        # self.showNormal()
        #
        # for name in ["dockTop", "dockMiddle", "dockBottom", "dockSide", "dockTrace"]:
        #     dock = self.findChild(QDockWidget, name)
        #     if dock:
        #         dock.show()

        if self.layout_exists("Default"):
            self.layout_load("Default")
            # self.showMaximized()
            # QTest.qWait(100)
            # self.showNormal()

        def force_visible(custom_dict):
            new_dict = {}
            for key, info in custom_dict.items():
                new_info = info.copy()
                new_info["visible"] = True
                new_dict[key] = new_info
            return new_dict

        self.topAreaInner.apply_custom_settings(force_visible(self.default_top_custom_settings))
        self.middleAreaInner.apply_custom_settings(force_visible(self.default_middle_custom_settings))

    # =============================================
    # Context Menu Behavior
    # =============================================

    def disable_all_context_items(self, ignore: Optional[list[str]] = None):
        _ignore = [item for item in ignore if item] if ignore else []
        for action_name, action_item in self.context_items.items():
            if action_name not in _ignore:
                action_item.setEnabled(False)

    def create_context_menu_items(self):
        # only ones active if self.run_state == RUNNING
        self.context_items["Stop"] = self.context_menu.addAction("Stop")
        self.context_items["Search"] = self.context_menu.addAction("Search")
        # self.context_items['SelectAll'] = self.context_menu.addAction("Select All")
        self.context_menu.addSeparator()
        self.context_items["Copy"] = self.context_menu.addAction("Copy")
        self.context_items["Copy"].setText(f"Copy All Lines")
        self.context_items["CopyLine"] = self.context_menu.addAction("Copy")
        self.context_items["CopyLine"].setText(f"Copy Selected Line")
        self.context_items["Clear"] = self.context_menu.addAction("Clear")
        self.context_menu.addSeparator()
        self.context_items["OpenOutput"] = self.context_menu.addAction("Open Normal Output In Text Editor")
        self.context_items["EditRules"] = self.context_menu.addAction("Edit Production Rule File")
        self.context_items["EditData"] = self.context_menu.addAction("Edit Data Output File")
        self.context_menu.addSeparator()
        self.context_items["OpenFolder"] = self.context_menu.addAction("Open Device Folder")
        self.context_menu.addSeparator()
        self.context_items["Quit"] = self.context_menu.addAction("Quit")

    # TODO: DELETE THIS
    # def normal_search_context_menu(self, event):
    #     device_file = config.device_cfg.device_file
    #     rules_file = config.device_cfg.rule_files[0] if config.device_cfg.rule_files else ""
    #
    #     if self.run_state == RUNNING:
    #         self.disable_all_context_items()
    #         for item in ["Stop", "EditPRS", "OpenOutput", "Quit"]:
    #             try:
    #                 self.context_items[item].setEnabled(True)
    #             except KeyError:
    #                 ...
    #     else:
    #         self.disable_all_context_items()
    #
    #         self.context_items["Search"].setEnabled(True)
    #
    #         self.context_items["Copy"].setEnabled(True)
    #         self.context_items["CopyLine"].setEnabled(self.normalPlainTextEditOutput.has_selection())
    #         self.context_items["Clear"].setEnabled(True)
    #
    #         self.context_items["OpenOutput"].setEnabled(True)
    #
    #         if self.run_state:
    #             self.context_items["EditData"].setEnabled(True)
    #
    #         if Path(rules_file).is_file():
    #             self.context_items["EditRules"].setEnabled(True)
    #
    #         if Path(device_file).is_file():
    #             self.context_items["OpenFolder"].setEnabled(True)
    #
    #         self.context_items["Quit"].setEnabled(True)
    #
    #     if hasattr(self.context_menu, "exec"):
    #         action = self.context_menu.exec(self.mapToGlobal(event))
    #     elif hasattr(self.context_menu, "exec_"):
    #         action = self.context_menu.exec_(self.mapToGlobal(event))
    #     else:
    #         Normal_out(f"Error bringing up context-menu (contact maintainer about exec/exe_ bug)")
    #         action = None
    #         return
    #
    #     if action is None:
    #         return
    #     elif action == self.context_items["Clear"]:
    #         self.clear()
    #     elif action == self.context_items["Search"]:
    #         self.normalPlainTextEditOutput.query_search()
    #     elif action == self.context_items["Quit"]:
    #         self.close()
    #     elif action == self.context_items["Stop"]:
    #         self.halt_simulation()
    #     # elif action == self.context_items['SelectAll']:
    #     #     self.plainTextEditOutput.selectAll()
    #     elif action == self.context_items["Copy"]:
    #         self.normalPlainTextEditOutput.copy_all_to_clipboard()
    #     elif action == self.context_items["CopyLine"]:
    #         self.normalPlainTextEditOutput.copy_line_to_clipboard()
    #     elif action == self.context_items["OpenOutput"]:
    #         self.launchEditor(which_file="NormalOut")
    #     elif action == self.context_items["EditRules"]:
    #         self.launchEditor(which_file="RuleFile")
    #     elif action == self.context_items["EditData"]:
    #         self.launchEditor(which_file="DataFile")
    #     elif action == self.context_items["OpenFolder"]:
    #         OS = platform.system()
    #         if OS == "Linux":
    #             open_cmd = "xdg-open"
    #         elif OS == "Darwin":
    #             open_cmd = "open"
    #         elif OS == "Windows":
    #             open_cmd = "explorer"
    #         else:
    #             open_cmd = ""
    #             err_msg = f"ERROR: Opening device folder when OS=='{OS}' is not yet implemented!"
    #             Normal_out(emoji_box(err_msg, line="thick"))
    #         if open_cmd:
    #             cmd = [open_cmd, str(Path(device_file).resolve().parent)]
    #             Normal_out(f'{" ".join(cmd)}')
    #             subprocess.run(cmd)
    #
    # def trace_search_context_menu(self, event):
    #     contextMenu = QMenu(self)
    #
    #     if hasattr(self, "simulation") and self.run_state == RUNNING:
    #         return
    #
    #     searchAction = contextMenu.addAction("Search")
    #     clearAction = contextMenu.addAction("Clear")
    #     # contextMenu.addSeparator()
    #     # selectAllAction = contextMenu.addAction("Select All")
    #     copyAction = contextMenu.addAction("Copy")
    #     copyAction.setText(f"Copy All Lines)")
    #     # contextMenu.addSeparator()
    #
    #     action = contextMenu.exec(self.mapToGlobal(event))
    #
    #     if action is None:
    #         ...
    #     elif action == clearAction:
    #         self.tracePlainTextEditOutput.flush()
    #     elif action == searchAction:
    #         self.tracePlainTextEditOutput.query_search()
    #     # elif action == selectAllAction:
    #     #     self.tracePlainTextEditOutput.selectAll()
    #     elif action == copyAction:
    #         self.tracePlainTextEditOutput.copy_all_to_clipboard()

    def launchEditor(self, which_file: str = "NormalOut"):
        if which_file == "NormalOut":
            file_id = datetime.datetime.now().strftime("%m%d%y_%H%M%S")
            file_path = Path(self.tmp_folder.name, f"TEMP_EPICPY_NORMALOUT_{file_id}.txt")
            file_path.write_text(self.normalPlainTextEditOutput.get_text())
        elif which_file == "RuleFile":
            if self.simulation.rule_files:
                if self.simulation.current_rule_index < len(self.simulation.rule_files):
                    file_path = Path(self.simulation.rule_files[self.simulation.current_rule_index].rule_file)
                else:
                    file_path = Path(self.simulation.rule_files[self.simulation.current_rule_index - 1].rule_file)
            else:
                file_path = None
                Normal_out(
                    emoji_box(
                        f"ERROR: Unable to open production rules in external text\n"
                        f"editor: [There are possibly no rules currently loaded.]",
                        line="thick",
                    )
                )
        elif which_file == "DataFile":
            try:
                file_path: Optional[Path] = self.simulation.device.data_filepath
                assert file_path.is_file()
                err_msg = ""
            except AttributeError:
                file_path = None
                err_msg = (
                    f"{e_boxed_x} ERROR: Device instance does not appear have " f"expected data_filepath attribute."
                )
            except FileNotFoundError:
                file_path = None
                err_msg = (
                    f"ERROR: Device data file does not appear to exist on disk,\n"
                    f"or is not readable:\n"
                    f"{str(self.simulation.device.data_filepath)}"
                )
            except Exception as e:
                file_path = None
                err_msg = (
                    f"ERROR: Unexpected error during attempt to open data file\n"
                    f"{str(self.simulation.device.data_filepath)}:\n"
                    f"{e}"
                )
            if err_msg:
                Normal_out(emoji_box(err_msg, line="thick"))
        else:
            file_path = None

        if file_path is not None:

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
                        f"It does not currently support your operating system type ({_os})."
                    )
                    Normal_out(emoji_box(err_msg, line="thick"))
                if open_cmd:
                    if _os == "Windows":
                        os.startfile(str(file_path.resolve()))
                    else:
                        # subprocess.run([open_cmd, str(file_path.resolve())])
                        run_without_waiting(open_cmd, str(file_path.resolve()))
            except Exception as e:
                Normal_out(
                    emoji_box(
                        f"ERROR: Unable to open {which_file} file\n" f"{file_path.name} in external text editor\n: {e}",
                        line="thick",
                    )
                )

    def start_tool(self, tool_name: Literal["rule_flow", "schematic", "process_graph", "brain"]):
        match tool_name:
            case "rule_flow":
                try:
                    self.rule_flow_window.close()
                except:
                    ...
                self.rule_flow_window = RuleFlowWindow(trace_textedit=self.normalPlainTextEditOutput)
                self.rule_flow_window.show()
                self.rule_flow_window.update_graph_edges()
                self.rule_flow_window.update_graph()
            case _:
                Exception_out(f'Tool "{tool_name}" has not been implemented')

    # =============================================
    # Keyboard Button Handler
    # =============================================

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        # TODO: Delete this
        # elif event.key() == Qt.Key.Key_F3:
        #     if not self.normalPlainTextEditOutput.continue_find_text():
        #         self.normalPlainTextEditOutput.query_search()
        #     else:
        #         super().keyPressEvent(event)
        # elif event.key() == Qt.Key.Key_F and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
        #     self.normalPlainTextEditOutput.query_search()
        else:
            super().keyPressEvent(event)

    # =============================================
    # Device Helpers
    # =============================================

    @property
    def trace_device(self) -> bool:
        return config.device_cfg.trace_device
