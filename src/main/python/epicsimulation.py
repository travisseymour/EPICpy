"""
This file is part of EPICpy, Created by Travis L. Seymour, PhD.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with EPICpy.
If not, see <https://www.gnu.org/licenses/>.
"""

import re
from typing import Optional
from pathlib import Path
import sys
import weakref
import timeit

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog

from apputils import LIBNAME, unpack_param_string
from cppinclude import epiclib_include
import cppyy

from encoderpassthru import NullVisualEncoder, NullAuditoryEncoder
from stateconstants import *
from emoji import *
from dialogs.loggingwindow import LoggingSettingsWin
import modulereloader
from loguru import logger as log
import config
from plum import dispatch  # keep here to ensure it gets pulled in, needed for devices

# ------------------------------------------------------
# Load Various Include files and objects we will need
# The location of the library depends on OS, this is
# figured out in main.py which sets apputils.LIBNAME
# so that the correct library can be loaded when this
# module is imported.
# ------------------------------------------------------

cppyy.load_library(LIBNAME)

epiclib_include("Model-View Classes/View_base.h")
epiclib_include("Model-View Classes/Model.h")
epiclib_include("Framework classes/Output_tee_globals.h")
epiclib_include("Framework classes/Device_base.h")
epiclib_include("Framework classes/Device_exception.h")
epiclib_include("Framework classes/Device_processor.h")
epiclib_include("Framework classes/Human_base.h")
epiclib_include("Framework classes/Human_processor.h")
epiclib_include("Framework classes/Parameter.h")
epiclib_include("Framework classes/Coordinator.h")
epiclib_include("Framework classes/Processor.h")
epiclib_include("Utility Classes/Symbol.h")
epiclib_include("Utility Classes/Output_tee.h")
epiclib_include("Utility Classes/Statistics.h")
epiclib_include("Standard_Symbols.h")
epiclib_include("PPS/PPS Interface classes/PPS_globals.h")
epiclib_include("Framework classes/Device_event_types.h")
epiclib_include("Motor Classes/Manual_actions.h")
epiclib_include("Motor Classes/Manual_processor.h")

from cppyy.gbl import Model
from cppyy.gbl import Coordinator
from cppyy.gbl import Normal_out


class Simulation:
    def __init__(self, parent, context):
        self.parent = parent
        self.ctx = context

        self.device = None
        self.model = None
        self.visual_encoder = None
        self.auditory_encoder = None

        self.tempmod_path: Path = None
        self.tempenc_v_path: Path = None
        self.tempenc_a_path: Path = None

        self.instance = Coordinator.get_instance()
        self.stop_model_now = False

        self.keep_checking_run = False
        self.run_start_time = 0
        self.run_time = 0
        self.run_time_limit = 0
        self.run_timer = QTimer()
        self.rule_files = []
        self.last_run_mode = ""
        self.current_rule_index = 0
        self.last_update_time = timeit.default_timer()
        self.default_device_parameters = ""

        self.steps_since_last_text_out = 0
        self.steps_run = 0

        self.write = self.parent.write

        self.raw_device_param_string = ""
        self.param_set = []

    def call_for_display_refresh(self):
        current_time = self.instance.get_time()
        if config.device_cfg.display_refresh in ("after_each_step", "continuously"):
            self.parent.update_views(current_time)
        elif config.device_cfg.display_refresh == "after_every_sec":
            if timeit.default_timer() - self.last_update_time >= float(
                config.device_cfg.run_command_value
            ):
                self.parent.update_views(current_time)
                self.last_update_time = timeit.default_timer()
        # ** if 'never_during_run' then this function does nothing

    def call_for_text_update(self, force: bool = False):
        if config.device_cfg.text_refresh == "after_each_step":
            if (
                force
                or self.steps_since_last_text_out
                >= config.device_cfg.text_refresh_value
            ):
                self.parent.dump_cache()
                self.parent.trace_win.dump_cache()

                self.steps_since_last_text_out = 0
            else:
                self.steps_since_last_text_out += 1

        # note: if text_refresh was 'continuously', there is no caching and so no need
        # to update anything here if text_refresh was 'none_during_run', caching is
        # supposed to stay on until the entire run is over

    def update_model_output_settings(self):
        # set some output and tracing options
        try:
            self.model.set_output_run_messages(config.device_cfg.output_run_messages)
            self.model.set_output_run_memory_contents(
                config.device_cfg.output_run_memory_contents
            )
            self.model.set_output_run_details(config.device_cfg.output_run_details)
            self.model.set_output_compiler_messages(
                config.device_cfg.output_compiler_messages
            )
            self.model.set_output_compiler_details(
                config.device_cfg.output_compiler_details
            )

            self.model.set_trace_manual(config.device_cfg.trace_manual)
            self.model.set_trace_cognitive(config.device_cfg.trace_cognitive)
            self.model.set_trace_visual(config.device_cfg.trace_visual)
            self.model.set_trace_auditory(config.device_cfg.trace_auditory)
            self.model.set_trace_ocular(config.device_cfg.trace_ocular)
            self.model.set_trace_vocal(config.device_cfg.trace_vocal)
            self.model.set_trace_temporal(config.device_cfg.trace_temporal)
            self.model.set_trace_device(config.device_cfg.trace_device)
        except Exception as e:
            self.write(
                emoji_box(
                    f"ERROR: Failed to update EPIC output or trace settings:\n"
                    f"{e}",
                    line="thick",
                )
            )

    def on_load_device(self, file: str = "", quiet: bool = False):

        if not file:
            if Path(config.device_cfg.device_file).is_file():
                start_dir = Path(config.device_cfg.device_file).parent
            elif Path(config.app_cfg.last_device_file).is_file():
                start_dir = Path(config.app_cfg.last_device_file).parent
            else:
                start_dir = str(Path.home())
            device_file, _ = QFileDialog.getOpenFileName(
                None,
                "Choose EPICpy Device File",
                str(start_dir),
                "Python Files (*.py)",
            )
        else:
            device_file = file

        if device_file:

            # save existing device config if necessary
            if config.device_cfg.device_file:
                config.save_config(quiet=True)

            # load config for this device, or create new device on if none exists already
            dark_mode = config.app_cfg.dark_mode
            current = config.device_cfg.current

            config.get_device_config(Path(device_file))
            config.device_cfg.device_file = device_file

            config.app_cfg.dark_mode = dark_mode
            config.device_cfg.current = current

            # save global app config in case we need last_device_file
            config.app_cfg.last_device_file = device_file
            config.save_app_config(quiet=True)

            if not config.device_cfg.normal_out_file:
                config.device_cfg.normal_out_file = (
                    LoggingSettingsWin.default_log_filename("normal")
                )
            if not config.device_cfg.trace_out_file:
                config.device_cfg.trace_out_file = (
                    LoggingSettingsWin.default_log_filename("trace")
                )
            if not config.device_cfg.stats_out_file:
                config.device_cfg.stats_out_file = (
                    LoggingSettingsWin.default_log_filename("stats")
                )

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
            try:
                assert self.tempmod_path and self.tempmod_path.is_file()
                self.tempmod_path.unlink()
            except AssertionError:
                # no file to delte
                ...
            except IOError as e:
                self.write(
                    f"ERROR: Unable to alter files on the path "
                    f"{str(self.tempmod_path.parent)} ({e})."
                )
            except Exception as e:
                log.error(
                    f"ERROR while trying to unlink file {str(self.tempmod_path)}: {e}"
                )

            # these will be handy
            device_file_p = Path(device_file)
            device_file_root = device_file_p.parent

            # make sure __init__.py exists in device folder
            if not Path(device_file_root, "__init__.py").is_file():
                self.write(
                    f'{e_info} Unable to find "__init__.py" in device folder '
                    f"({str(device_file_root)}). Will attempt to create one."
                )
                try:
                    Path(device_file_root, "__init__.py").write_text("")
                except IOError:
                    self.write(
                        emoji_box(
                            f'ERROR: Unable to create needed file \n'
                            f'"{str(Path(device_file_root, "__init__.py"))}".\n'
                            f'If your device does not load correctly, you may need to\n'
                            f'obtain write access to the device folder.',
                            line="thick",
                        )
                    )

            # Must add parent folder to python path
            sys.path.append(str(device_file_p.parent))

            # Optionally try to add grandparent folder too, helps if you have bases
            # in folder above the one the device is in, but we shouldn't require it.
            try:
                sys.path.append(str(device_file_p.parent.parent))
            except:
                ...

            # - to construct an import statement, the module name must be known.
            #   this expression copies the device code to a known file
            self.tempmod_path = Path(device_file_p.parent, "tempmod.py")
            try:
                assert self.tempmod_path and self.tempmod_path.is_file()
                self.tempmod_path.unlink()
            except AssertionError:
                # no file to delete
                ...
            except IOError as e:
                self.write(
                    f"ERROR: Unable to alter files on the path "
                    f"{str(self.tempmod_path.parent)} ({e})."
                )
            except Exception as e:
                log.error(
                    f"ERROR while trying to unlink file {str(self.tempmod_path)}: {e}"
                )
            device_code = device_file_p.read_text()

            try:
                assert device_code.strip(), "Device file appears to be empty!"
                pattern = r"class EpicDevice *\( *.*EpicPyDevice *\) *\:"
                regex_error = (
                    "Unable to find class EpicDevice subclassed from "
                    "EpicPyDevice or epicpy_device.EpicPyDevice"
                )
                assert re.findall(pattern, device_code), regex_error
                self.tempmod_path.write_text(device_code)
            except AssertionError as e:
                self.write(
                    emoji_box(
                        f"ERROR: Failed to create new EpicDevice from\n"
                        f"{device_file_p.name}!\n"
                        f"{e}",
                        line="thick",
                    )
                )
                self.device = None
                return
            except IOError as e:
                self.write(
                    f"ERROR: Unable to write to file\n"
                    f"{str(self.tempmod_path.parent)}:\n"
                    f"{e}"
                )
            except Exception as e:
                log.error(
                    f"ERROR while trying to write to file "
                    f"{str(self.tempmod_path)}: {e}"
                )

            # - now we can attempt to import the EpicDevice class from this module
            try:
                # despite appearances, BOTH of the following lines are required if we
                # want a device reload to pull any changes that have occurred since
                # starting EPICpy!
                import tempmod

                modulereloader.reset_module(tempmod)

                if not quiet:
                    self.write(
                        f"{e_info} loading device code from {device_file_p.name}..."
                    )

                self.device = tempmod.EpicDevice(
                    ot=Normal_out,
                    parent=self.parent,
                    device_folder=device_file_p.parent,
                )
                self.device.__release_gil__ = (
                    True  # no idea if this does anything at all!?
                )
                if not quiet:
                    self.write(
                        f"{e_info} found EpicDevice class, creating new device instance "
                        f"based on this class."
                    )
                self.write(
                    f"\n{e_boxed_check} {self.device.device_name} device was created "
                    f"successfully."
                )

                # must store default device params before we reload one from settings
                if hasattr(self.device, "condition_string"):
                    self.default_device_parameters = str(self.device.condition_string)
                else:
                    self.default_device_parameters = ""

                # restore layout for device
                device_layout_file = Path(device_file_p.parent, "layout.json")
                if device_layout_file.is_file():
                    self.parent.manage_z_order = False
                    self.parent.layout_load(str(device_layout_file))
                    self.parent.manage_z_order = True

                # restore params for device
                if config.device_cfg.device_params:
                    self.device.set_parameter_string(config.device_cfg.device_params)

            except Exception as e:
                self.write(
                    emoji_box(
                        f"ERROR: Failed to create new EpicDevice from\n"
                        f"{device_file_p.name}!\n"
                        f"{e}",
                        line="thick",
                    )
                )
                self.device = None
                return

            try:
                assert self.device.get_device_proc_ptr()
            except AssertionError:
                self.write(
                    emoji_box(
                        f"ERROR: Created new device, but access to "
                        f"device_processor_pointer failed!",
                        line="thick",
                    )
                )
                self.device = None
                return

            # create new model and connect it to the new device
            try:
                # suggested in Model::connect_device_to_human, but may not be
                #  necessary in Python
                try:
                    self.model.device_ptr = None
                    self.model.device_processor_ptr = None
                except:  # FIXME: Seriously? Why would setting these to None fail??
                    pass
                # actually create a new model, we're passing in the new device
                #  (different than EpicCLI approach)
                self.model = Model(self.device)
                self.model.__release_gil__ = True
                assert self.model, "Error creating new Model() with device."

                # now connect everything up
                self.model.device_processor_ptr = self.device.get_device_proc_ptr()

                assert (
                    self.model.device_processor_ptr
                ), "Failed to get valid device_proc_ptr"
                self.model.device_processor_ptr.connect(self.model.get_human_ptr())
                assert (
                    self.model.device_processor_ptr
                ), "Failed to connect device_proc_ptr to human_ptr"
                # NOTE: Keep the note below so no one is temped to mirror what's going
                # on in dkepic here self.model.get_human_ptr().
                #   connect(self.model.get_device_processor_ptr()) # <--don't do this!!!!!
                # This is the only way that works vvv
                self.model.get_human_ptr().connect(self.model.device_processor_ptr)
                assert (
                    self.model.get_human_ptr()
                ), "Failed to connect human_ptr back to device_ptr"

                self.update_model_output_settings()

                self.write(f"{e_boxed_check} Model successfully initialized.")
            except Exception as e:
                self.write(
                    emoji_box(
                        f"ERROR: Unable to properly connect new device and model:\n"
                        f"{e}",
                        line="thick",
                    )
                )
                self.device = None
                return

            self.parent.update_title()
            if not quiet:
                self.write(
                    f"{e_boxed_check} Successfully initialized device: {device_file}."
                )

            if self.device and self.model.get_compiled():
                self.parent.run_state = RUNNABLE
                if hasattr(self.device, "rule_filename"):
                    self.device.rule_filename = Path(self.model.get_prs_filename()).name
            else:
                self.parent.run_state = UNREADY

            self.parent.update_views(self.instance.get_time())

    def get_encoder_file(self, kind: str) -> str:
        assert kind in ("Visual", "Auditory")
        prev_encoder = (
            config.device_cfg.visual_encoder
            if kind == "Visual"
            else config.device_cfg.auditory_encoder
        )
        encoder = Path(prev_encoder).parent
        if prev_encoder and encoder.is_dir():
            if not str(encoder) == ".":
                start_dir = encoder
            else:
                start_dir = Path(config.device_cfg.device_file).parent
        elif (
            config.device_cfg.device_file
            and Path(config.device_cfg.device_file).parent.is_dir()
        ):
            start_dir = Path(config.device_cfg.device_file).parent
        else:
            start_dir = str(Path.home())

        encoder_file, _ = QFileDialog.getOpenFileName(
            None,
            f"Choose EPICpy {kind} Encoder File",
            str(start_dir),
            "Python Files (*.py)",
        )
        return encoder_file

    def on_unload_encoder(self, kind: str):
        assert kind in ("Auditory", "Visual")
        encoder = self.visual_encoder if kind == "Visual" else self.auditory_encoder

        if not encoder:
            self.write(
                f"Failed to unload {kind} encoder..."
                f"none appears to be currently loaded."
            )
            return
        else:
            self.write(f"Attempting to unload {kind} encoder...")

        # go ahead and save now. Unlike in on_load_encoder(), we do this first.
        # If unload fails, it will still be effectively unloaded on session reload.

        if kind == "Visual":
            config.device_cfg.visual_encoder = ""
        else:
            config.device_cfg.auditory_encoder = ""

        try:
            assert self.model, (
                f"{e_bangbang} Model doesn't appear to be initialized...has a "
                f"device been loaded??!!"
            )
            if kind == "Visual":
                self.visual_encoder = NullVisualEncoder("NullVisualEncoder", self)
                self.model.get_human_ptr().set_visual_encoder_ptr(self.visual_encoder)
            else:
                # note "aditory" spelling is from C++ code. When the spelling
                # gets fixed there, will fix it here!
                self.auditory_encoder = NullAuditoryEncoder("NullAuditoryEncoder", self)
                self.model.get_human_ptr().set_aditory_encoder_ptr(
                    self.auditory_encoder
                )
        except Exception as e:
            self.write(
                emoji_box(
                    f"ERROR: Unable to unload {kind} encoder!\n"
                    f"[{e}]\n"
                    f"However, it won't be loaded the next time this device is loaded.",
                    line="thick",
                )
            )
            if kind == "Visual":
                self.visual_encoder = None
            else:
                self.auditory_encoder = None
            # self.device = None  # NOTE: This was enabled, but seems too hard?!

        self.parent.update_title()

        config.save_config(quiet=True)

        self.write(f"{e_boxed_check} {kind} encoder successfully unloaded.")

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

            sys.path.append(str(encoder_file_p.parent))
            # - to construct an import statement, the module name must be known.
            #   this expression copies the device code to a known file
            if kind == "Visual":
                self.tempenc_v_path = Path(encoder_file_p.parent, "tempvenc.py")
            else:
                self.tempenc_a_path = Path(encoder_file_p.parent, "tempaenc.py")

            try:
                encoder_code = encoder_file_p.read_text()
                assert encoder_code.strip(), "Encoder appears to be empty!"
                if kind == "Visual":
                    pattern = r"class VisualEncoder *" \
                              r"\( *(Visual_encoder_base|EPICPyVisualEncoder) *\) *\:"
                    regex_error = (
                        "Unable to find class VisualEncoder subclassed from "
                        "Visual_encoder_base"
                    )
                    assert re.findall(pattern, encoder_code), regex_error
                    self.tempenc_v_path.write_text(encoder_code)
                else:
                    pattern = (
                        r"class AuditoryEncoder *"
                        r"\( *(Auditory_encoder_base|EPICPyAuditoryEncoder) *\) *\:"
                    )
                    regex_error = (
                        "Unable to find class AuditoryEncoder subclassed from "
                        "Auditory_encoder_base"
                    )
                    assert re.findall(pattern, encoder_code), regex_error
                    self.tempenc_a_path.write_text(encoder_code)
            except Exception as e:
                self.write(
                    emoji_box(
                        f"ERROR: Failed to create new {kind} encoder from\n"
                        f"{encoder_file_p.name}:\n"
                        f"{e}",
                        line="thick",
                    )
                )
                if kind == "Visual":
                    self.visual_encoder = None
                    config.device_cfg.visual_encoder = ""
                else:
                    self.auditory_encoder = None
                    config.device_cfg.auditory_encoder = ""
                return

            # - now we can attempt to import the VisualEncoder or AuditoryEncoder class
            #   from this module
            try:
                # despite appearances, BOTH of the following lines are required if we
                # want an encoder reload to pull any changes that have occurred since
                # starting EPICpy!
                if kind == "Visual":
                    import tempvenc as tempenc
                else:
                    import tempaenc as tempenc

                modulereloader.reset_module(tempenc)

                if not quiet:
                    self.write(
                        f"{e_info} loading encoder from {encoder_file_p.name}..."
                    )

                if kind == "Visual":
                    self.visual_encoder = tempenc.VisualEncoder(
                        encoder_file_p.stem.replace("_", " ").title(), self
                    )
                else:
                    self.auditory_encoder = tempenc.AuditoryEncoder(
                        encoder_file_p.stem.replace("_", " ").title(), self
                    )

                if kind == "Visual":
                    setattr(self.visual_encoder, "write", self.write)
                else:
                    setattr(self.auditory_encoder, "write", self.write)

                if not quiet:
                    self.write(
                        f"{e_info} found {kind}Encoder class, "
                        f"creating new encoder instance based on this class..."
                    )
                self.write(f"{e_boxed_check} {kind}encoder was created successfully.")
            except Exception as e:
                self.write(
                    emoji_box(
                        f"ERROR: Failed to create new {kind}Encoder from\n"
                        f"{encoder_file_p.name}:"
                        f"{e}",
                        line="thick",
                    )
                )
                if kind == "Visual":
                    self.visual_encoder = None
                    config.device_cfg.visual_encoder = ""
                else:
                    self.auditory_encoder = None
                    config.device_cfg.auditory_encoder = ""
                # self.device = None  # NOTE: This was enabled, but seems too harsh?!
                return

            try:
                assert self.model, (
                    f"{e_bangbang} Model doesn't appear to be initialized...has a "
                    f"device been loaded??!!"
                )
                if kind == "Visual":
                    self.model.get_human_ptr().set_visual_encoder_ptr(
                        self.visual_encoder
                    )
                else:
                    # (*) note "aditory" spelling is from C++ code. When the spelling
                    # gets fixed there, will fix it here!
                    self.model.get_human_ptr().set_aditory_encoder_ptr(  # (*)
                        self.auditory_encoder
                    )
            except Exception as e:
                self.write(
                    emoji_box(
                        f"ERROR: Created new {kind} encoder, but connection to\n"
                        f"Human_processor failed:\n"
                        f"{e}",
                        line="thick",
                    )
                )
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

            config.save_config(quiet=True)

    def recompile_rules(self):
        self.current_rule_index = 0
        if self.rule_files and Path(self.rule_files[self.current_rule_index]).is_file():
            self.write(
                f"{e_info} Recompiling {self.rule_files[self.current_rule_index]}..."
            )
            self.compile_rule(self.rule_files[self.current_rule_index])
        else:
            self.write(
                emoji_box(
                    f"ERROR: Rule recompile failed because former rule file no longer\n"
                    f"exists or is not readable.",
                    line="thick",
                )
            )
            self.parent.ui.actionRecompile_Rules.setEnabled(False)

    def choose_rules(self, files: Optional[list] = None):
        """
        Select EPIC prs rule file(s) from disk
        """

        if files:
            note = "reloaded"
            rule_files = [str(Path(file).resolve()) for file in files]
        else:
            note = "selected"
            if (
                config.device_cfg.device_file
                and Path(config.device_cfg.device_file).parent.is_dir()
            ):
                start_dir = Path(config.device_cfg.device_file).parent
            else:
                start_dir = str(Path.home())

            rule_files = QFileDialog.getOpenFileNames(
                None,
                "Choose 1 or More EPIC RuleSet Files",
                str(start_dir),
                "Rule files (*.prs)",
            )[0]
        if rule_files:
            self.rule_files = rule_files
            self.rule_files = sorted(self.rule_files)
            self.current_rule_index = 0

            # go ahead and save in case we need cfg.rule_files
            config.device_cfg.rule_files = rule_files
            config.save_config(quiet=True)
            endl = "\n"
            self.write(
                f"\n{len(self.rule_files)} ruleset files {note}:\n"
                f"{endl.join(Path(rule_file).name for rule_file in self.rule_files)}\n"
            )
            self.write(
                f"{e_info} Attempting to compile first rule in {note} ruleset list..."
                if len(rule_files) > 1
                else f"{e_info} Attempting to compile {note} ruleset..."
            )
            self.compile_rule(self.rule_files[self.current_rule_index])
        else:
            self.rule_files = []
            self.write(f"{e_boxed_x} No valid rule file(s) {note}.")

    def compile_rule(self, file: str = "") -> bool:
        rule_path = Path(file)

        try:
            # try to compile rule
            self.model.set_prs_filename(file)
            result = self.model.compile()
        except Exception as e:
            self.write(
                emoji_box(
                    f"ERROR: Unable to compile ruleset file\n{rule_path.name}:\n"
                    f"{e}",
                    line="thick",
                )
            )
            result = False

        if result:
            self.write(
                f"Rule file {rule_path.name} compiled successfully!"
            )
            self.parent.update_title()
            rule_compiled = True
        else:
            self.write(
                emoji_box(
                    f"ERROR: Unable to (re)compile ruleset file\n"
                    f"{rule_path.name}!",
                    line="thick",
                )
            )
            rule_compiled = False

        # make sure run state reflects result of rule compile attempt
        if self.device and self.model.get_compiled():
            self.parent.run_state = RUNNABLE

            if hasattr(self.device, "rule_filename"):
                self.device.rule_filename = Path(
                    str(self.model.get_prs_filename())
                ).name
        else:
            self.parent.run_state = UNREADY

        return rule_compiled

    def run_one_step(self):
        # just in case output settings were changed between runs
        self.update_model_output_settings()

        self.last_run_mode = "run_one_step"
        try:
            # self.parent.write_plain('\n')
            self.instance.run_for(50)
            self.call_for_display_refresh()
            self.call_for_text_update()

            run_result = self.device.state != self.device.SHUTDOWN
            self.run_time = self.model.get_time()
        except Exception as e:
            run_result = False
            self.write(emoji_box(f"ERROR:\n"
                                 f"{e}", line="thick"))
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
            self.write(
                emoji_box(
                    f"ERROR: Unable to run simulation because model is not yet RUNNABLE\n"
                    f"(device successfully loaded and rules successfully compiled)",
                    line="thick",
                )
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
            )

            # model.initialize() isn't working, but the only critical part is getting
            # done elsewhere is instance (i.e. Coordinator.get_instance() initialization.
            self.instance.initialize()

            # call encoder initializers
            if self.visual_encoder:
                self.visual_encoder.initialize()
            if self.auditory_encoder:
                self.auditory_encoder.initialize()

            self.model.initialized = True
            self.model.running = True
            if config.device_cfg.describe_parameters:
                self.model.get_human_ptr().describe_parameters(Normal_out)
                self.write("\n")

            self.write(emoji_box("\nSIMULATION STARTING\n", line="double"))

            device_param_str = self.device.get_parameter_string()

            if "[" in device_param_str:
                self.raw_device_param_string = device_param_str
                self.param_set = unpack_param_string(device_param_str)

            if self.param_set:
                current_param = self.param_set.pop()
                self.device.set_parameter_string(current_param)

            if config.device_cfg.run_command == "run_for":
                self.run_time_limit = self.run_time + int(
                    config.device_cfg.run_command_value
                )
            elif config.device_cfg.run_command == "run_until":
                self.run_time_limit = int(config.device_cfg.run_command_value)
            elif config.device_cfg.run_command == "run_for_cycles":
                self.run_time_limit = (
                    self.run_time + int(config.device_cfg.run_command_value) * 50
                )
            elif config.device_cfg.run_command == "run_until_done":
                self.run_time_limit = sys.maxsize
            else:
                self.write(
                    f"{e_info} WARNING: unexpected run command found in config file "
                    f' ("{config.device_cfg.run_command}"), using "RUN_UNTIL_DONE" '
                    f"instead."
                )

        elif self.parent.run_state == PAUSED:

            if config.device_cfg.run_command in ("run_for", "run_for_cycles"):
                # go again if we ran for the specified amount of time or we paused
                #   and then changed
                if self.run_time >= self.run_time_limit:
                    self.run_time_limit = self.run_time + int(
                        config.device_cfg.run_command_value
                    )
                elif config.device_cfg.run_command == "run_until":
                    # are we past the specified time or did we pause and change from
                    #   run until done?
                    if self.run_time >= config.device_cfg.run_command_value:
                        self.write(
                            "{e_info} Unable to run additional steps, RUN_UNTIL_TIME "
                            "value already reached!"
                        )
                    self.run_time_limit = 0
                    return
                else:
                    self.run_time_limit = 0

        self.write(f"\nRun Started...\n")
        self.parent.run_state = RUNNING

        disable_views = config.device_cfg.display_refresh == "none_during_run"
        self.parent.enable_view_updates(not disable_views)
        disable_text = config.device_cfg.text_refresh in (
            "after_each_step",
            "none_during_run",
        )
        self.parent.enable_text_updates(not disable_text)

        self.steps_run = 0
        self.run_start_time = timeit.default_timer()
        self.run_timer.singleShot(
            config.device_cfg.step_time_delay, self.run_next_cycle
        )

    def run_next_cycle(self):

        if self.parent.run_state != RUNNING:
            return

        try:
            # self.parent.write_plain('\n')
            self.instance.run_for(50)
            self.call_for_display_refresh()
            self.call_for_text_update()

            run_result = self.device.state != self.device.SHUTDOWN
            self.run_time = self.model.get_time()
            self.steps_run += 1
        except Exception as e:
            run_result = False
            self.write(
                emoji_box(
                    f"ERROR: Run of\n"
                    f"{self.device.rule_filename}\n"
                    f"Stopped With Error:\n"
                    f"{e}",
                    line="thick",
                )
            )
            self.write(e)
            self.halt_simulation("error")
            return

        if self.instance.is_paused():
            # this is presumably because of a rule with a break state set
            self.parent.run_state = PAUSED
            self.write(f"{e_info} Run of {self.device.rule_filename} Paused.")

        if run_result and (
            (
                config.device_cfg.run_command in ("run_for", "run_until")
                and self.run_time < self.run_time_limit
            )
            or (config.device_cfg.run_command == "run_until_done")
            or config.device_cfg.run_command == "run_for_cycles"
            and self.steps_run < config.device_cfg.run_command_value
        ):
            # *** Still running, keep going
            self.run_timer.singleShot(
                config.device_cfg.step_time_delay, self.run_next_cycle
            )
        else:
            # *** Running seems to be done, shut it down
            self.parent.run_state = PAUSED if run_result else RUNNABLE
            if self.parent.run_state == PAUSED:
                self.pause_simulation()
                if config.device_cfg.run_command == "run_for_cycles":
                    self.steps_run = 0
            elif self.parent.run_state == RUNNABLE:
                self.write(f"{e_boxed_ok} Run of {self.device.rule_filename} Finished.")
                self.halt_simulation("finished")

    def pause_simulation(self):
        if self.parent.run_state == RUNNING:
            self.parent.run_state = PAUSED

        self.call_for_display_refresh()
        self.call_for_text_update(force=True)

        # just in case these were disabled during the run
        self.parent.enable_view_updates(True)
        self.parent.enable_text_updates(True)

        self.write(f"{e_info} Run paused\n", copy_to_trace=True)

    def halt_simulation(self, reason: str = ""):

        self.model.stop()

        self.model.initialized = False
        self.model.running = False
        self.parent.run_state = RUNNABLE
        self.stop_model_now = True

        self.call_for_display_refresh()
        self.call_for_text_update(force=True)

        # just in case these were disabled during the run
        self.parent.enable_view_updates(True)
        self.parent.enable_text_updates(True)

        if not reason:
            self.write(f"{e_bangbang} Run halted\n")

        self.write("", copy_to_trace=True)

        duration = timeit.default_timer() - self.run_start_time
        self.write(f"{e_info} (run took {duration:0.4f} seconds)")

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
                rule_name = Path(self.rule_files[self.current_rule_index]).name
                self.write(
                    emoji_box(
                        f"RULE FILE: {rule_name} "
                        f"({self.current_rule_index}/{len(self.rule_files)})"
                    )
                )
                if self.compile_rule(self.rule_files[self.current_rule_index]):
                    self.run_all()
                else:
                    self.current_rule_index += 1
                    if self.current_rule_index < len(self.rule_files):
                        self.write(
                            f"\n{e_boxed_x} Compile Failed for {rule_name}, "
                            f"moving to next rule in list....\n"
                        )
                        if self.compile_rule(self.rule_files[self.current_rule_index]):
                            self.run_all()
                    else:
                        self.current_rule_index = 0
            else:
                self.current_rule_index = 0
