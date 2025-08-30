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
import warnings
from typing import Optional, List
from pathlib import Path
import sys
import weakref
import timeit

from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QFileDialog

from epicpy.utils.apputils import unpack_param_string

from epicpy.epic.encoderpassthru import NullVisualEncoder, NullAuditoryEncoder
from epicpy.epic.epicpyexception import EPICpyException
from epicpy.epic.runinfo import RunInfo
from epicpy.constants.stateconstants import *
from epicpy.constants.emoji import *
from epicpy.dialogs.loggingwindow import LoggingSettingsWin

from epicpy.utils import config

from epicpy.utils.modulereloader import reset_module
from epicpy.views.epicpy_visualview import EPICVisualView

warnings.filterwarnings("ignore", module=r"^matplotlib")
warnings.filterwarnings("ignore", module=r"^pingouin")
warnings.filterwarnings("ignore", module=r"^pandas")


# KEEP HERE, USED IN EXEC STATEMENT!

# KEEP HERE, NEEDED FOR DEVICES

from epicpy.epiclib.epiclib.output_tee_globals import Normal_out, Trace_out, Exception_out
from epicpy.epiclib.epiclib import Model, Coordinator
from epicpy.epiclib.epiclib import set_visual_encoder_ptr, set_auditory_encoder_ptr

try:
    from epicpy.epiclib.epiclib import describe_parameters_u

    desc_param_loaded = True
except:
    desc_param_loaded = False
    Exception_out(f'WARNING: Failed to load "describe_parameters_u" from epiclib. Will not be able to dump parameters.')


class Simulation:
    def __init__(self, parent):
        self.parent = parent

        self.device = None
        self.model = None
        self.visual_encoder = None
        self.auditory_encoder = None

        self.instance = Coordinator.get_instance()
        self.stop_model_now = False

        self.keep_checking_run = False
        self.run_start_time = 0
        self.run_time = 0
        self.run_time_limit = 0
        self.run_timer = QTimer()
        self.rule_files: List[RunInfo] = []
        self.last_run_mode = ""
        self.current_rule_index = 0
        self.last_update_time = timeit.default_timer()
        self.default_device_parameters = ""

        self.steps_since_last_text_out = 0
        self.steps_run = 0

        self.raw_device_param_string = ""
        self.param_set = []

        self.device_path_additions = []
        self.visual_encoder_path_additions = []
        self.auditory_encoder_path_additions = []

    def call_for_display_refresh(self):
        current_time = self.instance.get_time()
        if config.device_cfg.display_refresh in ("after_each_step", "continuously"):
            self.parent.update_views(current_time)
        elif config.device_cfg.display_refresh == "after_every_sec":
            current_timeit = timeit.default_timer()  # Cache timer result
            if current_timeit - self.last_update_time >= float(config.device_cfg.run_command_value):
                self.parent.update_views(current_time)
                self.last_update_time = current_timeit  # Reuse cached value

        # ** if 'never_during_run' then this function does nothing

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
            Normal_out(f"\n❌ ERROR: Failed to update EPIC output or trace settings:\n{e}\n")

    def on_load_device(self, device_file: str = "", quiet: bool = False):

        # load config for this device, or create new device on if none exists already
        dark_mode = config.app_cfg.dark_mode
        current = config.device_cfg.current

        config.get_device_config(Path(device_file))
        config.device_cfg.device_file = device_file

        config.app_cfg.dark_mode = dark_mode
        config.device_cfg.current = current

        # save global app config in case we need last_device_file
        config.app_cfg.last_device_file = device_file

        if not config.device_cfg.normal_out_file:
            config.device_cfg.normal_out_file = LoggingSettingsWin.default_log_filename("normal")
        if not config.device_cfg.trace_out_file:
            config.device_cfg.trace_out_file = LoggingSettingsWin.default_log_filename("trace")
        if not config.device_cfg.stats_out_file:
            config.device_cfg.stats_out_file = LoggingSettingsWin.default_log_filename("stats")

        if self.device:
            # make sure device data output gets flushed and saved no matter how
            # device object is deleted, includes normal exit/quit as well as
            # exceptions! Because the target method, or even the data file handle
            # are not part of Device_base, we have to condition this feature on
            # whether the expected attributes are present.
            if hasattr(self.device, "finalize_data_output"):
                weakref.finalize(self.device, self.device.finalize_data_output)
            elif hasattr(self.device, "data_file"):
                weakref.finalize(self.device, self.device.data_file.close)
            else:
                # data file will not be guaranteed to automatically closed in every
                # case. However, on normal exit (an often on abnormal ones), Python
                # is pretty good about open file handles. I'm just not sure if
                # *all* available data will be preserved.
                pass

        self.current_rule_index = 0
        self.device = None

        # these will be handy
        device_file_p = Path(device_file)
        device_file_root = device_file_p.parent

        # make sure __init__.py exists in device folder
        if not Path(device_file_root, "../__init__.py").is_file():
            Normal_out(
                f'\n{e_info} Unable to find "__init__.py" in device folder '
                f"({str(device_file_root)}). Will attempt to create one.\n"
            )
            try:
                Path(device_file_root, "../__init__.py").write_text("")
            except IOError:
                Normal_out(
                    f"\nERROR: Unable to create needed file \n"
                    f'"{str(Path(device_file_root, "../__init__.py"))}".\n'
                    f"If your device does not load correctly, you may need to\n"
                    f"obtain write access to the device folder.\n",
                )

        # remove any old device path additions
        for path in self.device_path_additions:
            if path in sys.path:
                sys.path.remove(path)

        # Must add parents folder to system path
        for parent_path in (
            device_file_p.parent,
            device_file_p.parent.parent,
            device_file_p.parent.parent.parent,
        ):
            if parent_path.is_dir():
                sys.path.append(str(parent_path))
                self.device_path_additions.append(str(parent_path))

        # - now we can attempt to import the EpicDevice class from this module
        try:
            # despite appearances, BOTH of the following lines are required if we
            # want a device reload to pull any changes that have occurred since
            # starting EPICpy!
            module_name = device_file_p.stem  # Get module name without .py
            module = importlib.import_module(module_name)  # Import dynamically
            reset_module(module)  # Use your custom reset function

            # Inject the module into the global namespace so it behaves like an `import` statement
            globals()[module_name] = module

            if not quiet:
                Normal_out(f"\n{e_info} loading device code from {device_file_p.name}...\n")

            # Dynamically retrieve the class and instantiate the object
            EpicDeviceClass = getattr(module, "EpicDevice", None)
            if EpicDeviceClass is None:
                raise ImportError(f"Class 'EpicDevice' not found in module '{module_name}'.")

            self.device = EpicDeviceClass(ot=Normal_out, parent=self.parent, device_folder=device_file_p.parent)

            if not quiet:
                Normal_out(f"\n{e_info} found EpicDevice class, created new device instance based on this class.\n")
            Normal_out(f"\n{e_boxed_check} {self.device.device_name} device was created successfully.\n")

            # must store default device params before we reload one from settings
            if hasattr(self.device, "condition_string"):
                self.default_device_parameters = str(self.device.condition_string)
            else:
                self.default_device_parameters = ""

            # restore layout for device
            device_layout_file = Path(device_file_p.parent, "layout.json")
            if device_layout_file.is_file():
                self.parent.context = "".join([c for c in self.device.device_name if c.isalnum()]).title()
                self.parent.layout_load(str(device_layout_file))

            # restore params for device
            if config.device_cfg.device_params:
                self.device.set_parameter_string(config.device_cfg.device_params)

        except Exception as e:
            Normal_out(f"\nERROR: Failed to create new EpicDevice from\n{device_file_p.name}!\n{e}\n")
            self.device = None
            self.parent.context = "UnKnown"
            return

        try:
            assert self.device.processor_info()
        except AssertionError:
            Normal_out(f"\nERROR: Created new device, but access to device_processor_pointer failed!\n")
            self.device = None
            self.parent.context = "UnKnown"
            return

        # create new model and connect it to the new device
        try:
            self.model = Model(self.device)
            if isinstance(self.model, Model):
                Normal_out(f"\n{e_boxed_check} New Model() was successfully created with device.\n")
            else:
                raise EPICpyException(f"\n{e_boxed_x} Error creating new Model() with device.\n")

            # now connect everything up

            self.model.interconnect_device_and_human()

            # if self.model.compile() and self.model.initialize():
            #     Normal_out(f"{e_boxed_check} Model() was successfully initialized.")
            # else:
            #     raise EPICpyException(f"{e_boxed_x} Error compiling and initializing Model().")

            self.update_model_output_settings()

        except Exception as e:
            Normal_out(f"\nERROR: Simulation unable to properly connect new Device and Model:\n{e}\n")
            self.device = None
            self.parent.context = "UnKnown"
            return

        self.parent.update_title()
        if not quiet:
            Normal_out(f"\n{e_boxed_check} Successfully initialized device: {device_file}.\n")

        if self.device and self.model.get_compiled():
            self.parent.run_state = RUNNABLE
            if hasattr(self.device, "rule_filename"):
                self.device.rule_filename = Path(self.model.get_prs_filename()).name
        else:
            self.parent.run_state = UNREADY

        self.parent.update_views(self.instance.get_time())

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
            self.parent,
            f"Choose EPICpy {kind} Encoder File",
            str(start_dir),
            "Python Files (*.py)",
        )
        return encoder_file

    def on_unload_encoder(self, kind: str):
        assert kind in ("Auditory", "Visual")
        encoder = self.visual_encoder if kind == "Visual" else self.auditory_encoder

        if not encoder:
            Normal_out(f"\nFailed to unload {kind} encoder...none appears to be currently loaded.\n")
            return
        else:
            Normal_out(f"\nAttempting to unload {kind} encoder...\n")

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
                # self.model.get_human_ptr().set_visual_encoder_ptr(self.visual_encoder)
                set_visual_encoder_ptr(self.model, self.visual_encoder)
            else:
                # note "aditory" spelling is from C++ code. When the spelling
                # gets fixed there, will fix it here!
                self.auditory_encoder = NullAuditoryEncoder("NullAuditoryEncoder", self)
                # self.model.get_human_ptr().set_aditory_encoder_ptr( self.auditory_encoder )
                set_auditory_encoder_ptr(self.model, self.auditory_encoder)
        except Exception as e:
            Normal_out(
                f"\nERROR: Unable to unload {kind} encoder!\n"
                f"[{e}]\n"
                f"However, it won't be loaded the next time this device is loaded.\n",
            )
            if kind == "Visual":
                self.visual_encoder = None
            else:
                self.auditory_encoder = None
            # self.device = None  # NOTE: This was enabled, but seems too hard?!

        self.parent.update_title()

        Normal_out(f"\n{e_boxed_check} {kind} encoder successfully unloaded.\n")

    def on_load_encoder(self, kind: str, file: str = "", quiet: bool = False):
        assert kind in ("Auditory", "Visual")

        if not file:
            encoder_file = self.get_encoder_file(kind=kind)
        else:
            encoder_file = file

        if encoder_file:
            if kind == "Visual":
                self.visual_encoder = None
            else:
                self.auditory_encoder = None

            # create a new encoder [encoder file must define a class called VisualEncoder]
            encoder_file_p = Path(encoder_file)

            # remove any old encoder paths
            for path in (
                self.visual_encoder_path_additions if kind == "Visual" else self.auditory_encoder_path_additions
            ):
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
                # despite appearances, BOTH of the following lines are required if we
                # want an encoder reload to pull any changes that have occurred since
                # starting EPICpy!
                exec(f"import {encoder_file_p.stem}")
                from epicpy.utils.modulereloader import reset_module

                exec(f"reset_module({encoder_file_p.stem})")

                if not quiet:
                    Normal_out(f"\n{e_info} loading encoder from {encoder_file_p.name}...\n")

                ul_name = encoder_file_p.stem.replace("_", " ").title()
                if kind == "Visual":
                    exec(f'self.visual_encoder = {encoder_file_p.stem}.VisualEncoder("{ul_name}", self)')
                else:
                    exec(f'self.auditory_encoder = {encoder_file_p.stem}.AuditoryEncoder("{ul_name}", self)')

                if kind == "Visual":
                    setattr(self.visual_encoder, "write", Normal_out)
                else:
                    setattr(self.auditory_encoder, "write", Normal_out)

                if not quiet:
                    Normal_out(
                        f"\n{e_info} found {kind}Encoder class, creating new encoder instance based on this class...\n"
                    )
                Normal_out(f"\n{e_boxed_check} {kind}encoder was created successfully.\n")
            except Exception as e:
                Normal_out(f"\nERROR: Failed to create new {kind}Encoder from\n{encoder_file_p.name}: {e}\n")
                if kind == "Visual":
                    self.visual_encoder = None
                    config.device_cfg.visual_encoder = ""
                else:
                    self.auditory_encoder = None
                    config.device_cfg.auditory_encoder = ""
                # self.device = None  # NOTE: This was enabled, but seems too harsh?!
                return

            try:
                assert self.model, f"{e_bangbang} Model doesn't appear to be initialized...has a device been loaded??!!"
                if kind == "Visual":
                    # self.model.get_human_ptr().set_visual_encoder_ptr( self.visual_encoder )
                    set_visual_encoder_ptr(self.model, self.visual_encoder)
                else:
                    # self.model.get_human_ptr().set_auditory_encoder_ptr( self.auditory_encoder )
                    set_auditory_encoder_ptr(self.model, self.auditory_encoder)
            except Exception as e:
                Normal_out(f"\nERROR: Created new {kind} encoder, but connection to\nHuman_processor failed:\n{e}\n")
                if kind == "Visual":
                    self.visual_encoder = None
                    config.device_cfg.visual_encoder = ""
                else:
                    self.auditory_encoder = None
                    config.device_cfg.auditory_encoder = ""
                # self.device = None  # NOTE: This was enabled, but seems too hard?!
                return

            self.parent.update_title()

            # go ahead and save in case we need cfg.last_visual_encoder
            if kind == "Visual":
                config.device_cfg.visual_encoder = encoder_file
            else:
                config.device_cfg.auditory_encoder = encoder_file

    def recompile_rules(self):
        self.current_rule_index = 0
        if self.rule_files and Path(self.rule_files[self.current_rule_index].rule_file).is_file():
            Normal_out(f"\n{e_info} Recompiling {self.rule_files[self.current_rule_index].rule_file}...\n")
            self.compile_rule(self.rule_files[self.current_rule_index].rule_file)
        else:
            Normal_out(
                f"\nERROR: Rule recompile failed because former rule file no longer\nexists or is not readable.\n"
            )
            self.parent.actionRecompile_Rules.setEnabled(False)

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
                Normal_out(
                    f"\nERROR: epicsimulation.choose_rules can only accept a list of ALL RuleInfo objects, or"
                    f" a list of ALL rule file path strings, not a list consisting of multiple types"
                    f" (e.g., {the_types}).\n"
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
                self.parent,
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
            raise ValueError(f"Unknown state in epicsimulation.choose_rules(): {mode=} {files=}")

        if rule_files:
            self.rule_files = rule_files
            self.current_rule_index = 0

            rule_file_paths = [item.rule_file for item in rule_files]

            # go ahead and save in case we need cfg.rule_files
            if not any(item.from_script for item in self.rule_files):
                config.device_cfg.rule_files = rule_file_paths
            endl = "\n"
            Normal_out(
                f"\n{len(rule_file_paths)} ruleset files {note}:\n"
                f"{endl.join(Path(rule_file).name for rule_file in rule_file_paths)}\n"
            )
            Normal_out(
                f"\n{e_info} Attempting to compile first rule in {note} ruleset list...\n"
                if len(rule_files) > 1
                else f"\n{e_info} Attempting to compile {note} ruleset...\n"
            )

            return self.compile_rule(
                self.rule_files[self.current_rule_index].rule_file,
                note.lower() == "reloaded",
            )
        else:
            self.rule_files = []
            Normal_out(f"\n{e_boxed_x} No valid rule file(s) {note}.\n")

        return False

    def compile_rule(self, file: str = "", calm: bool = False) -> bool:
        rule_path = Path(file)

        try:
            # try to compile rule
            self.model.set_prs_filename(file)
            result = self.model.compile() and self.model.initialize()
        except Exception as e:
            if calm:
                Normal_out(f"\nWARNING: Unable to compile ruleset file\n{rule_path.name}: {e}\n")
            else:
                Normal_out(
                    f"\nERROR: Unable to compile ruleset file\n{rule_path.name}:\n{e}\n",
                )
            result = False

        if result:
            Normal_out(f"\nRule file {rule_path.name} compiled successfully!\n")
            self.parent.update_title()
            rule_compiled = True
        else:
            if calm:
                Normal_out(f"\nWARNING: Unable to (re)compile ruleset file\n{rule_path.name}\n")
            else:
                Normal_out(f"\nERROR: Unable to (re)compile ruleset file\n" f"{rule_path.name}!\n")
            rule_compiled = False

        # make sure run state reflects result of rule compile attempt
        if self.device and self.model.get_compiled():
            self.parent.run_state = RUNNABLE

            if hasattr(self.device, "rule_filename"):
                self.device.rule_filename = Path(str(self.model.get_prs_filename())).name
        else:
            self.parent.run_state = UNREADY

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
        self.model.add_visual_physical_view(visual_physical)
        self.model.add_visual_sensory_view(visual_sensory)
        self.model.add_visual_perceptual_view(visual_perceptual)
        self.model.add_auditory_physical_view(auditory_physical)
        self.model.add_auditory_sensory_view(auditory_sensory)
        self.model.add_auditory_perceptual_view(auditory_perceptual)

    def remove_views_from_model(
        self,
        visual_physical: EPICVisualView,
        visual_sensory: EPICVisualView,
        visual_perceptual: EPICVisualView,
        auditory_physical: EPICVisualView,
        auditory_sensory: EPICVisualView,
        auditory_perceptual: EPICVisualView,
    ):
        self.model.get_human_ptr().remove_visual_physical_view(visual_physical)
        self.model.get_human_ptr().remove_visual_sensory_view(visual_sensory)
        self.model.get_human_ptr().remove_visual_perceptual_view(visual_perceptual)
        self.model.get_human_ptr().remove_auditory_physical_view(auditory_physical)
        self.model.get_human_ptr().remove_auditory_sensory_view(auditory_sensory)
        self.model.get_human_ptr().remove_auditory_perceptual_view(auditory_perceptual)

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
            return

        if not run_result:
            self.parent.run_state = RUNNABLE
        else:
            self.parent.run_state = PAUSED
            self.parent.run_state = PAUSED

    def run_all(self, clear_ui: bool = True):
        # just in case output settings were changed between runs
        self.update_model_output_settings()
        if self.parent.run_state not in (RUNNABLE, PAUSED):
            # This shouldn't be possible
            Normal_out(
                f"\nERROR: Unable to run simulation because model is not yet RUNNABLE\n"
                f"(device successfully loaded and rules successfully compiled).\n",
            )
            return

        self.last_run_mode = "run_all"

        self.run_time = self.model.get_time()
        if self.parent.run_state == RUNNABLE:
            self.parent.clear_ui(
                visual_views=True,
                auditory_views=True,
                normal_output=clear_ui and len(self.rule_files) == 1,
                trace_output=True,
                stats_output=True,
            )

            self.instance.initialize()

            # call encoder initializers
            if self.visual_encoder:
                self.visual_encoder.initialize()
            if self.auditory_encoder:
                self.auditory_encoder.initialize()

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

        elif self.parent.run_state == PAUSED:
            if config.device_cfg.run_command in ("run_for", "run_for_cycles"):
                # go again if we ran for the specified amount of time or we paused
                #   and then changed
                if self.run_time >= self.run_time_limit:
                    self.run_time_limit = self.run_time + int(config.device_cfg.run_command_value)
                elif config.device_cfg.run_command == "run_until":
                    # are we past the specified time or did we pause and change from
                    #   run until done?
                    if self.run_time >= config.device_cfg.run_command_value:
                        Normal_out(
                            f"\n{e_info} Unable to run additional steps, RUN_UNTIL_TIME value already reached!\n"
                        )
                    self.run_time_limit = 0
                    return
                else:
                    self.run_time_limit = 0

        Normal_out(f"\nRun Started...\n")
        self.parent.run_state = RUNNING

        disable_views = config.device_cfg.display_refresh == "none_during_run"
        disable_text = config.device_cfg.text_refresh == "none_during_run"
        self.parent.enable_view_updates(not disable_views)
        self.parent.enable_text_updates(not disable_text)

        self.steps_run = 0
        self.run_start_time = timeit.default_timer()
        self.run_timer.singleShot(config.device_cfg.step_time_delay, self.run_next_cycle)

    def run_next_cycle(self):
        if self.parent.run_state != RUNNING:
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
            self.halt_simulation("error", msg)
            return

        if self.instance.is_paused():
            # this is presumably because of a rule with a break state set
            self.parent.run_state = PAUSED
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
            self.parent.run_state = PAUSED if run_result else RUNNABLE
            if self.parent.run_state == PAUSED:
                self.pause_simulation()
                if config.device_cfg.run_command == "run_for_cycles":
                    self.steps_run = 0
            elif self.parent.run_state == RUNNABLE:
                msg = f"\n{e_boxed_ok} Run of {self.device.rule_filename} Finished."
                self.halt_simulation("finished", msg)

    def pause_simulation(self):
        if self.parent.run_state == RUNNING:
            self.parent.run_state = PAUSED

        self.call_for_display_refresh()

        # just in case these were disabled during the run
        self.parent.enable_view_updates(True)
        self.parent.enable_text_updates(True)

        # _ = self.wait_until_text_outputs_are_idle()  # TODO: DELME

        Normal_out(f"\n{e_info} Run paused\n")

    # TODO: DELME
    # def wait_until_text_outputs_are_idle(self) -> bool:
    #     start = time.time()
    #     while time.time() - start < 3.0:
    #         QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 1000)
    #         if self.parent.normalPlainTextEditOutput.is_idle or self.parent.tracePlainTextEditOutput.is_idle:
    #             break
    #     return True

    def halt_simulation(self, reason: str = "", extra: str = ""):
        try:
            # TODO: Not clear on whether this is needed or even a good idea.
            self.device.stop_simulation()
        except Exception as e:
            Exception_out(f"While calling `self.device.stop_simulation()` got this error: {e}")
        self.model.stop()
        self.instance.stop()

        # self.model.initialized = False  # model.stop should do this!
        # self.model.running = False      # model.stop should do this!
        self.parent.run_state = RUNNABLE
        self.stop_model_now = True

        self.call_for_display_refresh()

        # just in case these were disabled during the run
        self.parent.enable_view_updates(True)
        self.parent.enable_text_updates(True)

        # _ = self.wait_until_text_outputs_are_idle()  # TODO: DELME

        if not reason:
            Normal_out(f"\n{e_bangbang} Run halted\n")

        Normal_out(extra)

        duration = timeit.default_timer() - self.run_start_time

        msg = (
            f"\n{e_info} {self.rule_files[self.current_rule_index].parameter_string} "
            f"(run took {duration:0.4f} seconds)\n"
        )
        Normal_out(msg)
        Trace_out(msg)

        # For ensuring that all param string versions get run
        #  when done, drop to next section to make sure all files get run!

        if self.last_run_mode == "run_all" and self.raw_device_param_string and reason:
            if self.param_set:
                self.run_all(clear_ui=False)
                return  # don't worry about running other rule files
            else:
                self.device.set_parameter_string(self.raw_device_param_string)
                self.raw_device_param_string = ""
                self.param_set = []

        # For ensuring that all rules in list get run
        if self.last_run_mode == "run_all":
            self.current_rule_index += 1
            if self.current_rule_index < len(self.rule_files):
                next_sim = self.rule_files[self.current_rule_index]
                prev_sim = self.rule_files[self.current_rule_index - 1]
                rule_name = Path(next_sim.rule_file).name
                Normal_out(f"\nRULE FILE: {rule_name} ({self.current_rule_index}/{len(self.rule_files)})\n")

                if next_sim.clear_data:
                    # nothing that this is an odd thing to ask for...what's the point in running
                    # multiple files if you are only going to end up with data from the last one?!
                    self.parent.delete_datafile()

                # NOTE: when not running from script, next_sim.device_file & prev_sim.device_file are both ''
                #       and next_sim.reload_device is False. Thus, this section gets bypassed
                if (next_sim.device_file and next_sim.device_file != prev_sim.device_file) or next_sim.reload_device:
                    if not self.parent.on_load_device(next_sim.device_file, auto_load_rules=False, quiet=True):
                        Normal_out(
                            f"\n{e_boxed_x} Device (re)load failed while running "
                            f"{next_sim.device_file} + {next_sim.rule_file} from script!\n"
                        )
                        self.current_rule_index = 0
                        return

                if next_sim.parameter_string:
                    self.device.set_parameter_string(next_sim.parameter_string)

                if self.compile_rule(next_sim.rule_file):
                    self.run_all()
                else:
                    self.current_rule_index += 1
                    if self.current_rule_index < len(self.rule_files):
                        Normal_out(f"\n{e_boxed_x} Compile Failed for {rule_name}, moving to next rule in list....\n")
                        if self.compile_rule(self.rule_files[self.current_rule_index].rule_file):
                            self.run_all()
                    else:
                        self.current_rule_index = 0
            else:
                self.current_rule_index = 0
