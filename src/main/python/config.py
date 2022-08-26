"""
This file is part of EPICpy.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar.
If not, see <https://www.gnu.org/licenses/>.
"""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, fields

from loguru import logger as log

"""
Global Configuration Variable
"""


@dataclass
class AppConfig:
    """Class for keeping track of device-independent EpicPy config info"""

    config_version: str = "20211023"

    last_device_file: str = ""  # for reloading last session
    dark_mode: bool = False
    epiclib_version: str = (
        ""  # if not "", passes this value to DeviceConfig on app init
    )
    font_name: str = "Consolas"  # default, user can change to whatever they want
    font_size: int = 14
    dialog_size: dict = field(default_factory=dict)  # hold dialog sizes if changed
    main_geom: list = field(default_factory=list)  # does nothing yet
    auto_load_last_device: bool = (
        False  # only True when changing epiclib_version from UI
    )
    text_editor: str = "BUILT-IN"


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

    # will hold temporary config data, will not be saved to config file
    current: dict = field(default_factory=dict)


device_cfg = DeviceConfig()  # *** Global Device Configuration ***
app_cfg = AppConfig()  # *** Global App Configuration ***

"""
Dataclass Utilities
"""


def replace_config(new_items: dict):
    """
    Given a dict of config keys and values (most likely from reading a dict in from a
    json file), update global_device_config by a) starting with a fresh DeviceConfig and
    copying any relevant keys and values from new_items.
    """
    # https://stackoverflow.com/questions/57962873
    global device_cfg
    device_cfg = DeviceConfig()
    for _field in fields(DeviceConfig):
        try:
            setattr(device_cfg, _field.name, new_items[_field.name])
        except KeyError:
            pass


def replace_app_config(new_items: dict):
    """
    Given a dict of config keys and values (most likely from reading a dict in from a
    json file), update global_app_config by a) starting with a fresh AppConfig and
    copying any relevant keys and values from new_items.
    """
    # https://stackoverflow.com/questions/57962873
    global app_cfg
    app_cfg = AppConfig()
    for _field in fields(AppConfig):
        try:
            setattr(app_cfg, _field.name, new_items[_field.name])
        except KeyError:
            pass


"""
Configuration File Management
"""


def get_app_config():
    global app_cfg
    config_dir = Path("~", ".config", "epicpy").expanduser()
    config_file = Path(config_dir, "global_config.json")

    try:
        config = json.loads(config_file.read_text())

        try:
            # make sure config is new enough
            cfg_ver = config["config_version"]
            assert str(cfg_ver).isdigit()
            assert int(cfg_ver) >= 20211023

            # ok to merge loaded loaded values into default config
            replace_app_config(config)
        except (AssertionError, KeyError):
            log.info(
                "Substantial changes have been made to the EPICpy configuration format. "
                "The entire configuration will be replaced with default values in the "
                "new format."
            )
            app_cfg = AppConfig()

    except FileNotFoundError:
        # Problem? Just use the defaults.
        log.info(
            f'Unable to find global app file "global_config.json" in {str(config_dir)}, '
            f"using defaults."
        )
        app_cfg = AppConfig()


def save_app_config(quiet: bool = False) -> bool:
    config_dir = Path("~", ".config", "epicpy").expanduser()
    config_file = Path(config_dir, "global_config.json")

    try:
        config_file.write_text(json.dumps(app_cfg.__dict__, indent=4))
        return True
    except Exception as e:
        if not quiet:
            log.error(
                f'ERROR attempting to read app configuration file "{config_file.name}" to '
                f'"{str(config_dir)}: {e}"'
            )
        return False


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

            # ok to merge loaded loaded values into default config
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


def save_config(quiet: bool = False):

    if not device_cfg.device_file:
        return

    device = Path(device_cfg.device_file)
    device_folder = device.parent
    device_name = device.stem.strip().replace(" ", "_")
    device_config_file = f"{device_name}_config.json"

    cfg = {
        key: value for key, value in device_cfg.__dict__.items() if not key == "current"
    }

    try:
        Path(device_folder, device_config_file).write_text(json.dumps(cfg, indent=4))
        return True
    except Exception as e:
        if not quiet:
            log.error(
                f"Unable to write updated config file to "
                f"{str(Path(device_folder, device_config_file))}:\n{e}"
            )
        return False
