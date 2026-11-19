# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Mixin class providing simulation running functionality for MainWin.
"""

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from PySide6.QtWidgets import QApplication

from epicpy import EPICPY_DEBUG
from epicpy.constants.emoji import emoji_box
from epicpy.constants.state_constants import PAUSED, RUNNABLE, RUNNING
from epicpy.utils import config
from epicpy.utils.app_utils import hcolor
from epiclibcpp.epiclib.output_tee_globals import (
    Debug_out,
    Device_out,
    Exception_out,
    Info_out,
    Normal_out,
    Trace_out,
)
from epiclibcpp.epiclib.pps_globals import PPS_out
from epicpy.epic.parallel_simulation import (
    OutputSettings,
    ParallelRunWorker,
    SimulationConfig,
    SimulationResult,
    create_sim_configs_from_permutations,
    expand_permutations,
    has_permutations,
)
from epicpy.epic.run_info import ParameterGridItem, RunInfo

if TYPE_CHECKING:
    from epicpy.windows.main_window import MainWin


class SimulationMixin:
    """
    Mixin for MainWin providing simulation running functionality.

    Includes methods for:
    - Running simulations (single step, normal, parallel)
    - Parameter grid execution
    - Pause/halt controls
    """

    # Type hints for attributes that exist on MainWin
    if TYPE_CHECKING:
        self: "MainWin"

    def run_one_step(self):
        if self.run_state in (RUNNABLE, PAUSED):
            self.simulation.device.set_parameter_string(config.device_cfg.device_params)
            self.simulation.run_one_step()
        else:
            Info_out(hcolor("WARNING: Unable to complete RunOneStep action because run_state is not RUNNABLE\n", "gold"))

    def run_normal(self, parallel: bool = True):
        """
        Run all permutations of the currently loaded simulation.
        If parallel is True and the device parameter string has permutations like [Easy|Hard],
        then run all permutations in parallel using separate processes. Otherwise, use the
        existing sequential approach.
        """

        # Resume from paused state - just continue without resetting
        if self.run_state == PAUSED:
            self.simulation.run()
            return

        if self.run_state != RUNNABLE:
            Info_out(hcolor("ERROR: Unable to complete RunNormal action because run_state is not RUNNABLE<font>\n", "red"))
            return

        # Check if parameter grid mode is enabled
        if config.device_cfg.use_parameter_grid and config.device_cfg.parameter_grid:
            self._run_with_parameter_grid()
            return

        self.simulation.current_rule_index = 0
        rule_name = Path(self.simulation.rule_files[self.simulation.current_rule_index].rule_file).name
        Normal_out(emoji_box(f"RULE FILE: {rule_name}", line="thick") + "\n")

        # Determine the parameter string to use
        if self.simulation.rule_files[self.simulation.current_rule_index].parameter_string:
            param_string = self.simulation.rule_files[self.simulation.current_rule_index].parameter_string
        elif config.device_cfg.device_params:
            param_string = config.device_cfg.device_params
        else:
            param_string = self.simulation.device.get_parameter_string()

        # Check for permutations in parameter string
        # Use the checkbox state directly as the source of truth for the parallel decision,
        # rather than config.device_cfg.allow_parallel_runs which can get out of sync.
        allow_parallel = parallel and self.actionAllow_Parallel_Runs.isChecked()
        if allow_parallel and has_permutations(param_string):
            self._run_parallel(param_string)
            return

        # Sequential execution (normal serial run)
        param_count = 1 if not has_permutations(param_string) else len(expand_permutations(param_string))
        Info_out(hcolor(f"Running {param_count} parameter permutations serially...\n", bold=True))

        # Delete existing data file if overwrite mode is enabled
        if config.device_cfg.overwrite_data:
            self.delete_datafile()

        QApplication.processEvents()  # Force UI update before blocking call

        self.simulation.device.set_parameter_string(param_string)
        self.simulation.run()

    def _run_parallel(self, param_string: str) -> None:
        """
        Run all parameter permutations in parallel using separate processes.
        Parameter strings are indicated with [option1|option2] syntax.

        The heavy work runs on a background QThread so the UI stays responsive.
        Post-processing happens on the main thread via signal connections.
        """
        rule_file = self.simulation.rule_files[self.simulation.current_rule_index].rule_file
        device_file = config.app_cfg.last_device_file

        # Create configurations for each permutation
        sim_configs = create_sim_configs_from_permutations(
            device_file=device_file,
            rule_file=rule_file,
            base_param_string=param_string,
            output_settings=OutputSettings.from_device_config(config.device_cfg),
            run_command=config.device_cfg.run_command,
            run_command_value=int(config.device_cfg.run_command_value),
            visual_encoder_file=config.device_cfg.visual_encoder,
            auditory_encoder_file=config.device_cfg.auditory_encoder,
        )

        Info_out(hcolor(f"Running {len(sim_configs)} parameter permutations in parallel:\n", bold=True))
        for i, cfg in enumerate(sim_configs, 1):
            Info_out(f"  {i}. {cfg.parameter_string}\n")
        Info_out(hcolor("Please wait...\n", bold=True))

        # Mark UI as running so menus are disabled and status bar updates
        self.run_state = RUNNING

        device_folder = Path(device_file).parent
        self._parallel_worker = ParallelRunWorker(
            sim_configs=sim_configs,
            max_workers=min(len(sim_configs), os.cpu_count() or 4),
            device_folder=device_folder,
            overwrite_data=config.device_cfg.overwrite_data,
        )
        self._parallel_worker.permutation_done.connect(self._on_parallel_permutation_done)
        self._parallel_worker.all_done.connect(self._on_parallel_run_finished)
        self._parallel_worker.start()

    def _on_parallel_permutation_done(self, completed: int, total: int, param_string: str, success: bool):
        """Slot: update status bar as each permutation finishes."""
        status = "ok" if success else "FAILED"
        self.statusBar().showMessage(f"Parallel Run: {completed}/{total} complete  ({param_string}: {status})")

    def _on_parallel_run_finished(self, results: list[SimulationResult]):
        """Slot: all parallel permutations are done - restore UI and display results."""
        was_stopped = self._parallel_worker is not None and self._parallel_worker._stop_event.is_set()

        # Clean up worker reference
        self._parallel_worker = None

        # Restore default Output_tee routing
        for ot in (Normal_out, Debug_out, Device_out, Exception_out, PPS_out):
            ot.clear_py_streams()
            ot.add_py_stream(self.normalTextOutput)
            if EPICPY_DEBUG:
                ot.add_py_stream(sys.stdout)  # for debug
        Exception_out.add_py_stream(sys.stderr)
        Trace_out.clear_py_streams()
        Trace_out.add_py_stream(self.traceTextOutput)

        # Move cached output_tee contents where they belong
        if results:
            self._emit_outputs_from_parallel_run(results=tuple(results))

        # Report results
        if was_stopped:
            Info_out(hcolor(f"\nParallel run stopped by user ({len(results)} of permutations completed).\n", "gold"))
        else:
            Info_out("\nParallel execution complete. Results:\n")
        for result in results:
            status = hcolor("SUCCESS", "green", paragraph=False) if result.success else hcolor("FAILED", "red", paragraph=False)
            Info_out(f"  [{status}] {result.sim_config.parameter_string}")
            if result.success:
                Info_out(f" -> Simulated time: {result.simulated_time_ms}ms, Wall time: {result.run_time_seconds:.2f}s")
            else:
                Info_out(f" -> Error: {result.error_message}\n")

        # Restore Info_out routing (kept separate until above messages are emitted)
        Info_out.clear_py_streams()
        Info_out.add_py_stream(self.infoTextOutput)
        Info_out(f"\nParallel Run {'Stopped' if was_stopped else 'Finished'}!\n")

        # Show updated graph
        try:
            html = self.simulation.device.show_output_stats()
            self.stats_win.setHtml(html)
        except Exception as e:
            msg = f"""
                <span style="color: red;">
                <h2>Unable to render analysis for
                {self.simulation.device.get_name() if self.simulation.has_device else "Current Device"}
                </h2>:<br><b>{str(e)}</b>
                </span>
                """
            self.stats_win.setHtml(msg)
            Info_out(msg)

        # Save output logs if enabled
        self._save_output_logs()

        # Restore run state so UI becomes interactive again
        self.run_state = RUNNABLE

    def _emit_outputs_from_parallel_run(
        self, results: tuple[SimulationResult, ...], mode: Literal["All Runs", "Last Run"] = "Last Run"
    ):
        _mode = mode if mode in ["All Runs", "Last Run"] else "Last Run"
        from collections import deque
        from itertools import chain

        if _mode == "All Runs":
            start = 0  # All output
        else:
            start = -1  # Output from last run only

        self.normalTextOutput.load(deque(chain.from_iterable(result.outputs["Normal_out"] for result in results[start:])))
        self.traceTextOutput.load(deque(chain.from_iterable(result.outputs["Trace_out"] for result in results[start:])))

    def _run_with_parameter_grid(self):
        """
        Run simulations according to the parameter grid.
        Respects the Allow Parallel Runs setting.
        """
        # Build list of enabled grid items with non-empty parameter strings
        grid_items = [
            ParameterGridItem.from_dict(item)
            for item in config.device_cfg.parameter_grid
            if item.get("enabled", True) and item.get("parameter_string", "").strip()
        ]

        if not grid_items:
            Info_out(hcolor("WARNING: No enabled rows with parameter strings in parameter grid. Nothing to run.\n", "gold"))
            return

        # Get current rule file for comparison
        current_rule = self.simulation.rule_files[0].rule_file if self.simulation.rule_files else ""

        # Check if parallel runs are allowed
        allow_parallel = self.actionAllow_Parallel_Runs.isChecked()

        if allow_parallel and len(grid_items) > 1:
            self._run_grid_parallel(grid_items, current_rule)
        else:
            self._run_grid_sequential(grid_items, current_rule)

    def _run_grid_parallel(self, grid_items: list, current_rule: str):
        """Run parameter grid items in parallel."""
        device_file = config.app_cfg.last_device_file

        # Create SimulationConfig for each grid item, expanding any permutations
        sim_configs = []
        for item in grid_items:
            rule_file = current_rule if item.rule_file == "*" else item.rule_file
            # Expand permutations in the parameter string (e.g., [P1|P2|P3] -> 3 configs)
            item_configs = create_sim_configs_from_permutations(
                device_file=device_file,
                rule_file=rule_file,
                base_param_string=item.parameter_string,
                output_settings=OutputSettings.from_device_config(config.device_cfg),
                run_command=config.device_cfg.run_command,
                run_command_value=int(config.device_cfg.run_command_value),
                visual_encoder_file=config.device_cfg.visual_encoder,
                auditory_encoder_file=config.device_cfg.auditory_encoder,
            )
            sim_configs.extend(item_configs)

        # Build output message (use <br> for line breaks since Info_out renders HTML)
        lines = [hcolor(f"Running {len(sim_configs)} parameter grid configurations in parallel:<br>", bold=True)]
        for i, cfg in enumerate(sim_configs, 1):
            rule_name = Path(cfg.rule_file).stem if cfg.rule_file else "(current)"
            lines.append(f"&nbsp;&nbsp;{i}. Rule: {rule_name}, Params: {cfg.parameter_string}<br>")
        lines.append(hcolor("Please wait...<br>", bold=True))
        Info_out("".join(lines))

        # Mark UI as running so menus are disabled and status bar updates
        self.run_state = RUNNING

        device_folder = Path(device_file).parent
        self._parallel_worker = ParallelRunWorker(
            sim_configs=sim_configs,
            max_workers=min(len(sim_configs), os.cpu_count() or 4),
            device_folder=device_folder,
            overwrite_data=config.device_cfg.overwrite_data,
        )
        self._parallel_worker.permutation_done.connect(self._on_parallel_permutation_done)
        self._parallel_worker.all_done.connect(self._on_parallel_run_finished)
        self._parallel_worker.start()

    def _run_grid_sequential(self, grid_items: list, current_rule: str):
        """Run parameter grid items sequentially."""
        # Delete existing data file if overwrite mode is enabled (once at start)
        if config.device_cfg.overwrite_data:
            self.delete_datafile()

        # Convert grid items to RunInfo objects for existing batch run infrastructure
        run_infos = []
        for item in grid_items:
            rule_file = current_rule if item.rule_file == "*" else item.rule_file
            run_infos.append(
                RunInfo(
                    from_script=False,
                    device_file="",
                    rule_file=rule_file,
                    parameter_string=item.parameter_string,
                    clear_data=False,  # Respect overwrite_data setting already applied
                    reload_device=False,
                )
            )

        # Log what we're about to run (use <br> for line breaks since Info_out renders HTML)
        lines = [hcolor(f"Running {len(run_infos)} parameter grid configurations sequentially:<br>", bold=True)]
        for i, ri in enumerate(run_infos, 1):
            rule_name = Path(ri.rule_file).stem if ri.rule_file else "(current)"
            lines.append(f"&nbsp;&nbsp;{i}. Rule: {rule_name}, Params: {ri.parameter_string}<br>")
        Info_out("".join(lines))

        # Set up the rule_files list and start the run
        self.simulation.rule_files = run_infos
        self.simulation.current_rule_index = 0

        # Compile and run the first rule
        first_rule = run_infos[0].rule_file
        rule_name = Path(first_rule).name if first_rule else "(current)"
        Normal_out(emoji_box(f"RULE FILE: {rule_name}", line="thick") + "\n")

        if first_rule and first_rule != current_rule:
            # Need to compile a different rule
            if not self.simulation.compile_rule(first_rule):
                Info_out(hcolor(f"ERROR: Failed to compile {rule_name}\n", "red"))
                return

        # Set the parameter string and run
        self.simulation.device.set_parameter_string(run_infos[0].parameter_string)
        self.simulation.run()

    def run_next_cycle(self):
        self.simulation.run_next_cycle()

    def pause_simulation(self):
        self.simulation.pause_simulation()

    def halt_simulation(self):
        self.simulation.halt_simulation(reason="user_stop", force=True)
