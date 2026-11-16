# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass
class RuleEvent:
    trial: int
    delay_ms: int
    post_stim_ms: int | None  # None renders as "-"
    rule_name: str
    cycle: int
    adds: list[str] = field(default_factory=list)
    deletes: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)


@dataclass
class _FiredRule:
    """Accumulator for a single rule firing during pass 1."""

    name: str
    adds: list[str] = field(default_factory=list)
    deletes: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)


@dataclass
class TrialData:
    trial_number: int
    events: list[RuleEvent] = field(default_factory=list)


STIMULUS_ONSET_LABEL = "**STIMULUS ONSET**"
RESPONSE_MADE_LABEL = "**RESPONSE MADE**"

DEFAULT_TRIAL_START_RULE = "TRIAL_mfg"
DEFAULT_STIMULUS_ONSET_CLAUSE = r"\(Visual Stimulus.* Detection Onset\)"
DEFAULT_RESPONSE_CLAUSE = r"\(Motor (Manual|Vocal) .* Started\)"


def parse_normal_output_lines(
    lines: Iterable[str],
    trial_start_rule: str = DEFAULT_TRIAL_START_RULE,
    stimulus_onset_clause: str = DEFAULT_STIMULUS_ONSET_CLAUSE,
    response_clause: str = DEFAULT_RESPONSE_CLAUSE,
) -> list[TrialData]:
    """Parse EPIC normal-output-window trace lines and return per-trial rule maps.

    This version works directly with an iterable of lines (e.g., from MemLargeTextView.lines)
    instead of reading from a file.
    """

    cycle_re = re.compile(r"^(\d+):Cycle (\d+):\s*(.*)")
    fire_re = re.compile(r"^\*\*\* Fire: (.+)")
    add_re = re.compile(r"^\s+Add: (.+)")
    del_re = re.compile(r"^\s+Delete: (.+)")
    cmd_re = re.compile(r"^\s+Command: (.+)")
    stim_re = re.compile(stimulus_onset_clause)
    resp_re = re.compile(response_clause)

    # --- pass 1: split the file into per-cycle records ---
    CycleRecord = tuple[int, int, list[_FiredRule], bool, bool]
    cycles: list[CycleRecord] = []

    cur_time: int | None = None
    cur_cycle: int | None = None
    cur_rules: list[_FiredRule] = []
    cur_rule: _FiredRule | None = None  # most recently fired rule
    cur_has_stim = False
    cur_has_resp = False
    cur_body_lines: list[str] = []

    def _flush() -> None:
        nonlocal cur_has_stim, cur_has_resp, cur_rule
        if cur_time is None:
            return
        for bl in cur_body_lines:
            if not cur_has_stim and stim_re.search(bl):
                cur_has_stim = True
            if not cur_has_resp and resp_re.search(bl):
                cur_has_resp = True
        assert cur_cycle is not None
        cycles.append((cur_time, cur_cycle, cur_rules, cur_has_stim, cur_has_resp))
        cur_rule = None

    for line in lines:
        m = cycle_re.match(line)
        if m:
            _flush()
            cur_time = int(m.group(1))
            cur_cycle = int(m.group(2))
            cur_rules = []
            cur_rule = None
            cur_has_stim = False
            cur_has_resp = False
            cur_body_lines = []
            remainder = m.group(3).strip()
            if remainder and remainder != "No rules fired":
                cur_body_lines.append(remainder)
        else:
            if cur_time is not None:
                fm = fire_re.match(line)
                if fm:
                    cur_rule = _FiredRule(name=fm.group(1).strip())
                    cur_rules.append(cur_rule)
                elif cur_rule is not None:
                    am = add_re.match(line)
                    if am:
                        cur_rule.adds.append(am.group(1).strip())
                        continue
                    dm = del_re.match(line)
                    if dm:
                        cur_rule.deletes.append(dm.group(1).strip())
                        continue
                    cm = cmd_re.match(line)
                    if cm:
                        cur_rule.commands.append(cm.group(1).strip())
                        continue
                    cur_body_lines.append(line)
                else:
                    cur_body_lines.append(line)

    _flush()  # last cycle

    # --- pass 2: group into trials and build events ---
    trials: list[TrialData] = []
    trial_num = 0
    trial_start_time: int | None = None  # reset to each trial's own start
    stim_onset_delay: int | None = None
    stim_found = False
    resp_found = False

    for time_ms, cycle_num, rules, has_stim, has_resp in cycles:
        rule_names = [r.name for r in rules]

        # detect trial boundary
        if trial_start_rule in rule_names:
            trial_num += 1
            trial_start_time = time_ms
            stim_onset_delay = None
            stim_found = False
            resp_found = False
            trials.append(TrialData(trial_number=trial_num))

        if trial_num == 0 or trial_start_time is None:
            continue

        trial = trials[-1]
        delay = time_ms - trial_start_time

        # stimulus onset pseudo-event (first match this trial)
        if has_stim and not stim_found:
            stim_found = True
            stim_onset_delay = delay
            trial.events.append(
                RuleEvent(
                    trial=trial_num,
                    delay_ms=delay,
                    post_stim_ms=None,
                    rule_name=STIMULUS_ONSET_LABEL,
                    cycle=cycle_num,
                )
            )

        # real rules
        for fr in rules:
            post_stim: int | None = None
            if stim_found and stim_onset_delay is not None:
                post_stim = delay - stim_onset_delay
            trial.events.append(
                RuleEvent(
                    trial=trial_num,
                    delay_ms=delay,
                    post_stim_ms=post_stim,
                    rule_name=fr.name,
                    cycle=cycle_num,
                    adds=list(fr.adds),
                    deletes=list(fr.deletes),
                    commands=list(fr.commands),
                )
            )

        # response pseudo-event (first match this trial)
        if has_resp and not resp_found:
            resp_found = True
            post_stim = None
            if stim_onset_delay is not None:
                post_stim = delay - stim_onset_delay
            trial.events.append(
                RuleEvent(
                    trial=trial_num,
                    delay_ms=delay,
                    post_stim_ms=post_stim,
                    rule_name=RESPONSE_MADE_LABEL,
                    cycle=cycle_num,
                )
            )

    return trials
