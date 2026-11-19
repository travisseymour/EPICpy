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


@dataclass
class ParameterGridItem:
    """Single row in the parameter grid for batch runs."""

    rule_file: str = "*"  # "*" = use current rule, otherwise full path to .prs file
    parameter_string: str = ""
    enabled: bool = True

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage."""
        return {
            "rule_file": self.rule_file,
            "parameter_string": self.parameter_string,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ParameterGridItem":
        """Deserialize from dictionary."""
        return cls(
            rule_file=data.get("rule_file", "*"),
            parameter_string=data.get("parameter_string", ""),
            enabled=data.get("enabled", True),
        )
