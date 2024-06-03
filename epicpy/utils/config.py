"""
This file is part of EPICpy.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with EPICpy.
If not, see <https://www.gnu.org/licenses/>.
"""

import os
import json
from pathlib import Path
import platform
from typing import Optional
from dataclasses import dataclass, field, fields

from loguru import logger as log

SAVE_CONFIG_ON_UPDATE: bool = True

device_cfg: Optional["DeviceConfig"] = None
app_cfg: Optional["AppConfig"] = None

"""
Global Configuration Variable
"""


@dataclass
class AppConfig:
    """Class for keeping track of device-independent EpicPy config info"""

    config_version: str = "20211023"

    last_device_file: str = ""  # for reloading last session
    last_script_file: str = ""
    dark_mode: str = "Light"  # in ('Light', 'Dark', 'Auto')
    epiclib_version: str = ""  # if not "", passes this value to DeviceConfig on app init
    font_name: str = "Fira Mono"  # default, user can change to whatever they want
    font_size: int = 12
    dialog_size: dict = field(default_factory=dict)  # hold dialog sizes if changed
    main_geom: list = field(default_factory=list)  # does nothing yet
    auto_load_last_device: bool = False  # only True when changing epiclib_version from UI
    text_editor: str = ""  # defaults to BUILT-IN editor
    config_file: str = ""

    # will hold temporary config data, will not be saved to config file
    current: dict = field(default_factory=dict)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        global SAVE_CONFIG_ON_UPDATE
        if SAVE_CONFIG_ON_UPDATE:
            self.save_config()

    def save_config(self) -> bool:
        global app_cfg
        if app_cfg is None:
            return False

        if not hasattr(self, "config_file") or self.config_file == "":
            config_dir = get_config_dir()
            self.config_file = str(Path(config_dir, "global_config.json").resolve())

        cfg = {key: value for key, value in app_cfg.__dict__.items() if not key == "current"}

        try:
            self.current["last_config"] = cfg
        except:
            ...

        try:
            Path(self.config_file).write_text(json.dumps(cfg, indent=4))
            return True
        except Exception as e:
            log.error(f'ERROR attempting to write to app configuration file @ "{str(self.config_file)}": {e}')
            return False

    def rollback(self) -> bool:
        if "last_config" not in self.current:
            return False

        try:
            replace_app_config(self.current["last_config"])
            del self.current["last_config"]
            return True
        except Exception as e:
            log.error(f"Unable to rollback app config, '{e}'")
            return False


@dataclass
class DeviceConfig:
    """Class for keeping track of EpicPy configuration"""

    config_version: str = "20211023"

    device_file: str = ""
    rule_files: list = field(default_factory=list)
    epiclib_version: str = ""

    auto_load_last_encoders: str = "ask"
    visual_encoder: str = ""
    auditory_encoder: str = ""

    log_normal_out: bool = False
    log_trace_out: bool = False
    normal_out_file: str = ""
    trace_out_file: str = ""
    stats_out_file: str = ""

    run_command: str = "run_until_done"
    run_command_value: float = 1.0
    display_refresh: str = "after_each_step"
    text_refresh: str = "after_each_step"
    display_refresh_value: float = 1.0
    text_refresh_value: float = 2.0

    trace_visual: bool = False
    trace_auditory: bool = False
    trace_cognitive: bool = True
    trace_ocular: bool = False
    trace_manual: bool = False
    trace_vocal: bool = False
    trace_temporal: bool = False
    trace_device: bool = True
    trace_pps: bool = True

    output_compiler_messages: bool = False
    output_compiler_details: bool = False
    output_run_messages: bool = True
    output_run_details: bool = False
    output_run_memory_contents: bool = True

    sound_text_kind: bool = True
    sound_text_stream: bool = False
    sound_text_timbre: bool = True
    sound_text_loudness: bool = False

    speech_text_kind: bool = True
    speech_text_stream: bool = False
    speech_text_pitch: bool = False
    speech_text_loudness: bool = False
    speech_text_content: bool = True
    speech_text_speaker: bool = False
    speech_text_gender: bool = False

    step_time_delay: int = 0
    setting_run_for_real_secs: int = 5
    setting_run_until_msecs: int = 600
    setting_run_cycles: int = 1
    setting_refresh_secs: float = 1.0
    device_params: str = ""

    spatial_scale_degree: int = 10
    calibration_grid: bool = False
    center_dot: bool = False
    describe_parameters: bool = False
    allow_device_images: bool = False

    device_config_file: str = ""

    # will hold temporary config data, will not be saved to config file
    current: dict = field(default_factory=dict)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        global SAVE_CONFIG_ON_UPDATE
        if SAVE_CONFIG_ON_UPDATE:
            self.save_config()

    def save_config(self):
        global device_cfg
        if device_cfg is None or not self.device_file:
            return

        # NOTE: it's important that this get recomputed every time!
        device = Path(self.device_file)
        device_folder = device.parent
        device_name = device.stem.strip().replace(" ", "_")
        device_config_file = f"{device_name}_config.json"

        cfg = {key: value for key, value in device_cfg.__dict__.items() if not key == "current"}

        try:
            self.current["last_config"] = cfg
        except:
            ...

        try:
            Path(device_folder, device_config_file).write_text(json.dumps(cfg, indent=4))
            return True
        except Exception as e:
            log.error(
                f"Unable to write updated config file to " f"{str(Path(device_folder, device_config_file))}:\n{e}"
            )
            return False

    def rollback(self) -> bool:
        if "last_config" not in self.current:
            return False

        try:
            replace_config(self.current["last_config"])
            del self.current["last_config"]
            return True
        except Exception as e:
            log.error(f"Unable to rollback device config, '{e}'")
            return False


"""
Dataclass Utilities
"""


def replace_config(new_items: dict):
    """
    Given a dict of config keys and values (most likely from reading a dict in from a
    json file), update global_device_config by (a) starting with a fresh DeviceConfig and
    copying any relevant keys and values from new_items.
    """
    # https://stackoverflow.com/questions/57962873
    global device_cfg, SAVE_CONFIG_ON_UPDATE
    SAVE_CONFIG_ON_UPDATE = False
    device_cfg = DeviceConfig()
    try:
        for _field in fields(DeviceConfig):
            try:
                setattr(device_cfg, _field.name, new_items[_field.name])
            except KeyError:
                pass
    finally:
        SAVE_CONFIG_ON_UPDATE = True


def replace_app_config(new_items: dict):
    """
    Given a dict of config keys and values (most likely from reading a dict in from a
    json file), update global_app_config by (a) starting with a fresh AppConfig and
    copying any relevant keys and values from new_items.
    """
    # https://stackoverflow.com/questions/57962873
    global app_cfg, SAVE_CONFIG_ON_UPDATE
    SAVE_CONFIG_ON_UPDATE = False
    app_cfg = AppConfig()
    try:
        for _field in fields(AppConfig):
            try:
                setattr(app_cfg, _field.name, new_items[_field.name])
            except KeyError:
                pass
    finally:
        SAVE_CONFIG_ON_UPDATE = True


"""
Configuration File Management
"""


def get_config_dir() -> Path:
    if platform.system() == "Windows":
        config_dir = Path(Path().home(), "Documents", "epicpy")
    else:
        config_dir = Path("~", ".config", "epicpy").expanduser()
    try:
        # just in case this is the very first run, create the config folder
        config_dir.mkdir(exist_ok=True)
    except Exception as err:
        config_dir = Path().home().expanduser()
        print(f"WARNING: Unable to create config folder at {str(config_dir)}: {err}!")
        print(f"         Using {config_dir} instead.")

    return config_dir


def get_app_config():
    global app_cfg
    config_dir = get_config_dir()
    config_file = Path(config_dir, "global_config.json")

    try:
        cfg = json.loads(config_file.read_text())

        try:
            # make sure config is new enough
            cfg_ver = cfg["config_version"]
            assert str(cfg_ver).isdigit()
            assert int(cfg_ver) >= 20211023

            # ok to merge loaded values into default config
            replace_app_config(cfg)
        except (AssertionError, KeyError):
            log.info(
                "Substantial changes have been made to the EPICpy configuration format. "
                "The entire configuration will be replaced with default values in the "
                "new format."
            )
            app_cfg = AppConfig()

    except FileNotFoundError:
        # Problem? Just use the defaults.
        log.info(f'Unable to find global app file "global_config.json" in {str(config_dir)}, ' f"using defaults.")
        app_cfg = AppConfig()


def get_device_config(device: Optional[Path]):
    global device_cfg

    if device is None:
        device_cfg = DeviceConfig()
        return

    device_folder = device.parent
    device_name = device.stem.strip().replace(" ", "_")
    device_config_file = f"{device_name}_config.json"

    try:
        config = json.loads(Path(device_folder, device_config_file).read_text())

        try:
            # make sure config is new enough
            cfg_ver = config["config_version"]
            assert str(cfg_ver).isdigit()
            assert int(cfg_ver) >= 20211023

            # ok to merge loaded values into default config
            replace_config(config)
        except (AssertionError, KeyError):
            log.info(
                "Substantial changes have been made to the EPICpy device configuration "
                "format. The entire configuration will be replaced with default values "
                "in the new format."
            )
            current = device_cfg.current
            device_cfg = DeviceConfig(current=current)
    except FileNotFoundError:
        log.info(
            f"ERROR: Unable to find device configuration file "
            f'"{device_config_file}" in "{str(device_folder)}". '
            f"Creating default configuration instead."
        )
        current = device_cfg.current
        device_cfg = DeviceConfig(current=current)
