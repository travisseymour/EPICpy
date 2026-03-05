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

import importlib
import sys
import timeit
import warnings
from pathlib import Path
from typing import List, Optional

from epicpydevicelib.epicpy_device_base import EpicPyDevice
from qtpy.QtCore import (
    QObject,
    QTimer,
)
from qtpy.QtWidgets import QFileDialog

from epicpy.constants.emoji import (
    e_bangbang,
    e_boxed_check,
    e_boxed_ok,
    e_boxed_x,
    e_info,
)
from epicpy.constants.state_constants import PAUSED, RUNNABLE, RUNNING, UNREADY
from epicpy.dialogs.logging_window import LoggingSettingsWin
from epicpy.epic.encoder_passthru import NullAuditoryEncoder, NullVisualEncoder
from epicpy.epic.epicpy_exception import EPICpyException
from epicpy.epic.run_info import RunInfo
from epicpy.utils import config
from epicpy.utils.app_utils import rich_traceback_str, unpack_param_string
from epicpy.utils.module_reloader import make_device, unload_directory_modules, unload_module
from epicpy.utils.syspath_manage import (
    clear_active_plugin_path,
    get_active_plugin_path,
    set_active_plugin_path,
)
from epicpy.views.epicpy_visual_view import EPICVisualView

warnings.filterwarnings("ignore", module=r"^matplotlib")
warnings.filterwarnings("ignore", module=r"^pingouin")
warnings.filterwarnings("ignore", module=r"^pandas")
warnings.filterwarnings("ignore", module=r"^numpy")


from epiclibcpp.epiclib import Coordinator, Model, set_auditory_encoder_ptr, set_visual_encoder_ptr
from epiclibcpp.epiclib.output_tee_globals import Exception_out, Info_out, Normal_out, Trace_out
from epicpydevicelib.epicpy_auditory_encoder_base import EPICPyAuditoryEncoder
from epicpydevicelib.epicpy_visual_encoder_base import EPICPyVisualEncoder

try:
    from epiclibcpp.epiclib import describe_parameters_u

    desc_param_loaded = True
except Exception as e:

    def describe_parameters_u(*args, **kwargs):
        pass

    desc_param_loaded = False
    Exception_out(f'WARNING: Failed to load "describe_parameters_u" from epiclib. Will not be able to dump parameters. ({e})\n')


class Simulation(QObject):
    def __init__(self, main_win):
        super().__init__(None)
        self.main_win = main_win

        self.device: EpicPyDevice
        self._device_modname: str
        self.model: Model
        self.visual_encoder: EPICPyVisualEncoder
        self.auditory_encoder = EPICPyAuditoryEncoder

        self.instance: Coordinator = Coordinator.get_instance()
        self.stop_model_now: bool = False
        self.user_stopped: bool = False

        self.keep_checking_run: bool = False
        self.run_start_time: float = 0
        self.run_time: int = 0
        self.run_time_limit: int = 0
        self.run_timer: QTimer = QTimer()
        self.rule_files: List[RunInfo] = []
        self.last_run_mode: str = ""
        self.current_rule_index: int = 0
        self.last_update_time: float = timeit.default_timer()
        self.default_device_parameters: str = ""

        self.steps_since_last_text_out: int = 0
        self.steps_since_last_display: int = 0
        self.steps_run: int = 0

        self.raw_device_param_string: str = ""
        self.param_set: list = []

        self.device_path_additions: list = []
        self.visual_encoder_path_additions: list = []
        self.auditory_encoder_path_additions: list = []

    def has_coordinator(self) -> bool:
        return hasattr(self, "Coordinator") and isinstance(self.instance, Coordinator)

    def has_model(self) -> bool:
        return hasattr(self, "model") and isinstance(self.model, Model)

    def has_device(self) -> bool:
        return hasattr(self, "device") and isinstance(self.device, EpicPyDevice)

    def has_visual_encoder(self) -> bool:
        return (
            hasattr(self, "visual_encoder")
            and isinstance(self.visual_encoder, EPICPyVisualEncoder)
            and not hasattr(self.visual_encoder, "is_null_encoder")
        )

    def has_auditory_encoder(self) -> bool:
        return (
            hasattr(self, "auditory_encoder")
            and isinstance(self.auditory_encoder, EPICPyAuditoryEncoder)
            and not hasattr(self.auditory_encoder, "is_null_encoder")
        )

    def call_for_display_refresh(self):
        current_time = self.instance.get_time()
        if config.device_cfg.display_refresh == "after_each_step":
            step_interval = int(config.device_cfg.display_refresh_value)
            self.steps_since_last_display += 1
            if self.steps_since_last_display >= step_interval:
                self.main_win.force_view_display(current_time)
                self.steps_since_last_display = 0
        elif config.device_cfg.display_refresh == "continuously":
            self.main_win.update_views(current_time)
        elif config.device_cfg.display_refresh == "after_every_sec":
            current_timeit = timeit.default_timer()
            if current_timeit - self.last_update_time >= float(config.device_cfg.display_refresh_value):
                self.main_win.force_view_display(current_time)
                self.last_update_time = current_timeit

        # ** if 'none_during_run' then this function does nothing

    def update_model_output_settings(self):
        # set some output and tracing options
        try:
            self.model.set_output_run_messages(config.device_cfg.output_run_messages)
            self.model.set_output_run_memory_contents(config.device_cfg.output_run_memory_contents)
            self.model.set_output_run_details(config.device_cfg.output_run_details)
            self.model.set_output_compiler_messages(config.device_cfg.output_compiler_messages)
            self.model.set_output_compiler_details(config.device_cfg.output_compiler_details)

            self.model.set_trace_manual(config.device_cfg.trace_manual)
            self.model.set_trace_cognitive(config.device_cfg.trace_cognitive)
            self.model.set_trace_visual(config.device_cfg.trace_visual)
            self.model.set_trace_auditory(config.device_cfg.trace_auditory)
            self.model.set_trace_ocular(config.device_cfg.trace_ocular)
            self.model.set_trace_vocal(config.device_cfg.trace_vocal)
            self.model.set_trace_temporal(config.device_cfg.trace_temporal)
            self.model.set_trace_device(config.device_cfg.trace_device)
        except Exception as e:
            Info_out(f"\n❌ ERROR: Failed to update EPIC output or trace settings:\n{e}\n")

    def on_load_device(self, device_file: str = "", quiet: bool = False):
        # load config for this device, or create new device on if none exists already
        dark_mode = config.app_cfg.dark_mode
        current = config.device_cfg.current

        config.get_device_config(Path(device_file))
        config.device_cfg.device_file = device_file

        # Force text refresh to none_during_run (continuously is disabled)
        if config.device_cfg.text_refresh != "none_during_run":
            config.device_cfg.text_refresh = "none_during_run"

        config.app_cfg.dark_mode = dark_mode
        config.device_cfg.current = current

        # save global app config in case we need last_device_file
        config.app_cfg.last_device_file = device_file

        if not config.device_cfg.normal_out_file:
            logfile = LoggingSettingsWin.default_log_filename("normal")
            config.device_cfg.normal_out_file = logfile if logfile else ""
        if not config.device_cfg.trace_out_file:
            logfile = LoggingSettingsWin.default_log_filename("trace")
            config.device_cfg.trace_out_file = logfile if logfile else ""
        if not config.device_cfg.stats_out_file:
            logfile = LoggingSettingsWin.default_log_filename("stats")
            config.device_cfg.stats_out_file = logfile if logfile else ""

        if self.has_device():
            # make sure device data output gets flushed and saved no matter how
            # device object is deleted, includes normal exit/quit as well as
            # exceptions! Because the target method, or even the data file handle
            # are not part of EpicPyDevice, we have to condition this feature on
            # whether the expected attributes are present.
            if hasattr(self.device, "finalize_data_output"):
                self.device.finalize_data_output()
            elif hasattr(self.device, "data_file"):
                self.device.data_file.close()
            else:
                # data file will not be guaranteed to automatically closed in every
                # case. However, on normal exit (an often on abnormal ones), Python
                # is pretty good about open file handles. I'm just not sure if
                # *all* available data will be preserved.
                self.device = None  # type: ignore[assignment]

        self.current_rule_index = 0
        self.device = None  # type: ignore[assignment]

        # Reset the Coordinator to clear all old processors before creating new device/model.
        # This ensures clean state even if Python's GC hasn't collected old objects yet.
        self.instance.reset()

        if getattr(self, "_device_modname", ""):
            # Clear device-local modules (graph_maker, etc.) before unloading.
            # We get the directory from the loaded module itself, since
            # config.device_cfg has already been updated to the NEW device.
            old_mod = sys.modules.get(self._device_modname)
            if old_mod and getattr(old_mod, "__file__", None):
                unload_directory_modules(Path(old_mod.__file__).parent)
            unload_module(self._device_modname)
            self._device_modname = ""
            if get_active_plugin_path():
                clear_active_plugin_path()

        device_file_p = Path(device_file)

        set_active_plugin_path(str(device_file_p.parent))

        try:
            if not quiet:
                Info_out(f"\n{e_info} loading device code from {device_file_p.name}...\n")

            device, modname = make_device(
                Path(device_file),
                ot=Normal_out,
                device_folder=device_file_p.parent,
            )
            self.device = device
            self._device_modname = modname

            if not quiet:
                Info_out(f"\n{e_info} found EpicDevice class, created new device instance based on this class.\n")
            Info_out(f"\n{e_boxed_check} {self.device.device_name} device was created successfully.\n")

            # must store default device params before we reload one from settings
            if hasattr(self.device, "condition_string"):
                self.default_device_parameters = str(self.device.condition_string)
            else:
                self.default_device_parameters = ""

            # restore layout for device
            device_layout_file = Path(device_file_p.parent, "layout.json")
            if device_layout_file.is_file():
                self.main_win.context = "".join([c for c in self.device.device_name if c.isalnum()]).title()
                self.main_win.layout_load(str(device_layout_file))

            # restore params for device
            if config.device_cfg.device_params:
                self.device.set_parameter_string(config.device_cfg.device_params)

        except Exception as e:
            Info_out(f"\nERROR: Failed to create new EpicDevice from\n{device_file_p.name}!\n{e}\n")
            self.device = None  # type: ignore[assignment]
            self.main_win.context = "UnKnown"
            self.main_win.update_text_outputs()
            return

        try:
            assert self.device.processor_info()
        except AssertionError:
            Info_out("\nERROR: Created new device, but access to device_processor_pointer failed!\n")
            self.device = None  # type: ignore[assignment]
            self.main_win.context = "UnKnown"
            self.main_win.update_text_outputs()
            return

        # create new model and connect it to the new device
        try:
            self.model = Model(self.device)
            if isinstance(self.model, Model):
                Info_out(f"\n{e_boxed_check} New Model() was successfully created with device.\n")
            else:
                self.main_win.update_text_outputs()
                raise EPICpyException(f"\n{e_boxed_x} Error creating new Model() with device.\n")

            # now connect everything up

            self.model.interconnect_device_and_human()

            # if self.model.compile() and self.model.initialize():
            #     Info_out(f"{e_boxed_check} Model() was successfully initialized.")
            # else:
            #     raise EPICpyException(f"{e_boxed_x} Error compiling and initializing Model().")

            self.update_model_output_settings()

        except Exception as e:
            Info_out(f"\nERROR: Simulation unable to properly connect new Device and Model:\n{e}\n")
            self.device = None  # type: ignore[assignment]
            self.main_win.context = "UnKnown"
            self.main_win.update_text_outputs()
            return

        self.main_win.update_title()
        if not quiet:
            Info_out(f"\n{e_boxed_check} Successfully initialized device: {device_file}.\n")

        if self.has_device() and self.model.get_compiled():
            self.main_win.run_state = RUNNABLE
            if hasattr(self.device, "rule_filename"):
                self.device.rule_filename = Path(self.model.get_prs_filename()).name
        else:
            self.main_win.run_state = UNREADY

        self.main_win.update_views(self.instance.get_time())

    def get_encoder_file(self, kind: str) -> str:
        assert kind in ("Visual", "Auditory")
        prev_encoder = config.device_cfg.visual_encoder if kind == "Visual" else config.device_cfg.auditory_encoder
        encoder = Path(prev_encoder).parent
        if prev_encoder and encoder.is_dir():
            if not str(encoder) == ".":
                start_dir = encoder
            else:
                start_dir = Path(config.device_cfg.device_file).parent
        elif config.device_cfg.device_file and Path(config.device_cfg.device_file).parent.is_dir():
            start_dir = Path(config.device_cfg.device_file).parent
        else:
            start_dir = str(Path.home())

        encoder_file, _ = QFileDialog.getOpenFileName(
            self.main_win,
            f"Choose EPICpy {kind} Encoder File",
            str(start_dir),
            "Python Files (*.py)",
        )
        return encoder_file

    def on_unload_encoder(self, kind: str):
        assert kind in ("Auditory", "Visual")
        encoder = self.visual_encoder if kind == "Visual" else self.auditory_encoder

        if not encoder:
            Info_out(f"\nFailed to unload {kind} encoder...none appears to be currently loaded.\n")
            return
        else:
            Info_out(f"\nAttempting to unload {kind} encoder...\n")

        # go ahead and save now. Unlike in on_load_encoder(), we do this first.
        # If unload fails, it will still be effectively unloaded on session reload.

        if kind == "Visual":
            config.device_cfg.visual_encoder = ""
        else:
            config.device_cfg.auditory_encoder = ""

        try:
            assert self.model, f"{e_bangbang} Model doesn't appear to be initialized...has a device been loaded??!!"
            if kind == "Visual":
                self.visual_encoder = NullVisualEncoder("NullVisualEncoder", self)
                set_visual_encoder_ptr(self.model, self.visual_encoder)
            else:
                self.auditory_encoder = NullAuditoryEncoder("NullAuditoryEncoder", self)
                set_auditory_encoder_ptr(self.model, self.auditory_encoder)
        except Exception as e:
            Info_out(
                f"\nERROR: Unable to unload {kind} encoder!\n"
                f"[{e}]\n"
                f"However, it won't be loaded the next time this device is loaded.",
            )
            if kind == "Visual":
                self.visual_encoder = None  # type: ignore[assignment]
            else:
                self.auditory_encoder = None  # type: ignore[assignment]

        self.main_win.update_title()

        Info_out(f"\n{e_boxed_check} {kind} encoder successfully unloaded.\n")
        self.main_win.update_text_outputs()

    def on_load_encoder(self, kind: str, file: str = "", quiet: bool = False):
        assert kind in ("Auditory", "Visual")

        if not file:
            encoder_file = self.get_encoder_file(kind=kind)
        else:
            encoder_file = file

        if encoder_file:
            if kind == "Visual":
                self.visual_encoder = None  # type: ignore[assignment]
            else:
                self.auditory_encoder = None  # type: ignore[assignment]

            # create a new encoder [encoder file must define a class called VisualEncoder]
            encoder_file_p = Path(encoder_file)

            # remove any old encoder paths
            for path in self.visual_encoder_path_additions if kind == "Visual" else self.auditory_encoder_path_additions:
                try:
                    sys.path.remove(path)
                except ValueError:
                    ...

            # Must add encoder parent folder to system path
            if str(encoder_file_p.parent) not in self.device_path_additions:
                self.device_path_additions.append(str(encoder_file_p.parent))
            sys.path.append(str(encoder_file_p.parent))

            # - now we can attempt to import the VisualEncoder or AuditoryEncoder class
            #   from this module
            try:
                # Import and reload the module to pull any changes that have occurred
                # since starting EPICpy
                mod = importlib.import_module(encoder_file_p.stem)
                mod = importlib.reload(mod)

                if not quiet:
                    Info_out(f"\n{e_info} loading encoder from {encoder_file_p.name}...\n")

                ul_name = encoder_file_p.stem.replace("_", " ").title()
                if kind == "Visual":
                    self.visual_encoder = mod.VisualEncoder(ul_name)
                else:
                    self.auditory_encoder = mod.AuditoryEncoder(ul_name)

                if kind == "Visual":
                    setattr(self.visual_encoder, "write", Normal_out)
                else:
                    setattr(self.auditory_encoder, "write", Normal_out)

                if not quiet:
                    Info_out(f"\n{e_info} found {kind}Encoder class, creating new encoder instance based on this class...\n")
                Info_out(f"\n{e_boxed_check} {kind}encoder was created successfully.\n")
            except Exception as e:
                Info_out(f"\nERROR: Failed to create new {kind}Encoder from\n{encoder_file_p.name}:\n{e}\n")
                if kind == "Visual":
                    self.visual_encoder = None  # type: ignore[assignment]
                    config.device_cfg.visual_encoder = ""
                else:
                    self.auditory_encoder = None
                    config.device_cfg.auditory_encoder = ""
                # self.device = None  # NOTE: This was enabled, but seems too harsh?!
                self.main_win.update_text_outputs()
                return

            try:
                assert self.model, f"{e_bangbang} Model doesn't appear to be initialized...has a device been loaded??!!"
                if kind == "Visual":
                    set_visual_encoder_ptr(self.model, self.visual_encoder)
                else:
                    set_auditory_encoder_ptr(self.model, self.auditory_encoder)
            except Exception as e:
                Info_out(f"\nERROR: Created new {kind} encoder, but connection to\nHuman_processor failed:\n{e}\n")
                if kind == "Visual":
                    self.visual_encoder = None  # type: ignore[assignment]
                    config.device_cfg.visual_encoder = ""
                else:
                    self.auditory_encoder = None  # type: ignore[assignment]
                    config.device_cfg.auditory_encoder = ""

                self.main_win.update_text_outputs()
                return

            self.main_win.update_title()

            # go ahead and save in case we need cfg.last_visual_encoder
            if kind == "Visual":
                config.device_cfg.visual_encoder = encoder_file
            else:
                config.device_cfg.auditory_encoder = encoder_file

        self.main_win.update_text_outputs()

    def recompile_rules(self):
        self.current_rule_index = 0
        if self.rule_files and Path(self.rule_files[self.current_rule_index].rule_file).is_file():
            Info_out(f"\n{e_info} Recompiling {self.rule_files[self.current_rule_index].rule_file}...\n")
            self.compile_rule(self.rule_files[self.current_rule_index].rule_file)
        else:
            Info_out("\nERROR: Rule recompile failed because former rule file no longer\nexists or is not readable.\n")
            self.main_win.actionRecompile_Rules.setEnabled(False)

    def choose_rules(self, files: Optional[list] = None) -> bool:
        """
        Select EPIC prs rule file(s) from disk
        """

        if files:
            if all(isinstance(item, RunInfo) for item in files):
                mode = "rule_info"
            elif all(isinstance(item, str) for item in files):
                mode = "rule_files"
            else:
                the_types = set([type(item) for item in files])
                Info_out(
                    f"\nERROR: epic_simulation.choose_rules can only accept a list of ALL RuleInfo objects, or"
                    f" a list of ALL rule file path strings, not a list consisting of multiple types"
                    f" (e.g., {the_types})."
                )
                raise ValueError("Mixed types given to choose_rule function!")
        else:
            mode = "rule_files"

        if not files:
            note = "selected"
            if config.device_cfg.device_file and Path(config.device_cfg.device_file).parent.is_dir():
                start_dir = Path(config.device_cfg.device_file).parent
            else:
                start_dir = str(Path.home())

            rule_files = QFileDialog.getOpenFileNames(
                self.main_win,
                "Choose 1 or More EPIC RuleSet Files",
                str(start_dir),
                "Rule files (*.prs)",
            )[0]

            rule_files = [RunInfo(False, "", str(Path(item).resolve()), "", False, False) for item in rule_files]

        elif files and mode == "rule_files":
            note = "reloaded"
            rule_files = [RunInfo(False, "", str(Path(item).resolve()), "", False, False) for item in files]
        elif files and mode == "rule_info":
            note = "scripted"
            rule_files = [
                RunInfo(
                    item.from_script,
                    str(Path(item.device_file).resolve()),
                    str(Path(item.rule_file).resolve()),
                    item.parameter_string,
                    item.clear_data,
                    item.reload_device,
                )
                for item in files
            ]
        else:
            raise ValueError(f"Unknown state in epic_simulation.choose_rules(): {mode=} {files=}")

        if rule_files:
            self.rule_files = rule_files
            self.current_rule_index = 0

            rule_file_paths = [item.rule_file for item in rule_files]

            # go ahead and save in case we need cfg.rule_files
            if not any(item.from_script for item in self.rule_files):
                config.device_cfg.rule_files = rule_file_paths
            line_end = "\n"
            Info_out(
                f"\n{len(rule_file_paths)} ruleset files {note}:\n"
                f"{line_end.join(Path(rule_file).name for rule_file in rule_file_paths)}"
            )
            Info_out(
                f"\n{e_info} Attempting to compile first rule in {note} ruleset list..."
                if len(rule_files) > 1
                else f"\n{e_info} Attempting to compile {note} ruleset..."
            )

            return self.compile_rule(
                self.rule_files[self.current_rule_index].rule_file,
                note.lower() == "reloaded",
            )
        else:
            self.rule_files = []
            Info_out(f"\n{e_boxed_x} No valid rule file(s) {note}.\n")

        return False

    def compile_rule(self, file: str = "", calm: bool = False) -> bool:
        rule_path = Path(file)

        try:
            # try to compile rule
            self.model.set_prs_filename(file)
            result = self.model.compile() and self.model.initialize()
        except Exception as e:
            if calm:
                Info_out(f"\nWARNING: Unable to compile ruleset file\n{rule_path.name}:\n{e}\n")
            else:
                Info_out(
                    f"\nERROR: Unable to compile ruleset file\n{rule_path.name}:\n{e}",
                )
            result = False

        if result:
            Info_out(f"\nRule file {rule_path.name} compiled successfully!\n")
            self.main_win.update_title()
            rule_compiled = True
        else:
            if calm:
                Info_out(f"\nWARNING: Unable to (re)compile ruleset file\n{rule_path.name}\n")
            else:
                Info_out(f"\nERROR: Unable to (re)compile ruleset file\n{rule_path.name}!\n")
            rule_compiled = False

        # make sure run state reflects result of rule compile attempt
        if self.has_device() and self.model.get_compiled():
            self.main_win.run_state = RUNNABLE

            if hasattr(self.device, "rule_filename"):
                self.device.rule_filename = Path(str(self.model.get_prs_filename())).name
        else:
            self.main_win.run_state = UNREADY

        self.main_win.update_text_outputs()
        return rule_compiled

    def add_views_to_model(
        self,
        visual_physical: EPICVisualView,
        visual_sensory: EPICVisualView,
        visual_perceptual: EPICVisualView,
        auditory_physical: EPICVisualView,
        auditory_sensory: EPICVisualView,
        auditory_perceptual: EPICVisualView,
    ):
        try:
            self.model.add_visual_physical_view(visual_physical)
            self.model.add_visual_sensory_view(visual_sensory)
            self.model.add_visual_perceptual_view(visual_perceptual)
            self.model.add_auditory_physical_view(auditory_physical)
            self.model.add_auditory_sensory_view(auditory_sensory)
            self.model.add_auditory_perceptual_view(auditory_perceptual)
        except Exception as e:
            self.main_win.update_text_outputs()
            Info_out(f"Unable to add views to model: {e}\n")

    def remove_views_from_model(
        self,
        visual_physical: EPICVisualView,
        visual_sensory: EPICVisualView,
        visual_perceptual: EPICVisualView,
        auditory_physical: EPICVisualView,
        auditory_sensory: EPICVisualView,
        auditory_perceptual: EPICVisualView,
    ):
        try:
            self.model.get_human_ptr().remove_visual_physical_view(visual_physical)
            self.model.get_human_ptr().remove_visual_sensory_view(visual_sensory)
            self.model.get_human_ptr().remove_visual_perceptual_view(visual_perceptual)
            self.model.get_human_ptr().remove_auditory_physical_view(auditory_physical)
            self.model.get_human_ptr().remove_auditory_sensory_view(auditory_sensory)
            self.model.get_human_ptr().remove_auditory_perceptual_view(auditory_perceptual)
        except Exception as e:
            self.main_win.update_text_outputs()
            Info_out(f"Unable to remove views to model: {e}\n")

    def run_one_step(self):
        # just in case output settings were changed between runs
        self.update_model_output_settings()

        self.last_run_mode = "run_one_step"
        try:
            self.instance.run_for(50)
            self.call_for_display_refresh()

            run_result = self.device.state != self.device.SHUTDOWN
            self.run_time = self.model.get_time()
        except Exception as e:
            run_result = False
            Normal_out(f"\nERROR:\n{e}\n")
            self.main_win.update_text_outputs()
            return

        if not run_result:
            self.main_win.run_state = RUNNABLE
        else:
            self.main_win.run_state = PAUSED
            self.main_win.run_state = PAUSED

        self.main_win.update_text_outputs()

    def run(self, clear_ui: bool = True):
        # just in case output settings were changed between runs
        self.update_model_output_settings()
        if self.main_win.run_state not in (RUNNABLE, PAUSED):
            # This shouldn't be possible
            Info_out(
                "\nERROR: Unable to run simulation because model is not yet RUNNABLE\n"
                "(device successfully loaded and rules successfully compiled).",
            )
            return

        self.last_run_mode = "run_normal"

        self.run_time = self.model.get_time()
        if self.main_win.run_state == RUNNABLE:
            self.main_win.clear_ui(
                visual_views=True,
                auditory_views=True,
                normal_output=clear_ui and len(self.rule_files) == 1,
                trace_output=True,
                stats_output=True,
                info_output=False,
            )

            self.instance.initialize()

            # call encoder initializers
            if self.has_visual_encoder():
                self.visual_encoder.initialize()
            if self.has_auditory_encoder():
                self.auditory_encoder.initialize()  # type: ignore[assignment]

            self.model.initialize()

            if config.device_cfg.describe_parameters:
                if desc_param_loaded:
                    Normal_out(f"\n{describe_parameters_u(self.model)}\n")

            Normal_out("\nSIMULATION STARTING\n")

            device_param_str = self.device.get_parameter_string()

            if "[" in device_param_str:
                self.raw_device_param_string = device_param_str
                self.param_set = unpack_param_string(device_param_str)

            if self.param_set:
                current_param = self.param_set.pop()
                self.device.set_parameter_string(current_param)
                Info_out(f"{self.device.get_name()}: {current_param}\n")

            run_commands = {
                "run_for": self.run_time + int(config.device_cfg.run_command_value),
                "run_until": int(config.device_cfg.run_command_value),
                "run_for_cycles": self.run_time + int(config.device_cfg.run_command_value) * 50,
                "run_until_done": sys.maxsize,
            }
            if config.device_cfg.run_command in run_commands:
                self.run_time_limit = run_commands.get(config.device_cfg.run_command, sys.maxsize)
            else:
                Normal_out(
                    f"\n{e_info} WARNING: unexpected run command found in config file "
                    f' ("{config.device_cfg.run_command}"), using "RUN_UNTIL_DONE" '
                    f"instead.\n"
                )

        elif self.main_win.run_state == PAUSED:
            if config.device_cfg.run_command in ("run_for", "run_for_cycles"):
                # go again if we ran for the specified amount of time or we paused
                #   and then changed
                if self.run_time >= self.run_time_limit:
                    self.run_time_limit = self.run_time + int(config.device_cfg.run_command_value)
                elif config.device_cfg.run_command == "run_until":
                    # are we past the specified time or did we pause and change from
                    #   run until done?
                    if self.run_time >= config.device_cfg.run_command_value:
                        Normal_out(f"\n{e_info} Unable to run additional steps, RUN_UNTIL_TIME value already reached!\n")
                    self.run_time_limit = 0
                    return
                else:
                    self.run_time_limit = 0

        Normal_out("\nRun Started...\n")
        self.main_win.run_state = RUNNING
        self.stop_model_now = False
        self.user_stopped = False

        # Raise Info Output tab so user can see run progress
        self.main_win.dockInfo.raise_()

        disable_views = config.device_cfg.display_refresh == "none_during_run"
        # Enable batch_mode for all controlled refresh modes to suppress update() calls
        # from epiclibcpp notifications - we'll trigger updates explicitly
        batch_mode = config.device_cfg.display_refresh in ("after_every_sec", "after_each_step")

        self.main_win.enable_view_updates(not disable_views)
        self.main_win.set_view_batch_mode(batch_mode)

        self.steps_run = 0
        self.steps_since_last_display = 0
        self.run_start_time = timeit.default_timer()
        self.run_timer.singleShot(config.device_cfg.step_time_delay, self.run_next_cycle)

    def run_next_cycle(self):
        if self.main_win.run_state != RUNNING or self.stop_model_now:
            return

        try:
            self.instance.run_for(50)
            self.call_for_display_refresh()

            run_result = self.device.state != self.device.SHUTDOWN
            self.run_time = self.model.get_time()
            self.steps_run += 1
        except Exception as e:
            run_result = False
            msg = f"\nERROR: Run of {self.device.rule_filename} Stopped With Error:\n{e}"

            if config.app_cfg.show_full_error_trace:
                msg += f"\n{rich_traceback_str(e)}\n"

            self.halt_simulation("error", msg)
            return

        if self.instance.is_paused():
            # this is presumably because of a rule with a break state set
            self.main_win.run_state = PAUSED
            Normal_out(f"\n{e_info} Run of {self.device.rule_filename} Paused.\n")

        if run_result and (
            (config.device_cfg.run_command in ("run_for", "run_until") and self.run_time < self.run_time_limit)
            or (config.device_cfg.run_command == "run_until_done")
            or config.device_cfg.run_command == "run_for_cycles"
            and self.steps_run < config.device_cfg.run_command_value
        ):
            # *** Still running, keep going
            self.run_timer.singleShot(config.device_cfg.step_time_delay, self.run_next_cycle)
        else:
            # *** Running seems to be done, shut it down
            self.main_win.run_state = PAUSED if run_result else RUNNABLE
            if self.main_win.run_state == PAUSED:
                self.pause_simulation()
                if config.device_cfg.run_command == "run_for_cycles":
                    self.steps_run = 0
            elif self.main_win.run_state == RUNNABLE:
                msg = f"\n{e_boxed_ok} Run of {self.device.rule_filename} Finished."
                self.halt_simulation("finished", msg)

    def pause_simulation(self):
        if self.main_win.run_state == RUNNING:
            self.main_win.run_state = PAUSED

        self.call_for_display_refresh()

        # just in case these were disabled during the run
        self.main_win.enable_view_updates(True)
        self.main_win.set_view_batch_mode(False)

        self.main_win.update_text_outputs()

        Normal_out(f"\n{e_info} Run paused\n")

    def halt_simulation(self, reason: str = "", extra: str = "", force: bool = False):
        duration = timeit.default_timer() - self.run_start_time

        try:
            self.device.stop_simulation()
        except Exception as e:
            self.main_win.update_text_outputs()
            Exception_out(f"While calling `self.device.stop_simulation()` got this error: {e}\n")

        try:
            self.model.stop()
            self.instance.stop()
        except Exception as e:
            self.main_win.update_text_outputs()
            Exception_out(f"(Simulator.model.stop(); Simulator.instance.stop()) = {e}\n")

        # self.model.initialized = False  # model.stop should do this!
        # self.model.running = False      # model.stop should do this!
        self.main_win.run_state = RUNNABLE
        self.stop_model_now = True

        # if we're done with all param set permutations, update ui
        if self.last_run_mode == "run_normal" or not self.param_set:
            self.call_for_display_refresh()

            # just in case these were disabled during the run
            self.main_win.enable_view_updates(True)
            self.main_win.set_view_batch_mode(False)

        if not reason:
            Normal_out(f"\n{e_bangbang} Run halted\n")

        Normal_out(extra)

        msg = f" (run took {duration:0.4f} seconds)\n"

        Normal_out(msg)
        Trace_out(msg)
        Info_out(msg)

        if force:
            self.model.stop()
            self.instance.stop()

        # For ensuring that all param string versions get run
        #  when done, drop to next section to make sure all files get run!

        run_func = {"run_normal": self.run}

        # If user manually stopped, set flag and clear continuation state
        if reason == "user_stop":
            self.user_stopped = True
            self.param_set = []
            self.raw_device_param_string = ""
            self.current_rule_index = len(self.rule_files)  # Prevent rule file continuation
            return

        # If user previously requested stop, don't continue even on natural finish
        if self.user_stopped:
            return

        if self.last_run_mode in run_func and self.raw_device_param_string and reason:
            if self.param_set:
                run_func[self.last_run_mode](clear_ui=False)
                self.main_win.update_text_outputs()
                return  # don't worry about running other rule files
            else:
                self.device.set_parameter_string(self.raw_device_param_string)
                self.raw_device_param_string = ""
                self.param_set = []

        # For ensuring that all rules in list get run
        if self.last_run_mode in run_func:
            self.current_rule_index += 1
            if self.current_rule_index < len(self.rule_files):
                next_sim = self.rule_files[self.current_rule_index]
                prev_sim = self.rule_files[self.current_rule_index - 1]
                rule_name = Path(next_sim.rule_file).name
                Info_out(f"\nRULE FILE: {rule_name} ({self.current_rule_index}/{len(self.rule_files)})\n")

                if next_sim.clear_data:
                    # nothing that this is an odd thing to ask for...what's the point in running
                    # multiple files if you are only going to end up with data from the last one?!
                    self.main_win.delete_datafile()

                # NOTE: when not running from script, next_sim.device_file & prev_sim.device_file are both ''
                #       and next_sim.reload_device is False. Thus, this section gets bypassed
                if (next_sim.device_file and next_sim.device_file != prev_sim.device_file) or next_sim.reload_device:
                    if not self.main_win.on_load_device(next_sim.device_file, auto_load_rules=False, quiet=True):
                        Info_out(
                            f"\n{e_boxed_x} Device (re)load failed while running "
                            f"{next_sim.device_file} + {next_sim.rule_file} from script!"
                        )
                        self.current_rule_index = 0
                        self.main_win.update_text_outputs()
                        return

                if next_sim.parameter_string:
                    self.device.set_parameter_string(next_sim.parameter_string)

                if self.compile_rule(next_sim.rule_file):
                    run_func[self.last_run_mode](clear_ui=False)
                else:
                    self.current_rule_index += 1
                    if self.current_rule_index < len(self.rule_files):
                        Info_out(f"\n{e_boxed_x} Compile Failed for {rule_name}, moving to next rule in list....\n")
                        if self.compile_rule(self.rule_files[self.current_rule_index].rule_file):
                            run_func[self.last_run_mode](clear_ui=False)
                    else:
                        self.current_rule_index = 0
            else:
                self.current_rule_index = 0

        self.main_win.update_text_outputs()

        # All runs complete - raise Normal Output tab and scroll to bottom
        # self.main_win.dockNormal.raise_()
        self.main_win.normalTextOutput.scroll_to_bottom()

        try:
            html = self.device.show_output_stats()
            self.main_win.stats_win.setHtml(html)
        except Exception as e:
            msg = f"""
                <span style="color: red;">
                <h2>Unable to render analysis for 
                {self.device.get_name() if self.has_device else "Current Device"}
                </h2>:<br><b>{str(e)}</b>
                </span>
                """
            self.main_win.stats_win.setHtml(msg)
            Info_out(msg + "\n")
