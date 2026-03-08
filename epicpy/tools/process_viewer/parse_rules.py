"""
This file is part of the EPICpy source code. EPICpy is a tool for simulating
human performance tasks using the EPIC computational cognitive architecture
(David Kieras and David Meyer 1997a) using the Python programming language.
Copyright (C) 2022-2026 Travis L. Seymour, PhD

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

"""
Parse rule management module for Process Viewer.

Loads and translates parse rules that define how trace output lines
map to processor activity visualizations.

Rule format example:
    "Human:Cognitive:Motor update, add clause, Manual, Punch, Started = ON Keyboard, ON Hands"

Translated to:
    (("Human:Cognitive:Motor update", "add clause", "Manual", "Punch", "Started"), ("ON Keyboard", "ON Hands"))
"""

from pathlib import Path
from typing import List, Optional

from loguru import logger as log


def load_rules(file_path: str | Path) -> List[str]:
    """
    Load rules from the specified file.
    """
    try:
        temp_rules = Path(file_path).read_text().splitlines(keepends=False)
        return temp_rules
    except IOError as e:
        log.error(f"Unable to load trace file parse rules from {str(Path(file_path))}: {e}")
        return []


def clean_rules(rules: List[str]) -> List[str]:
    """
    Remove comments and blank lines from rule list.
    """
    _rules = [rule.strip() for rule in rules]
    return [rule for rule in _rules if rule and not rule.startswith("#")]


def load_parse_rules(file_path: str | Path) -> List[str]:
    """
    Load and clean parse rules from a file.
    """
    rules = load_rules(file_path)
    cleaned_rules = clean_rules(rules)
    return cleaned_rules


def translate(rules: List[str]) -> Optional[List[tuple]]:
    """
    Translate raw rule strings to a list of (conditions, actions) tuples.
    """
    output = []

    for rule in rules:
        rule = rule.strip(" ")
        try:
            conditions, actions = rule.split(" = ")
            conditions = tuple(word.strip() for word in conditions.split(", "))
            actions = tuple(word.strip() for word in actions.split(", "))
        except ValueError:
            log.error(f'Error: Rule "{rule}" lacks proper "[condition] = [action]" structure.')
            return None

        output.append((conditions, actions))

    return output
