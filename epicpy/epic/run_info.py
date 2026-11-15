# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass


@dataclass
class RunInfo:
    from_script: bool = False
    device_file: str = ""
    rule_file: str = ""
    parameter_string: str = ""
    clear_data: bool = False
    reload_device: bool = False
