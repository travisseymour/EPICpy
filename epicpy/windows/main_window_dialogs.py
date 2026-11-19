# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Mixin class providing settings dialog functionality for MainWin.
"""

from typing import TYPE_CHECKING

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from epicpy.constants.emoji import e_info
from epicpy.dialogs.break_settings_window import BreakSettingsWin
from epicpy.dialogs.device_settings_window import DeviceOptionsWin
from epicpy.dialogs.display_controls_window import DisplayControlsWin
from epicpy.dialogs.font_size_window import FontSizeDialog
from epicpy.dialogs.logging_window import LoggingSettingsWin
from epicpy.dialogs.run_settings_window import RunSettingsWin
from epicpy.dialogs.snd_text_settings_window import SoundTextSettingsWin
from epicpy.dialogs.trace_settings_window import TraceSettingsWin
from epicpy.utils import config
from epicpy.utils.app_utils import clear_font, hcolor
from epiclibcpp.epiclib.output_tee_globals import Info_out

if TYPE_CHECKING:
    from epicpy.windows.main_window import MainWin


class DialogsMixin:
    """
    Mixin for MainWin providing settings dialog functionality.

    Includes methods for:
    - Showing various settings dialogs (run, display, trace, logging, etc.)
    - Application font configuration
    - Toggle settings (parallel runs, overwrite data)
    """

    # Type hints for attributes that exist on MainWin
    if TYPE_CHECKING:
        self: "MainWin"

    def toggle_allow_parallel_runs(self, checked: bool):
        """Toggle the allow_parallel_runs setting."""
        config.device_cfg.allow_parallel_runs = checked

    def toggle_overwrite_data(self, checked: bool):
        """Toggle the overwrite_data setting."""
        config.device_cfg.overwrite_data = checked

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
        if hasattr(self, "log_settings_dialog"):
            self.log_settings_dialog.close()

        self.log_settings_dialog = LoggingSettingsWin()
        self.log_settings_dialog.setup_options()
        self.log_settings_dialog.setModal(True)
        self.log_settings_dialog.exec()

        if self.log_settings_dialog.ok:
            Info_out("Log Settings changes saved.\n")
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
