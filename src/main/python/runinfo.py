from dataclasses import dataclass


@dataclass
class RunInfo:
    from_script: bool = False
    device_file: str = ''
    rule_file: str = ''
    parameter_string: str = ''
    clear_data: bool = False
    reload_device: bool = False