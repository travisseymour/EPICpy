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
import socket

from itertools import chain
from textwrap import dedent

import pandas as pd
from PyQt6.QtCore import pyqtSignal, QEvent
from darktheme.widget_template_pyqt6 import DarkPalette

from epicpy.utils import fitness, config
from epicpy.dialogs.aboutwindow import AboutWin
from epicpy.dialogs.fontsizewindow import FontSizeDialog
from epicpy.dialogs.texteditchoicewindow import TextEditChoiceWin
from epicpy.epic.runinfo import RunInfo
from epicpy.uifiles.mainui import Ui_MainWindow
from epicpy.dialogs.sndtextsettingswindow import SoundTextSettingsWin
from epicpy.windows.statswindow import StatsWin
from epicpy.windows.tracewindow import TraceWin
from PyQt6.QtGui import (
    QTextCursor,
    QTextDocumentWriter,
    QTextDocument,
    QCloseEvent,
    QPalette,
    QColor,
    QMouseEvent,
    QFont,
    QGuiApplication,
    QColorConstants,
)

from PyQt6.QtCore import (
    QTimer,
    QByteArray,
    QRegularExpression,
    Qt,
    QSettings,
    QObject,
    QPoint,
    QSize,
    QThread,
)
from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMenu,
    QApplication,
    QPlainTextEdit,
    QMessageBox,
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
from epicpy.dialogs.epiclibsettingswindow import EPICLibSettingsWin
from epicpy.dialogs.searchwindow import SearchWin
from epicpy.epiccoder.mainwindow import MainWindow as MainEditorWindow
from epicpy.epic.encoderpassthru import NullVisualEncoder, NullAuditoryEncoder
import datetime
import time
import subprocess
from functools import partial
from epicpy.constants.version import __version__
import re
import tempfile
import webbrowser
from loguru import logger as log
from epicpy.epic.epicsimulation import Simulation
from epicpy.constants.stateconstants import *
from epicpy.constants.emoji import *
from typing import Callable, Optional

from epicpy.views.epicpy_textview import EPICTextViewCachedWrite
from epicpy.views.epicpy_visualview import EPICVisualView
from epicpy.views.epicpy_auditoryview import EPICAuditoryView

from epicpy.epiclib.epiclib import initialize_py_streamers, uninitialize_py_streamers


class StateChangeWatcher(QObject):
    """
    In order to make it so that thd SDI window arrangement we're using
    minimizes and/or restored as a unit, we're creating this state changer.
    This approach is easier to deal with than putting a separate state change
    handler in every window we add to the app.

    You have to specify a function to call when a window is minimized or
    restored if you actually want anything to happen on these events.
    """

    def __init__(
        self, parent=None, minimize_func: Callable = None, restore_func: Callable = None
    ):
        super(StateChangeWatcher, self).__init__(parent)
        self.minimize_func = minimize_func
        self.restore_func = restore_func

    def eventFilter(self, obj, event):
        # if obj.isWidgetType() and event.type() == QEvent.WindowStateChange:
        #     if obj.windowState() & Qt.WindowMinimized:
        #         if self.minimize_func is not None:
        #             self.minimize_func()
        #     elif obj.windowState() & Qt.WindowMaximized:
        #         pass
        #     elif obj.windowState() & Qt.WindowNoState:
        #         pass
        #     else:
        #         if self.restore_func is not None:
        #             self.restore_func()

        if obj.isWidgetType() and event.type() == QEvent.Type.Show:
            if obj.windowState() & Qt.WindowState.WindowMinimized:
                if self.minimize_func is not None:
                    self.minimize_func()
            elif obj.windowState() & Qt.WindowState.WindowMaximized:
                pass
            elif obj.windowState() & Qt.WindowState.WindowNoState:
                pass
            else:
                if self.restore_func is not None:
                    self.restore_func()

        return False


class UdpThread(QThread):
    messageReceived = pyqtSignal(str)

    def __init__(self, parent, udp_ip: str, udp_port: int):
        super(UdpThread, self).__init__(parent)
        self.udp_ip = udp_ip  # e.g., "127.0.0.1"
        self.udp_port = udp_port  # e.g., 13047
        self.is_running = True

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.udp_ip, self.udp_port))

        while self.is_running:
            data, addr = sock.recvfrom(4096)
            message = data.decode("utf-8")
            self.messageReceived.emit(message)

    def stop(self):
        self.is_running = False


class MainWin(QMainWindow):
    def __init__(self, app: QApplication):
        super(MainWin, self).__init__()
        self.app = app
        self.setObjectName("MainWindow")
        self.view_type = b"NormalOut"
        self.ok = False
        self.tmp_folder = tempfile.TemporaryDirectory()
        self.closing = False

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setCentralWidget(self.ui.plainTextEditOutput)

        self.setUnifiedTitleAndToolBarOnMac(True)  # doesn't appear to make a difference

        self.window_settings = QSettings("epicpy", "WindowSettings")

        self.statusBar().showMessage("Run Status: UNREADY")

        self.manage_z_order = False
        self.z_order: dict = {
            "Visual Physical": 0.0,
            "Visual Perceptual": 0.0,
            "Visual Sensory": 0.0,
            "Auditory Physical": 0.0,
            "Auditory Perceptual": 0.0,
            "Auditory Sensory": 0.0,
            "MainWindow": 0.0,
            "StatsWindow": 0.0,
            "TraceWindow": 0.0,
        }
        QApplication.instance().focusWindowChanged.connect(self.window_focus_changed)

        self.run_state = UNREADY

        # attach Normal_out and PPS_out output to this window
        self.normal_out_view = EPICTextViewCachedWrite(
            text_widget=self.ui.plainTextEditOutput
        )
        self.normal_out_view.text_widget.dark_mode = config.app_cfg.dark_mode
        self.normal_out_view_thread = UdpThread(
            self, udp_ip="127.0.0.1", udp_port=13050
        )
        self.normal_out_view_thread.messageReceived.connect(self.normal_out_view.write)
        self.normal_out_view_thread.start()

        # to avoid having to load any epic stuff in tracewindow.py, we go ahead and
        # connect Trace_out now
        self.trace_win = TraceWin(parent=self)
        self.trace_win.trace_out_view = EPICTextViewCachedWrite(
            text_widget=self.trace_win.ui.plainTextEditOutput
        )
        self.trace_win.trace_out_view.text_widget.dark_mode = config.app_cfg.dark_mode
        self.trace_win.ui.plainTextEditOutput.mouseDoubleClickEvent = (
            self.mouseDoubleClickEvent
        )
        self.trace_out_view_thread = UdpThread(self, udp_ip="127.0.0.1", udp_port=13048)
        self.trace_out_view_thread.messageReceived.connect(
            self.trace_win.trace_out_view.write
        )
        self.trace_out_view_thread.start()

        # self.debug_out_view_thread = UdpThread(self, udp_ip="127.0.0.1", udp_port=13049)
        # self.debug_out_view_thread.messageReceived.connect(self.trace_win.trace_out_view.write)
        # self.debug_out_view_thread.start()

        # self.pps_out_view_thread = UdpThread(self, udp_ip="127.0.0.1", udp_port=13053)
        # self.pps_out_view_thread.messageReceived.connect(self.trace_win.trace_out_view.write)
        # self.pps_out_view_thread.start()

        # in order to link epiclib Output_tees to Python, we need to set up py_streamers

        initialize_py_streamers(
            enable_normal=True,
            enable_trace=True,
            enable_debug=True,
            enable_pps=True,
        )

        # init output logging

        self.normal_file_output_never_updated = True
        self.trace_file_output_never_updated = True
        self.update_output_logging()

        self.stats_win = StatsWin(parent=self)

        self.simulation = Simulation(self)

        self.search_pattern = ""
        self.search_using_regex = False
        self.search_ignore_case = False
        self.search_dialog = SearchWin()
        self.search_dialog.setModal(True)
        self.ui.actionFind.triggered.connect(self.query_search)
        self.ui.actionFind.setShortcut("Ctrl+F")
        self.ui.actionFindNext.triggered.connect(self.do_search)
        self.ui.actionFindNext.setShortcut("F3")
        self.ui.actionFindPrevious.triggered.connect(
            partial(self.do_search, backwards=True)
        )
        self.ui.actionFindPrevious.setShortcut("Shift+F3")

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
        self.editor_window: Optional[MainEditorWindow] = None

        # setup state change watcher so all min or max together
        # note: this has to go before self.setup_view()
        self.state_watcher = StateChangeWatcher(
            self,
            minimize_func=self.minimize_windows,
            restore_func=self.un_minimize_windows,
        )
        self.installEventFilter(self.state_watcher)
        self.trace_win.installEventFilter(self.state_watcher)

        self.visual_views: Optional[dict[str, VisualViewWin]] = None
        self.visual_physical_view: Optional[EPICVisualView] = None
        self.visual_sensory_view: Optional[EPICVisualView] = None
        self.visual_perceptual_view: Optional[EPICVisualView] = None
        self.auditory_views: Optional[dict[str, AuditoryViewWin]] = None
        self.auditory_physical_view: Optional[EPICAuditoryView] = None
        self.auditory_sensory_view: Optional[EPICAuditoryView] = None
        self.auditory_perceptual_view: Optional[EPICAuditoryView] = None
        self.setup_views()

        self.view_updater = (
            QTimer()
        )  # to singleshot view updates that won't slow down main thread
        self.ui_timer = (
            QTimer()
        )  # for updating status bar and other stuff every second or so

        self.connect_menu_signals()

        # connect other ui signals
        self.ui.plainTextEditOutput.customContextMenuRequested.connect(
            self.search_context_menu
        )
        self.ui.plainTextEditOutput.mouseDoubleClickEvent = self.mouseDoubleClickEvent

        self.ui.plainTextEditOutput.clear()
        self.ui.plainTextEditOutput.write(
            f'Normal Out! ({datetime.datetime.now().strftime("%r")})\n'
        )

        self.default_palette = self.app.palette()
        self.set_stylesheet(config.app_cfg.dark_mode)

        # I'm not sure Fira Mono is the right font for us...seems to mess up boxes.
        # So we're forcing the font_name configuration to be 'Fira Code' for now
        config.app_cfg.font_name = "Fira Code"

        # This approach will presumably alter every widget that is a child of this window
        self.setStyleSheet(
            'QWidget {font: "'
            + config.app_cfg.font_name
            + '"; font-size: '
            + str(config.app_cfg.font_size)
            + "pt}"
        )
        self.ui.plainTextEditOutput.setFont(
            QFont(config.app_cfg.font_name, int(config.app_cfg.font_size))
        )

        # setup some ui timers
        self.ui_timer.timeout.connect(self.update_ui_status)
        self.ui_timer.start(1000)

        self.show()

        # need to position views, but their geometry can't be properly computed until
        # after we show them
        for i, view in enumerate(self.visual_views.values()):
            view.show()
        # similarly, need to make this window is shown, so do the positioning after a 250ms
        # delay (long enough for show?)
        one_off_timer = QTimer()
        one_off_timer.singleShot(250, self.position_windows)

        if config.app_cfg.auto_load_last_device:
            # this gets run when user tries to change epiclib version
            config.app_cfg.auto_load_last_device = False
            two_off_timer = QTimer()
            two_off_timer.singleShot(500, partial(self.session_reload, quiet=True))

        if platform.system().lower() == "darwin":
            self.setMenuBar(self.ui.menubar)
            self.ui.menubar.setNativeMenuBar(False)

        Exists = Path(config.app_cfg.last_device_file).is_file()
        Device = (
            config.app_cfg.last_device_file
            if config.app_cfg.last_device_file
            else "None"
        )
        last_session_notice = f"Last Device Loaded: {Device} [{Exists=}]"
        self.write(dedent(last_session_notice))

    def mouseDoubleClickEvent(self, event: QMouseEvent = None):
        try:
            self.manage_z_order = False
            for win in chain(
                [self, self.trace_win, self.stats_win],
                self.visual_views.values(),
                self.auditory_views.values(),
            ):
                if win.isVisible():
                    #     or win.windowState() == Qt.WindowMinimized:
                    # win.setWindowState(Qt.WindowNoState)
                    # win.showNormal()
                    win.raise_()
        finally:
            self.manage_z_order = True

    def connect_menu_signals(self):
        self.ui.actionQuit.triggered.connect(self.close)
        self.ui.actionQuit.setShortcut("Ctrl+Q")
        self.ui.actionLoad_Device.triggered.connect(self.on_load_device)
        self.ui.actionLoad_Visual_Encoder.triggered.connect(
            partial(self.simulation.on_load_encoder, kind="Visual")
        )
        self.ui.actionLoad_Auditory_Encoder.triggered.connect(
            partial(self.simulation.on_load_encoder, kind="Auditory")
        )
        self.ui.actionUnload_Visual_Encoder.triggered.connect(
            partial(self.simulation.on_unload_encoder, kind="Visual")
        )
        self.ui.actionUnload_Auditory_Encoder.triggered.connect(
            partial(self.simulation.on_unload_encoder, kind="Auditory")
        )
        self.ui.actionLoad_Device.setShortcut("Ctrl+L")
        self.ui.actionCompile_Rules.triggered.connect(self.choose_rules)
        self.ui.actionCompile_Rules.setShortcut("Ctrl+K")
        self.ui.actionRecompile_Rules.triggered.connect(self.recompile_rules)
        self.ui.actionRecompile_Rules.setShortcut("Ctrl+Alt+K")
        self.ui.actionRun_Settings.triggered.connect(self.show_run_settings)
        self.ui.actionRunAll.triggered.connect(self.run_all)
        self.ui.actionRunAll.setShortcut("Ctrl+R")
        self.ui.actionRun_One_Step.triggered.connect(self.run_one_step)
        self.ui.actionRun_One_Step.setShortcut("Ctrl+O")
        self.ui.actionStop.triggered.connect(self.halt_simulation)
        self.ui.actionStop.setShortcut("Ctrl+.")
        self.ui.actionPause.triggered.connect(self.pause_simulation)
        self.ui.actionPause.setShortcut("Ctrl+Alt+P")
        self.ui.actionAbout.triggered.connect(self.about_dialog)
        self.ui.actionHelp.triggered.connect(self.open_help_file)
        self.ui.actionStandardRun.triggered.connect(
            partial(self.run_tests, kind="StandardRun")
        )
        self.ui.actionEncoderRun.triggered.connect(
            partial(self.run_tests, kind="EncoderRun")
        )
        self.ui.actionAllRuns.triggered.connect(partial(self.run_tests, kind="AllRuns"))
        self.ui.actionDisplay_Controls.triggered.connect(
            self.show_display_settings_dialogs
        )
        self.ui.actionTrace_Settings.triggered.connect(self.show_trace_settings_dialogs)
        self.ui.actionLogging.triggered.connect(self.show_log_settings_dialogs)
        self.ui.actionRule_Break_Settings.triggered.connect(
            self.show_rule_break_settings_dialog
        )
        self.ui.actionDevice_Options.triggered.connect(self.show_device_options_dialog)

        # NOTE: this is disabled until we have another pybind11-based version of EPIClib to offer
        self.ui.actionEPICLib_Settings.setEnabled(False)
        # self.ui.actionEPICLib_Settings.triggered.connect(
        #     self.show_epiclib_settings_dialog
        # )

        self.ui.actionSound_Text_Settings.triggered.connect(
            self.show_sound_text_settings_dialog
        )
        self.ui.actionExport_Normal_Output.triggered.connect(
            partial(
                self.export_output, source=self.ui.plainTextEditOutput, name="Normal"
            )
        )
        self.ui.actionExport_Trace_Output.triggered.connect(
            partial(
                self.export_output,
                source=self.trace_win.ui.plainTextEditOutput,
                name="Trace",
            )
        )
        self.ui.actionExport_Stats_Output.triggered.connect(
            partial(
                self.export_output,
                source=self.stats_win.ui.statsTextBrowser,
                name="Stats",
            )
        )
        self.ui.actionReset_Layout.triggered.connect(self.layout_reset)
        self.ui.actionReload_Session.triggered.connect(
            partial(self.session_reload, quiet=False)
        )
        self.ui.actionShow_Trace_Window.triggered.connect(
            partial(self.reveal_windows, window="trace")
        )
        self.ui.actionShow_Stats_Window.triggered.connect(
            partial(self.reveal_windows, window="stats")
        )
        self.ui.actionShow_Visual_Views.triggered.connect(
            partial(self.reveal_windows, window="visual")
        )
        self.ui.actionShow_Auditory_Views.triggered.connect(
            partial(self.reveal_windows, window="auditory")
        )
        self.ui.actionShow_All.triggered.connect(
            partial(self.reveal_windows, window="all")
        )
        self.ui.actionMinimize_All.triggered.connect(self.minimize_windows)
        self.ui.actionClear_Output_Windows.triggered.connect(self.clear_output_windows)
        self.ui.actionSet_Application_Font.triggered.connect(self.set_application_font)
        self.ui.actionDark_Mode_Toggle.triggered.connect(self.toggle_darkmode)
        self.ui.actionDark_Mode_Toggle.setChecked(config.app_cfg.dark_mode)
        self.ui.actionDelete_Datafile.triggered.connect(self.delete_datafile)

        self.ui.actionText_Editor.triggered.connect(self.choose_text_editor)
        if not config.app_cfg.text_editor:
            config.app_cfg.text_editor = "default"
        self.ui.actionText_Editor.setText(
            f"Text Editor: {config.app_cfg.text_editor.upper()}"
        )

        self.ui.actionRun_Simulation_Script.triggered.connect(
            self.simulation_from_script
        )

    def window_focus_changed(self, win: QMainWindow):
        if not win or not self.manage_z_order:
            return
        win_name = win.objectName()
        if win_name.startswith("menu"):
            return
        win_name = re.sub(r"(.+)Window", r"\1", win_name)

        if win_name in self.z_order:
            self.z_order[win_name] = time.time()

    # ==============================================================================
    # Delegates for methods of self.simulation. This is required because we may delete
    # and re-init self.simulation and we don't want various menu items to then point
    # to nothing.
    # ==============================================================================

    def on_load_device(
        self, file: str = "", quiet: bool = False, auto_load_rules: bool = True
    ) -> bool:
        self.layout_save()

        try:
            self.remove_views_from_model()
        except:  # broad on purpose!
            ...

        for target in (self, self.trace_win, self.stats_win):
            target.clear()

        self.simulation.on_load_device(file, quiet)

        # Model was reset, so we have to reconnect views and such
        if self.simulation and self.simulation.device and self.simulation.model:
            self.add_views_to_model()
            self.simulation.update_model_output_settings()
            self.update_output_logging()
            self.clear_ui(
                visual_views=True,
                auditory_views=True,
                normal_output=False,
                trace_output=True,
            )
            self.manage_z_order = False
            self.layout_load(y_adjust=26)
            self.manage_z_order = True

            if auto_load_rules and config.device_cfg.rule_files:
                self.simulation.choose_rules(config.device_cfg.rule_files)

            return True
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
        rule_name = Path(
            self.simulation.rule_files[self.simulation.current_rule_index].rule_file
        ).name
        self.write(emoji_box(f"RULE FILE: {rule_name}", line="thick"))

        if not self.simulation.rule_files[
            self.simulation.current_rule_index
        ].parameter_string:
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
            self.write(
                emoji_box(
                    f"ERROR: Unable to reload last session: No previous device found in settings.",
                    line="thick",
                )
            )

        if self.simulation and self.simulation.device:
            if config.device_cfg.rule_files:
                self.write(
                    f"{len(config.device_cfg.rule_files)} rule files recovered from "
                    f"previous device session: "
                )
                for i, rule_file in enumerate(config.device_cfg.rule_files):
                    p = Path(rule_file)
                    if p.is_file():
                        status = f"({e_boxed_check} Found)"
                    else:
                        status = f"({e_boxed_x} Missing)"
                    self.write(f"   {p.name} ({status})")
                config.device_cfg.rule_files = [
                    rule_file
                    for rule_file in config.device_cfg.rule_files
                    if Path(rule_file).is_file()
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
                self.write(
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

            # NOTE: Keep this here...I need more user feedback on this...I think it's disruptive to
            #       be asked in this when reinstating a session, right?
            #       ===============================================================================
            # if aud_encoder or vis_encoder:
            #     alle = config.device_cfg.auto_load_last_encoders
            #     if alle == "yes" or (
            #         alle == "ask"
            #         and QMessageBox.question(
            #             self,
            #             "Previous Perceptual Encoder(s) Found",
            #             "Load encoder(s) previously used with this device?",
            #             QMessageBox.Yes | QMessageBox.No,
            #         )
            #         == QMessageBox.Yes
            #     ):
            #         if vis_encoder:
            #             self.simulation.on_load_encoder(
            #                 kind="Visual",
            #                 file=config.device_cfg.visual_encoder,
            #                 quiet=False,
            #             )
            #
            #         if aud_encoder:
            #             self.simulation.on_load_encoder(
            #                 kind="Auditory",
            #                 file=config.device_cfg.auditory_encoder,
            #                 quiet=False,
            #             )
            #     else:
            #         config.device_cfg.visual_encoder = ""
            #         config.device_cfg.auditory_encoder = ""

    def simulation_from_script(self):
        if (
            hasattr(config.app_cfg, "last_script_file")
            and Path(config.app_cfg.last_script_file).is_file()
        ):
            start_dir = Path(config.app_cfg.last_script_file)
        elif Path(config.device_cfg.device_file).is_file():
            start_dir = Path(config.device_cfg.device_file).parent
        elif Path(config.app_cfg.last_device_file).is_file():
            start_dir = Path(config.app_cfg.last_device_file).parent
        else:
            start_dir = str(Path.home())

        fd_options = QFileDialog.Options()
        if platform.system() == "Linux":
            fd_options = fd_options | QFileDialog.Option.DontUseNativeDialog

        script_file, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption="Choose EPICpy Device File",
            directory=str(start_dir),
            filter="CSV Files (*.csv);;Text Files (*.txt)",
            initialFilter="CSV Files (*.csv)",
            options=fd_options,
        )

        if not script_file:
            self.write(f"{e_boxed_x} The run-script loading operation was cancelled.")
            return

        if Path(script_file).is_file():
            config.app_cfg.last_script_file = script_file

        try:
            commands = pd.read_csv(
                script_file,
                names=[
                    "device_file",
                    "rule_file",
                    "parameter_string",
                    "clear_data",
                    "reload_device",
                ],
                skip_blank_lines=True,
                comment="#",
                on_bad_lines="skip",
                dtype={
                    "device_file": str,
                    "rule_file": str,
                    "parameter_string": str,
                    "clear_data": bool,
                    "reload_device": bool,
                },
            )

            err_msg = (
                f"{e_heavy_x} Unable to construct proper command matrix from '{script_file}'.\n"
                f"Make sure each line contains device_file,rule_file,parameter_string,clear_data,reload_device "
                f"on each line separated by commas and without spaces between elements "
                f"(like a standard csv file)"
            )

            assert isinstance(commands, pd.DataFrame), err_msg

        except Exception as e:
            self.write(
                f'{e_boxed_x} Error loading script from file\n"{script_file}":\n{str(e)}.'
            )
            return

        # def shorten_paths(row):
        #     row.device_file = Path(row.device_file).name
        #     row.rule_file = Path(row.rule_file).name
        #     return row

        run_info = []

        for i, cmd in commands.iterrows():
            run_info.append(
                RunInfo(
                    from_script=True,
                    device_file=cmd.device_file.strip(),
                    rule_file=cmd.rule_file.strip(),
                    parameter_string=cmd.parameter_string.strip(),
                    clear_data=cmd.clear_data,
                    reload_device=cmd.reload_device,
                )
            )

        sf_title = f'\nRUNS LOADED FROM SCRIPT FILE "{Path(script_file).name}":'
        self.write(sf_title)
        self.write("-" * len(sf_title))
        self.write(" ")
        pretty = [
            RunInfo(
                ri.from_script,
                Path(ri.device_file).name if ri.device_file else ri.device_file,
                Path(ri.rule_file).name if ri.rule_file else ri.rule_file,
                ri.parameter_string,
                ri.clear_data,
                ri.reload_device,
            )
            for ri in run_info
        ]
        self.ui.plainTextEditOutput.write(pd.DataFrame(pretty).to_string(index=False))

        if self.on_load_device(
            run_info[0].device_file, auto_load_rules=False
        ) and self.choose_rules(run_info):
            if run_info[0].clear_data:
                self.delete_datafile()

            if run_info[0].parameter_string:
                self.simulation.device.set_parameter_string(
                    run_info[0].parameter_string
                )

            self.write(
                f"\n{e_boxed_check} Scripted Run Ready! Press Run|Run_All In The Menu To Start!\n"
            )
        else:
            self.write(
                f"\n{e_boxed_x} Scripted Run NOT SETUP PROPERLY! Attempting to run may fail.\n"
            )

    def remove_file_loggers(self):
        if self.normal_out_view.file_writer.enabled:
            self.normal_out_view.file_writer.close()
        if self.trace_win.trace_out_view.file_writer.enabled:
            self.trace_win.trace_out_view.file_writer.close()

    def update_output_logging(self):
        self.remove_file_loggers()

        if config.device_cfg.log_normal_out and config.device_cfg.normal_out_file:
            if self.normal_file_output_never_updated:
                p = Path(config.device_cfg.normal_out_file)
                p.unlink(missing_ok=True)
                self.normal_file_output_never_updated = False

            try:
                self.normal_out_view.file_writer.open(
                    Path(config.device_cfg.normal_out_file)
                )
                self.write(
                    f"{e_boxed_check} Normal Output logging set to "
                    f"{config.device_cfg.normal_out_file}"
                )
            except Exception as e:
                self.write(
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
                self.trace_win.trace_out_view.file_writer.open(
                    Path(config.device_cfg.trace_out_file)
                )
                self.write(
                    f"{e_boxed_check} Trace Output logging set to "
                    f"{config.device_cfg.trace_out_file}"
                )
            except Exception as e:
                self.write(
                    emoji_box(
                        f"ERROR: Unable to set Trace Output logging to\n"
                        f"{config.device_cfg.trace_out_file}:\n"
                        f"{e}",
                        line="thick",
                    )
                )

    def add_views_to_model(self):
        self.simulation.model.add_visual_physical_view(self.visual_physical_view)
        self.simulation.model.add_visual_sensory_view(self.visual_sensory_view)
        self.simulation.model.add_visual_perceptual_view(self.visual_perceptual_view)
        self.simulation.model.add_auditory_physical_view(self.auditory_physical_view)
        self.simulation.model.add_auditory_sensory_view(self.auditory_sensory_view)
        self.simulation.model.add_auditory_perceptual_view(
            self.auditory_perceptual_view
        )

    def remove_views_from_model(self):
        self.simulation.model.get_human_ptr().remove_visual_physical_view(
            self.visual_physical_view
        )
        self.simulation.model.get_human_ptr().remove_visual_sensory_view(
            self.visual_sensory_view
        )
        self.simulation.model.get_human_ptr().remove_visual_perceptual_view(
            self.visual_perceptual_view
        )
        self.simulation.model.get_human_ptr().remove_auditory_physical_view(
            self.auditory_physical_view
        )
        self.simulation.model.get_human_ptr().remove_auditory_sensory_view(
            self.auditory_sensory_view
        )
        self.simulation.model.get_human_ptr().remove_auditory_perceptual_view(
            self.auditory_perceptual_view
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
        self.visual_perceptual_view = EPICVisualView(
            self.visual_views["Visual Perceptual"]
        )

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
        self.auditory_physical_view = EPICAuditoryView(
            self.auditory_views["Auditory Physical"]
        )
        self.auditory_sensory_view = EPICAuditoryView(
            self.auditory_views["Auditory Sensory"]
        )
        self.auditory_perceptual_view = EPICAuditoryView(
            self.auditory_views["Auditory Perceptual"]
        )

        for win in (
            self.visual_physical_view,
            self.visual_sensory_view,
            self.visual_perceptual_view,
            self.auditory_physical_view,
            self.auditory_sensory_view,
            self.auditory_perceptual_view,
        ):
            win.set_changed()

        # when one window is minimized, everything gets minimized!
        for view in chain(self.visual_views.values(), self.auditory_views.values()):
            view.installEventFilter(self.state_watcher)

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
            self.statusBar().showMessage(
                f'Run State: {"UnReady" if self.run_state == UNREADY else "Runnable"}'
            )
            self.set_ui_not_running()

    def closeEvent(self, event: QCloseEvent):
        if self.closing:
            event.ignore()
            return

        try:
            self.editor_window.close()
        except:
            ...

        self.manage_z_order = False
        self.closing = True

        if self.run_state == RUNNING:
            self.halt_simulation()

        self.normal_out_view_thread.stop()
        self.trace_out_view_thread.stop()
        try:
            self.debug_out_view_thread.stop()
        except AttributeError:
            ...
        try:
            self.pps_out_view_thread.stop()
        except AttributeError:
            ...

        self.remove_file_loggers()

        _ = self.layout_save()

        self.trace_win.can_close = True
        self.trace_win.close()  # destroy()

        self.stats_win.can_close = True
        self.stats_win.close()  # destroy()

        for view in chain(self.visual_views.values(), self.auditory_views.values()):
            view.can_close = True
            view.close()  # destroy()

        self.close_output_files()

        try:
            self.remove_views_from_model()
        except:
            pass

        if self.simulation:
            self.simulation.pause_simulation()
            if self.simulation.model:
                self.simulation.model.stop()
            if self.simulation.device:
                self.simulation.device.stop_simulation()
            self.simulation.instance.shutdown_simulation()

        self.simulation.model = None
        self.simulation.device = None
        self.simulation.instance = None

        try:
            uninitialize_py_streamers()
        except Exception as e:
            log.error(f"got this error in the closeEvent: {e}")

        event.accept()

    def position_windows(self):
        try:
            self.manage_z_order = False
            self.update_title()

            self.ui.actionReload_Session.setEnabled(
                Path(config.device_cfg.device_file).is_file()
            )

            if not self.layout_load(y_adjust=26):
                self.layout_reset()
        finally:
            self.manage_z_order = True

    def set_view_background_image(
        self, view_type: str, img_filename: str, scaled: bool = True
    ):
        if not config.device_cfg.allow_device_images:
            return

        _view_type = view_type.lower()
        try:
            assert _view_type in (
                "visual",
                "auditory",
            ), "view_type must be in ('visual', 'auditory')"
            assert Path(
                img_filename
            ).is_file(), f"{img_filename} is not a valid image file"
            if _view_type == "visual":
                views = self.visual_views
            elif _view_type == "auditory":
                views = self.auditory_views
            else:
                raise ValueError(
                    f"set_view_background_image: Got bad view_type ({_view_type}), "
                    f"should be in (visual, auditory)"
                )

            for view in views.values():
                view.set_background_image(img_filename, scaled=scaled)
        except Exception as e:
            log.error(f"Unable to set view background image [{e}]")

    def enable_view_updates(self, enable: bool = True):
        for view in self.visual_views.values():
            view.allow_updates(enable)  # determines whether anything is actually done

        for view in self.auditory_views.values():
            view.allow_updates(enable)  # determines whether anything is actually done

        # NOTE: The above seems unnecessary if we're adding/removing views from model.
        #       On Linux the above is unnecessary, but on mac, somehow the time updates
        #       are getting through causing a massive slowdown just when user has asked
        #       for max speed. (March 2022 -- is this still the case?)

    def enable_text_updates(self, enable: bool = True):
        self.ui.plainTextEditOutput.cache_text = not enable
        self.trace_win.ui.plainTextEditOutput.cache_text = not enable

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
            self.clear()
        if trace_output:
            self.trace_win.clear()
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

    def write(self, text: str, copy_to_trace: bool = False):
        if text:
            self.ui.plainTextEditOutput.write(text)
            if copy_to_trace:
                self.trace_win.ui.plainTextEditOutput.write(text)

    def dump_cache(self):
        return self.ui.plainTextEditOutput.dump_cache()

    def clear(self):
        self.ui.plainTextEditOutput.clear()

    def set_ui_running(self):
        self.ui.actionStop.setEnabled(True)
        self.ui.actionPause.setEnabled(True)

        self.ui.actionRunAll.setEnabled(False)
        self.ui.actionRun_One_Step.setEnabled(False)

        self.ui.actionLoad_Device.setEnabled(False)
        self.ui.actionLoad_Visual_Encoder.setEnabled(False)
        self.ui.actionLoad_Auditory_Encoder.setEnabled(False)
        self.ui.actionUnload_Visual_Encoder.setEnabled(False)
        self.ui.actionUnload_Auditory_Encoder.setEnabled(False)
        self.ui.actionCompile_Rules.setEnabled(False)
        self.ui.actionRecompile_Rules.setEnabled(False)

        self.ui.actionRun_Settings.setEnabled(False)
        self.ui.actionRule_Break_Settings.setEnabled(False)
        self.ui.actionDevice_Options.setEnabled(False)
        self.ui.actionSound_Text_Settings.setEnabled(False)

        self.ui.actionDisplay_Controls.setEnabled(True)
        self.ui.actionTrace_Settings.setEnabled(True)

        self.ui.actionLogging.setEnabled(False)
        self.ui.actionExport_Normal_Output.setEnabled(False)
        self.ui.actionExport_Trace_Output.setEnabled(False)
        self.ui.actionExport_Stats_Output.setEnabled(False)
        self.ui.actionReload_Session.setEnabled(False)

        # self.ui.actionEPICLib_Settings.setEnabled(False)
        self.ui.actionDelete_Datafile.setEnabled(False)

        self.ui.actionRun_Simulation_Script.setEnabled(False)

    def set_ui_paused(self):
        has_rules = (
            True
            if self.simulation
            and self.simulation.model
            and self.simulation.model.get_prs_filename() != ""
            else False
        )
        has_device = (
            True if self.simulation and self.simulation.device is not None else False
        )

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

        self.ui.actionStop.setEnabled(True)
        self.ui.actionPause.setEnabled(False)

        self.ui.actionRunAll.setEnabled(True)
        self.ui.actionRun_One_Step.setEnabled(True)

        self.ui.actionLoad_Device.setEnabled(True)
        self.ui.actionCompile_Rules.setEnabled(True)
        self.ui.actionRecompile_Rules.setEnabled(has_rules)
        self.ui.actionLoad_Visual_Encoder.setEnabled(has_device)
        self.ui.actionLoad_Auditory_Encoder.setEnabled(has_device)
        self.ui.actionUnload_Visual_Encoder.setEnabled(has_visual_encoder)
        self.ui.actionUnload_Auditory_Encoder.setEnabled(has_auditory_encoder)

        self.ui.actionRun_Settings.setEnabled(has_device)
        self.ui.actionDevice_Options.setEnabled(has_device)
        self.ui.actionRule_Break_Settings.setEnabled(has_device and has_rules)
        self.ui.actionSound_Text_Settings.setEnabled(False)

        self.ui.actionDisplay_Controls.setEnabled(True)
        self.ui.actionTrace_Settings.setEnabled(True)
        self.ui.actionLogging.setEnabled(True)

        self.ui.actionExport_Normal_Output.setEnabled(True)
        self.ui.actionExport_Trace_Output.setEnabled(True)
        self.ui.actionExport_Stats_Output.setEnabled(True)
        self.ui.actionReload_Session.setEnabled(True)

        # self.ui.actionEPICLib_Settings.setEnabled(False)

        self.ui.actionDelete_Datafile.setEnabled(False)

        self.ui.actionRun_Simulation_Script.setEnabled(True)

    def set_ui_not_running(self):
        runnable = self.run_state == RUNNABLE
        has_rules = (
            True
            if self.simulation
            and self.simulation.model
            and self.simulation.model.get_prs_filename() != ""
            else False
        )
        has_device = (
            True if self.simulation and self.simulation.device is not None else False
        )

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

        self.ui.actionStop.setEnabled(False)
        self.ui.actionPause.setEnabled(False)

        self.ui.actionRunAll.setEnabled(runnable)
        self.ui.actionRun_One_Step.setEnabled(runnable)

        self.ui.actionLoad_Device.setEnabled(True)
        self.ui.actionCompile_Rules.setEnabled(True)
        self.ui.actionRecompile_Rules.setEnabled(has_rules)
        self.ui.actionLoad_Visual_Encoder.setEnabled(has_device)
        self.ui.actionLoad_Auditory_Encoder.setEnabled(has_device)
        self.ui.actionUnload_Visual_Encoder.setEnabled(has_visual_encoder)
        self.ui.actionUnload_Auditory_Encoder.setEnabled(has_auditory_encoder)

        self.ui.actionRun_Settings.setEnabled(has_device)
        self.ui.actionDevice_Options.setEnabled(has_device)
        self.ui.actionRule_Break_Settings.setEnabled(has_device and has_rules)
        self.ui.actionSound_Text_Settings.setEnabled(has_device)

        self.ui.actionDisplay_Controls.setEnabled(has_device)
        self.ui.actionTrace_Settings.setEnabled(has_device)
        self.ui.actionLogging.setEnabled(has_device)

        self.ui.actionExport_Normal_Output.setEnabled(has_device)
        self.ui.actionExport_Trace_Output.setEnabled(has_device)
        self.ui.actionExport_Stats_Output.setEnabled(has_device)
        self.ui.actionReload_Session.setEnabled(True)

        # self.ui.actionEPICLib_Settings.setEnabled(has_device)
        self.ui.actionDelete_Datafile.setEnabled(has_device)

        self.ui.actionRun_Simulation_Script.setEnabled(True)

    def update_title(self):
        if self.simulation and self.simulation.device and self.simulation.model:
            device_name = f"""DEVICE: {self.simulation.device.device_name}"""
        else:
            device_name = "DEVICE: None"
        rule_name = (
            f"RULES: "
            f"{Path(self.simulation.rule_files[self.simulation.current_rule_index].rule_file).name}"
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
        if self.simulation.visual_encoder and not isinstance(
            self.simulation.visual_encoder, NullVisualEncoder
        ):
            encoders.append("Visual")
        if self.simulation.auditory_encoder and not isinstance(
            self.simulation.auditory_encoder, NullAuditoryEncoder
        ):
            encoders.append("Auditory")
        if encoders:
            encoder_info = f'ENCODERS: [{", ".join(encoders)}]'
        else:
            encoder_info = f"ENCODERS: None"

        self.setWindowTitle(
            f"EPICpy v{__version__} | {device_name} | {rule_name} | {epiclib_version} "
            f"| {encoder_info}"
        )

    def show_run_settings(self):
        if not self.simulation or not self.simulation.device:
            self.write(f"{e_boxed_x} Unable to open run settings, load a device first.")
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
            self.simulation.default_device_parameters,
            delete_data_func,
            data_info_func,
        )
        self.run_settings_dialog.ui.pushButtonDeleteData.setEnabled(
            delete_data_func is not None
        )

        self.run_settings_dialog.ui.lineEditDeviceParameters.setText("")
        if config.device_cfg.device_params:
            self.run_settings_dialog.ui.lineEditDeviceParameters.setText(
                config.device_cfg.device_params
            )
            self.write(
                f'Device parameters "{config.device_cfg.device_params}" set from '
                f"previous device session."
            )
        else:
            device_params = self.simulation.device.get_parameter_string()
            self.run_settings_dialog.ui.lineEditDeviceParameters.setText(device_params)
            config.device_cfg.device_params = device_params

        self.run_settings_dialog.setup_options()

        self.run_settings_dialog.setModal(True)
        self.run_settings_dialog.exec()  # needed to make it modal?!

        # ----- Dialog Closed, deal with any changes

        if self.run_settings_dialog.ok:
            self.write(f"{e_info} Settings changes accepted.")
            config.device_cfg.device_params = (
                self.run_settings_dialog.ui.lineEditDeviceParameters.text()
            )
            self.simulation.device.set_parameter_string(config.device_cfg.device_params)
        else:
            self.write(f"{e_info} Settings changes ignored.")
            config.device_cfg.rollback()

    def show_display_settings_dialogs(self):
        if self.display_settings_dialog is None:
            self.display_settings_dialog = DisplayControlsWin()

        self.display_settings_dialog.setup_options()
        self.display_settings_dialog.setModal(True)
        self.display_settings_dialog.exec()  # needed to make it modal?!

        if self.display_settings_dialog.ok:
            self.write(f"{e_info} Display controls changes accepted.")
            if self.simulation and self.simulation.device and self.simulation.model:
                self.update_output_logging()
                self.simulation.update_model_output_settings()
        else:
            self.write(f"{e_info} Display controls changes ignored.")
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
            self.write(f"{e_info} Trace Settings changes accepted.")
            self.simulation.update_model_output_settings()
            self.update_output_logging()
        else:
            self.write(f"{e_info} Trace Settings changes ignored.")
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
            self.write(f"{e_info} Log Settings changes saved.")
            self.simulation.update_model_output_settings()
            self.update_output_logging()
        else:
            self.write(f"{e_info} Log Settings changes ignored.")
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

    def show_epiclib_settings_dialog(self):
        _ = QMessageBox(
            QMessageBox.Information,
            "This Function Has Been Disabled",
            "At the moment, the ability to switch EPIClib versions has been disabled. It is currently"
            "hard-coded to the version published in 2016 by David Kieras at https://github.com/dekieras/EPIC",
            # QMessageBox.Ok,
        )
        return

        old_epiclib = config.device_cfg.epiclib_version
        self.epiclib_settings_dialog = EPICLibSettingsWin(
            self.epiclib_files, self.epiclib_name
        )
        self.epiclib_settings_dialog.setup_options()
        self.epiclib_settings_dialog.setModal(True)
        self.epiclib_settings_dialog.exec()  # needed to make it modal?!

        new_epiclib = config.device_cfg.epiclib_version
        if new_epiclib != old_epiclib:
            # temporarily save new version in app config
            config.app_cfg.epiclib_version = new_epiclib
            config.app_cfg.auto_load_last_device = True

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
            self.write(
                f"{e_info} Application font size changed to {config.app_cfg.font_size} "
                f"pt). Note that some dialogs may only use new font size after "
                f"application restart."
            )
            for target in (self, self.trace_win, self.stats_win):
                target.setStyleSheet(
                    'QWidget {font: "'
                    + config.app_cfg.font_name
                    + '"; font-size: '
                    + str(config.app_cfg.font_size)
                    + "pt}"
                )
        else:
            self.write(f"{e_info} No changes made to application font size.")
            config.app_cfg.rollback()

    def choose_text_editor(self):
        if self.text_editor_dialog is not None:
            self.text_editor_dialog.close()
            self.text_editor_dialog = None
        self.text_editor_dialog = TextEditChoiceWin()
        self.text_editor_dialog.setup_options()
        self.text_editor_dialog.setModal(True)
        self.text_editor_dialog.exec()  # needed to make it modal?!

        if self.text_editor_dialog.ok:
            self.write(
                f'{e_info} EPICpy\'s text editor setting is set to "{config.app_cfg.text_editor.upper()}".'
            )
        else:
            self.write(
                f"{e_info} No changes made to application EPICpy's text editor setting."
            )
            config.device_cfg.rollback()

        self.ui.actionText_Editor.setText(
            f"Text Editor: {config.app_cfg.text_editor.upper()}"
        )

    def toggle_darkmode(self, dark_mode: bool):
        config.app_cfg.dark_mode = dark_mode

        self.set_stylesheet(config.app_cfg.dark_mode)
        self.set_stylesheet(config.app_cfg.dark_mode)



    def reveal_windows(self, window: str):
        try:
            self.manage_z_order = False
            if window == "trace" and self.trace_win:
                self.trace_win.setHidden(False)
                self.trace_win.raise_()
            if window == "stats" and self.trace_win:
                self.stats_win.setHidden(False)
                self.stats_win.raise_()
            elif window == "visual":
                for view in self.visual_views.values():
                    if view:
                        view.setHidden(False)
                        view.raise_()
            elif window == "auditory":
                for view in self.auditory_views.values():
                    if view:
                        view.setHidden(False)
                        view.raise_()
            elif window == "all":
                self.reveal_windows("trace")
                self.reveal_windows("visual")
                self.reveal_windows("auditory")
                self.reveal_windows("stats")

                if self.editor_window is not None:
                    try:
                        self.editor_window.setHidden(False)
                        self.editor_window.raise_()
                        self.editor_window.activateWindow()
                    except:
                        ...

            self.raise_()
        finally:
            self.manage_z_order = True

    def un_minimize_windows(self):
        try:
            self.manage_z_order = False
            for win in chain(
                [self, self.trace_win, self.stats_win],
                (self.visual_views.values()),
                self.auditory_views.values(),
            ):
                if not win.isVisible():
                    continue
                if win.windowState() & Qt.WindowState.WindowNoState:
                    pass
                else:
                    win.setWindowState(Qt.WindowState.WindowActive)

        finally:
            self.manage_z_order = True

    def minimize_windows(self):
        try:
            self.manage_z_order = False
            for win in chain(
                [self, self.trace_win, self.stats_win],
                self.visual_views.values(),
                self.auditory_views.values(),
            ):
                if not win.isVisible():
                    continue
                if win.windowState() & Qt.WindowState.WindowMinimized:
                    pass
                else:
                    win.showMinimized()
        finally:
            self.manage_z_order = True

    def clear_output_windows(self):
        self.ui.plainTextEditOutput.clear()
        if self.trace_win:
            self.trace_win.ui.plainTextEditOutput.clear()
        if self.stats_win:
            self.stats_win.ui.statsTextBrowser.clear()

    def about_dialog(self):
        about_window = AboutWin(self)
        about_window.show()

    def run_tests(self, kind: str):
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

    def open_help_file(self):
        url = "https://travisseymour.github.io/EPICpyDocs/"
        if webbrowser.open(url):
            self.write(f"Opened {url} in default web browser.")
        else:
            self.write(f"Error opening {url} in default web browser.")

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
        else:
            start_file = ""

        if not start_file:
            if Path(config.device_cfg.device_file).parent.is_dir():
                start_dir = Path(config.device_cfg.device_file).parent
            else:
                start_dir = Path().home().expanduser()
            start_file = f"{start_dir.stem}_{kind}_output.txt"
            start_file = str(Path(start_dir, start_file).with_suffix(ext).resolve())

        if kind == "Stats":
            _filter = (
                "HTML-Files (*.html);;Text files (*.txt);;"
                "Markdown files (*.md);;ODF files (*.odt);;All Files (*)"
            )
            initial_filter = "HTML-Files (*.html)"
        else:
            _filter = (
                "Text files (*.txt);;HTML-Files (*.html);;"
                "Markdown files (*.md);;ODF files (*.odt);;All Files (*)"
            )
            initial_filter = "Text files (*.txt)"

        fd_options = QFileDialog.Options()
        if platform.system() == "Linux" and kind == "Stats":
            # if we don't do this on linux, initial filename won't have correct extension!
            # it's pretty ugly!
            fd_options = fd_options | QFileDialog.Option.DontUseNativeDialog
        file, _ = QFileDialog.getSaveFileName(
            None,
            caption=f"Specify {kind} Output File",
            directory=str(start_file),
            filter=_filter,
            initialFilter=initial_filter,
            options=fd_options,
        )

        return file

    def export_output(self, source: QPlainTextEdit, name: str):
        default_exts = {"Normal": ".txt", "Trace": ".txt", "Stats": ".html"}
        try:
            ext = default_exts[name]
        except NameError:
            ext = ".txt"

        out_file = self.choose_log_file(name, ext)
        if not out_file:
            self.write(f"{e_info} {name.title()} window text export abandoned.")
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
            self.write(
                f"{e_boxed_check} {name.title()} Output window text written to {out_file}"
            )
        else:
            self.write(
                emoji_box(
                    f"ERROR: Unable to write output text from "
                    f"{name.title()} "
                    f"to"
                    f"{out_file})",
                    line="thick",
                )
            )

    def delete_datafile(self):
        if self.simulation.device and self.simulation.model:
            if hasattr(self.simulation.device, "delete_data_file"):
                self.simulation.device.delete_data_file()

    # ============================================
    # Dark Mode Theme Switching
    # ============================================

    def set_stylesheet(self, dark_mode):
        self.app.setStyle("Fusion")

        if dark_mode:
            self.app.setPalette(DarkPalette())
        else:
            self.app.setPalette(QPalette())


    # =============================================
    # Layout Save/Restore
    # =============================================

    def layout_save(self) -> bool:
        self.manage_z_order = False

        # figure out which config subsection to use
        if self.simulation.device and self.simulation.device.device_name:
            section = "".join(
                [c for c in self.simulation.device.device_name if c.isalpha()]
            ).title()
        else:
            section = "NoDevice"

        # save window states
        for win in chain(
            [self, self.trace_win, self.stats_win],
            self.visual_views.values(),
            self.auditory_views.values(),
        ):
            obj_name = win.objectName().replace(" ", "")

            self.window_settings.setValue(f"{section}/{obj_name}/Size", win.size())
            self.window_settings.setValue(f"{section}/{obj_name}/Pos", win.pos())
            self.window_settings.setValue(
                f"{section}/{obj_name}/Visible", win.isVisible()
            )
            self.window_settings.setValue(
                f"{section}/{obj_name}/ZOrder", self.z_order[win.objectName()]
            )

        self.manage_z_order = True

        self.window_settings.sync()

        return True

    def layout_load(self, y_adjust: int = 0) -> bool:
        # figure out which config subsection to use
        if self.simulation.device and self.simulation.device.device_name:
            section = "".join(
                [c for c in self.simulation.device.device_name if c.isalpha()]
            ).title()
        else:
            section = "NoDevice"

        # if that section works, great, otherwise just use default
        try:
            _ = self.window_settings.value(f"{section}/MainWindow/Pos")
            _ = self.window_settings.value(f"{section}/MainWindow/Size")
        except Exception as e:
            log.warning(
                f"Failed to locate existing window layout for NoDevice state ({e}), "
                f"loading default layout instead..."
            )
            self.layout_reset()

        try:
            # reposition/size windows according to saved values
            for win in chain(
                [self, self.trace_win, self.stats_win],
                self.visual_views.values(),
                self.auditory_views.values(),
            ):
                obj_name = win.objectName().replace(" ", "")

                win.resize(self.window_settings.value(f"{section}/{obj_name}/Size"))
                win.move(self.window_settings.value(f"{section}/{obj_name}/Pos"))
                try:
                    # not every config will have this new z scheme
                    z_order = self.window_settings.value(
                        f"{section}/{obj_name}/ZOrder", type=float
                    )
                    self.z_order[win.objectName()] = z_order
                except Exception as e:
                    log.warning(f"Unable to find window Z value for {obj_name}: {e}")

                visible = self.window_settings.value(
                    f"{section}/{obj_name}/Visible", type=bool
                )
                if win.objectName() != "MainWindow":
                    if visible:
                        win.show()
                    else:
                        win.hide()

            result = True
        except Exception as e:
            if "NoneType" not in str(e):
                log.warning(f"Unable to restore window geometry: {e}")
            else:
                log.warning(f"Unable to restore window geometry.")
            result = False
            return result  # go ahead and fail now, no point in bothering with z-order

        try:
            # restore z-order
            sorted_windows = dict(sorted(self.z_order.items(), key=lambda x: x[1]))

            topLevelWindows = QApplication.topLevelWindows()
            for objName, Z in sorted_windows.items():
                if not Z:
                    # if Z is 0.0, then it was never focused -- nothing to do
                    continue
                for win in topLevelWindows:
                    win_name = win.objectName()
                    win_name = re.sub(r"(.+)Window", r"\1", win_name)
                    if win_name == objName:
                        win.raise_()

            result = True

        except Exception as e:
            log.warning(f"Unable to restore window Z arrangement: {e}")
            result = True  # just Z, not the end of the world...so no fail

        return result

    def layout_reset(self):
        # - Figure out the available screen geometry and starting point

        screen_info = QGuiApplication.primaryScreen().availableGeometry()

        sx, sy, sw, sh = (
            screen_info.x(),
            screen_info.y(),
            screen_info.width(),
            screen_info.height(),
        )

        title_height = self.heightMM() // 2

        # wide
        if sw >= 390 * 3 + 638:
            w_mode = "Physical Sensory Perceptual Stats"
        elif sw >= 390 * 3:
            w_mode = "Physical Sensory Perceptual"
        elif sw >= 390 * 2 + 638:
            w_mode = "Physical Sensory Stats"
        elif sw >= 390 + 638:
            w_mode = "Physical Stats"
        else:  # 390
            w_mode = "Physical"

        # tall
        if sh >= 338 * 2 + 382:
            h_mode = "Visual Auditory Main_Tall"
        elif sh >= 338 * 2 + 250:
            h_mode = "Visual Auditory Main_Short"
        elif sh >= 338 + 382:
            h_mode = "Visual Main_Tall"
        elif sh >= 338 + 250:
            h_mode = "Visual Main_Short"
        elif sh >= 382:
            h_mode = "Main_Tall"
        else:  # 250
            h_mode = "Main_Short"

        if "Visual" in h_mode:
            for i, kind in enumerate(["Physical", "Sensory", "Perceptual"]):
                if kind in w_mode:
                    self.visual_views[f"Visual {kind}"].move(QPoint(391 * i, 0))
                    self.visual_views[f"Visual {kind}"].show()
                else:
                    self.visual_views[f"Visual {kind}"].hide()

        if "Auditory" in h_mode:
            for i, kind in enumerate(["Physical", "Sensory", "Perceptual"]):
                if kind in w_mode:
                    if platform.system() == "Windows":
                        self.auditory_views[f"Auditory {kind}"].move(
                            QPoint(391 * i, 338)
                        )
                    else:
                        self.auditory_views[f"Auditory {kind}"].move(
                            QPoint(391 * i, 338 + (title_height // 2))
                        )
                    self.auditory_views[f"Auditory {kind}"].show()
                else:
                    self.auditory_views[f"Auditory {kind}"].hide()

        w_mode_set = set(w_mode.split(" "))
        h_mode_set = set(h_mode.split(" "))
        cols = len({"Physical", "Sensory", "Perceptual"} & w_mode_set)
        rows = len({"Visual", "Auditory"} & h_mode_set)

        if platform.system() == "Windows":
            self.move(QPoint(0, rows * 338))
        else:
            self.move(QPoint(0, rows * 338 + title_height // 2 + 1))
        self.resize(QSize(cols * 390 + 1, 382 if "Main_Tall" in h_mode else 250))
        self.show()

        if "Stats" in w_mode:
            self.stats_win.move(QPoint(cols * 390 + cols, 0))
            self.stats_win.resize(QSize(638, rows * 338 + self.height() + rows))
            self.stats_win.show()
        else:
            self.stats_win.hide()

    # =============================================
    # Context Menu Behavior
    # =============================================

    def search_context_menu(self, event):
        contextMenu = QMenu(self)
        device_file = config.device_cfg.device_file
        rules_file = (
            config.device_cfg.rule_files[0] if config.device_cfg.rule_files else ""
        )

        if self.run_state == RUNNING:
            stopAction = contextMenu.addAction("Stop")
            searchQuit = contextMenu.addAction("Quit")
            clearAction = None
            searchAction = None
            selectAllAction = None
            copyAction = None
            EditNormalOutAction = None
            EditRulesAction = contextMenu.addAction("Edit Rule File")
            EditDataAction = None
            OpenDeviceFolder = None
        else:
            stopAction = None

            searchAction = contextMenu.addAction("Search")
            selectAllAction = contextMenu.addAction("Select All")

            contextMenu.addSeparator()
            if self.ui.plainTextEditOutput.copyAvailable and len(
                self.ui.plainTextEditOutput.toPlainText()
            ):
                copyAction = contextMenu.addAction("Copy")
            else:
                copyAction = None
            clearAction = contextMenu.addAction("Clear")

            contextMenu.addSeparator()

            EditNormalOutAction = (
                contextMenu.addAction("Open Normal Output In Text Editor")
                if self.run_state != RUNNING
                else None
            )

            EditRulesAction = (
                (contextMenu.addAction("Edit Production Rule File"))
                if (self.run_state != RUNNING and Path(rules_file).is_file())
                else None
            )

            EditDataAction = (
                (contextMenu.addAction("Edit Data Output File"))
                if self.run_state and self.run_state != RUNNING
                else None
            )

            if Path(device_file).is_file() and self.run_state != RUNNING:
                contextMenu.addSeparator()
                OpenDeviceFolder = contextMenu.addAction("Open Device Folder")
            else:
                OpenDeviceFolder = None

            contextMenu.addSeparator()
            searchQuit = contextMenu.addAction("Quit")

        action = contextMenu.exec(self.mapToGlobal(event))

        if action is None:
            ...
        elif action == clearAction:
            self.clear()
        elif action == searchAction:
            self.query_search()
        elif action == searchQuit:
            self.close()
        elif action == stopAction:
            self.halt_simulation()
        elif action == selectAllAction:
            self.ui.plainTextEditOutput.selectAll()
        elif action == copyAction:
            self.ui.plainTextEditOutput.copy()
        elif action == EditNormalOutAction:
            self.launchEditor(which_file="NormalOut")
        elif action == EditRulesAction:
            self.launchEditor(which_file="RuleFile")
        elif action == EditDataAction:
            self.launchEditor(which_file="DataFile")
        elif action == OpenDeviceFolder:
            OS = platform.system()
            if OS == "Linux":
                open_cmd = "xdg-open"
            elif OS == "Darwin":
                open_cmd = "open"
            elif OS == "Windows":
                open_cmd = "start"
            else:
                open_cmd = ""
                err_msg = f"ERROR: Opening device folder when OS=='{OS}' is not yet implemented!"
                self.write(emoji_box(err_msg, line="thick"))

            if open_cmd:
                subprocess.run([open_cmd, str(Path(device_file).resolve().parent)])

    def query_search(self):
        self.search_dialog.ok = False
        self.search_dialog.ui.checkBoxRegEx.setChecked(self.search_using_regex)
        self.search_dialog.ui.checkBoxIgnoreCase.setChecked(self.search_ignore_case)
        self.search_dialog.exec()

        if self.search_dialog.ok:
            self.search_pattern = (
                self.search_dialog.ui.lineEditSearchText.text().strip()
            )
            self.search_using_regex = self.search_dialog.ui.checkBoxRegEx.isChecked()
            self.search_ignore_case = (
                self.search_dialog.ui.checkBoxIgnoreCase.isChecked()
            )
            self.search_active = True
            self.do_search(backwards=self.search_dialog.backwards)

    # start text cursor utility functions --------
    def get_text_cursor(self):
        return self.ui.plainTextEditOutput.textCursor()

    def set_text_cursor_pos(self, value):
        tc = self.get_text_cursor()
        tc.setPosition(value, QTextCursor.MoveMode.KeepAnchor)
        self.ui.plainTextEditOutput.setTextCursor(tc)

    def get_text_cursor_pos(self):
        return self.get_text_cursor().position()

    def get_text_selection(self):
        cursor = self.get_text_cursor()
        return cursor.selectionStart(), cursor.selectionEnd()

    def set_text_selection(self, start, end):
        cursor = self.get_text_cursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.ui.plainTextEditOutput.setTextCursor(cursor)

    # ---------------- end text cursor utility functions

    def do_search(self, backwards: bool = False):
        if not self.search_pattern:
            return

        sensitivity = (
            Qt.CaseSensitivity.CaseInsensitive
            if self.search_ignore_case
            else Qt.CaseSensitivity.CaseSensitive
        )
        pattern = (
            self.search_pattern
            if self.search_using_regex
            else re.escape(self.search_pattern)
        )

        regex = QRegularExpression(pattern, sensitivity)

        text_cursor = self.get_text_cursor()

        if backwards:
            if text_cursor.atStart():
                self.ui.plainTextEditOutput.moveCursor(QTextCursor.MoveOperation.End)
            result = self.ui.plainTextEditOutput.find(
                regex, QTextDocument.FindFlag.FindBackward
            )
        else:
            if text_cursor.atEnd():
                self.ui.plainTextEditOutput.moveCursor(QTextCursor.MoveOperation.Start)
            result = self.ui.plainTextEditOutput.find(regex)

        if result:
            self.ui.plainTextEditOutput.setFocus()
        # else:
        #     pos = self.get_text_cursor_pos()
        #     self.set_text_selection(pos, pos)

    def launchEditor(self, which_file: str = "NormalOut"):
        if which_file == "NormalOut":
            file_id = datetime.datetime.now().strftime("%m%d%y_%H%M%S")
            file_path = Path(
                self.tmp_folder.name, f"TEMP_EPICPY_NORMALOUT_{file_id}.txt"
            )
            file_path.write_text(self.ui.plainTextEditOutput.toPlainText())
        elif which_file == "RuleFile":
            if self.simulation.rule_files:
                if self.simulation.current_rule_index < len(self.simulation.rule_files):
                    file_path = Path(
                        self.simulation.rule_files[
                            self.simulation.current_rule_index
                        ].rule_file
                    )
                else:
                    file_path = Path(
                        self.simulation.rule_files[
                            self.simulation.current_rule_index - 1
                        ].rule_file
                    )
            else:
                file_path = None
                self.write(
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
                    f"{e_boxed_x} ERROR: Device instance does not appear have "
                    f"expected data_filepath attribute."
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
                self.write(emoji_box(err_msg, line="thick"))
        else:
            file_path = None

        if file_path is not None:
            editor_path = config.app_cfg.text_editor.lower()
            try:
                if editor_path == "built-in":
                    # If there is no current editor, create one
                    if (
                        (self.editor_window is None)
                        or (not hasattr(self.editor_window, "isVisible"))
                        or (not self.editor_window.isVisible())
                    ):
                        try:
                            self.editor_window.close()
                        except AttributeError:
                            ...
                        self.editor_window = None
                        self.editor_window = MainEditorWindow()
                        # FIXME: vvv this should open to current device folder if possible

                        if (
                            self.simulation
                            and self.simulation.device
                            and Path(config.device_cfg.device_file).is_file()
                        ):
                            self.editor_window.set_folder(
                                Path(config.device_cfg.device_file).parent
                            )
                        else:
                            # if all else fails, set wd to file parent
                            self.editor_window.set_folder(
                                file_path if file_path.is_dir() else file_path.parent
                            )

                    # In case editor was open prior to opening a device, make sure editor path is set to device path
                    if (
                        self.simulation
                        and self.simulation.device
                        and Path(self.editor_window.model.rootPath())
                        != Path(config.device_cfg.device_file).parent
                    ):
                        self.editor_window.set_folder(
                            Path(config.device_cfg.device_file).parent
                        )

                    # Time to actually open the file
                    if file_path.is_file():
                        self.editor_window.open_file(file_path)
                    self.editor_window.show()
                    self.editor_window.activateWindow()

                else:
                    # user has specified the system default editor
                    OS = platform.system()
                    if OS == "Linux":
                        open_cmd = "xdg-open"
                    elif OS == "Darwin":
                        open_cmd = "open"
                    elif OS == "Windows":
                        open_cmd = "start"
                    else:
                        open_cmd = ""
                        err_msg = (
                            f"ERROR: EPICpy can only open system default editor on\n"
                            f"Linux, Darwin, and Windows based operating systems.\n"
                            f"It does not currently support your operating system type ({OS})."
                        )
                        self.write(emoji_box(err_msg, line="thick"))
                    if open_cmd:
                        subprocess.run([open_cmd, str(file_path.resolve())])
            except Exception as e:
                self.write(
                    emoji_box(
                        f"ERROR: Unable to open {which_file} file\n"
                        f"{file_path.name} in {'internal' if not editor_path else 'external'} text editor\n"
                        f"({'BUILT-IN [EPICcoder]' if not editor_path else str(editor_path)}):\n"
                        f"{e}",
                        line="thick",
                    )
                )

    # =============================================
    # Keyboard Button Handler
    # =============================================

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_F3:
            if modifiers == Qt.KeyboardModifier.ShiftModifier:
                self.do_search()
            else:
                partial(self.do_search, backwards=True)

    # =============================================
    # Device Helpers
    # =============================================

    @property
    def trace_device(self) -> bool:
        return config.device_cfg.trace_device
