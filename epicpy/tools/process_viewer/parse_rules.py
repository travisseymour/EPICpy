# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

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
