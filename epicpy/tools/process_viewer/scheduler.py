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

"""
Scheduler module for processing EPIC trace events and building process timeline data.

Given a set of parse rules and trace lines, creates a schedule of processor activities
for visualization in a timeline graph.
"""

import re
from collections.abc import Iterable
from typing import List

import pandas as pd


def ms_to_timestamp(ms: int, date_str: str = "1977-01-01") -> str:
    """
    Convert milliseconds to timestamp string.

    Example:
        ms_to_timestamp(100)  -> '1977-01-01 00:00:00.100'
        ms_to_timestamp(1500) -> '1977-01-01 00:00:01.500'
    """
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{date_str} {hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


class Scheduler:
    """
    Processes trace event lines according to parsing rules and builds a DataFrame
    of processor activity periods (start/finish times).
    """

    def __init__(
        self,
        rules: List[tuple],
        time_scale: float = 1.0,
        flash_delay_ms: int = 100,
        reset_signal: str = "",
    ):
        """
        Initialize the scheduler.
        """
        self.rules: List[tuple] = rules
        self.time_scale: float = float(time_scale)
        self.flash_delay_ms: float = float(flash_delay_ms) * self.time_scale
        self.flash_delay_sec: float = self.flash_delay_ms / 1000
        self.reset_signal = reset_signal
        self.ongoing_processes: dict[str, str] = {}  # {processor: start_ts}

        # Initialize DataFrame with proper columns
        self.processes = pd.DataFrame(columns=["Processor", "Start", "Finish"])
        self.has_new_data: bool = False

    @property
    def process_count(self) -> int:
        return len(self.processes.index)

    def process_lines(self, lines: Iterable[str]):
        """
        Process all lines from an iterable (e.g., deque).
        """
        for line in lines:
            self.process_event_text(line)

    def process_event_text(self, event_text: str):
        """
        Process a single event text line and update the process schedule.

        Produces processor activity records based on matching rules:
        - FLASH: Creates a complete period (start + flash_delay_ms)
        - ON: Records start of an ongoing process
        - OFF: Completes an ongoing process with the current time
        """
        _event_text = event_text.strip()

        if self.reset_signal and self.reset_signal in _event_text:
            self.processes = self.processes[0:0]
            self.ongoing_processes = {}

        if _event_text and re.search(r"^[1-9][\d]*:", _event_text):
            sim_time_ms = int(_event_text.split(":")[0])

            for a_rule in self.rules:
                t_line = re.sub(r":\d+", ":", _event_text.replace("'", ""))
                condition, action = a_rule
                hit_list = [a_string in t_line for a_string in condition]

                if False not in hit_list:
                    for act in action:
                        event, processor = act.split(" ")

                        if event == "FLASH":
                            # Entire period known, add it to process list
                            new_data = {
                                "Processor": processor,
                                "Start": ms_to_timestamp(sim_time_ms),
                                "Finish": ms_to_timestamp(int(sim_time_ms + self.flash_delay_ms)),
                            }

                            # Check for duplicates
                            if not self._is_duplicate(new_data):
                                self.processes.loc[self.process_count] = new_data
                                self.has_new_data = True

                        elif event == "ON":
                            # Only start is known, store for later
                            if processor not in self.ongoing_processes:
                                self.ongoing_processes[processor] = ms_to_timestamp(sim_time_ms)

                        elif event == "OFF":
                            # Complete an ongoing process
                            if processor in self.ongoing_processes:
                                new_data = {
                                    "Processor": processor,
                                    "Start": self.ongoing_processes[processor],
                                    "Finish": ms_to_timestamp(int(sim_time_ms)),
                                }

                                if not self._is_duplicate(new_data):
                                    self.processes.loc[self.process_count] = new_data

                                del self.ongoing_processes[processor]
                                self.has_new_data = True

    def _is_duplicate(self, new_data: dict) -> bool:
        """Check if the new data already exists in the DataFrame."""
        if self.processes.empty:
            return False
        return (
            (self.processes["Processor"] == new_data["Processor"])
            & (self.processes["Start"] == new_data["Start"])
            & (self.processes["Finish"] == new_data["Finish"])
        ).any()
