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
Parallel simulation execution for running multiple parameter permutations concurrently.

Each simulation runs in a separate process with its own epiclibcpp globals,
ensuring complete isolation of the Coordinator singleton and output streams.
"""

import multiprocessing
import os
import tempfile
from typing import Literal

# Set to True to force 'spawn' start method on Linux (matching Windows/macOS behavior).
# This helps catch pickling issues during development that would otherwise only appear
# on Windows/macOS. Set to False to use the platform default.
CHECK_MAC_WIN_MP = False

if CHECK_MAC_WIN_MP:
    try:
        multiprocessing.set_start_method("spawn", force=False)
    except RuntimeError:
        pass  # Already set
from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import psutil

# Default to physical cores - 1, minimum of 2
_DEFAULT_MAX_WORKERS = max(2, (psutil.cpu_count(logical=False) or 4) - 1)

from epiclibcpp.epiclib import Model

from epicpy.utils.param_utils import unpack_param_string

# Module-level temp directory
_session_temp_dir: tempfile.TemporaryDirectory | None = None


def _get_session_temp_dir() -> Path:
    """Get or create the session-level temp directory for parallel data files."""
    global _session_temp_dir
    if _session_temp_dir is None:
        _session_temp_dir = tempfile.TemporaryDirectory(prefix="epicpy_parallel_")
    return Path(_session_temp_dir.name)


@dataclass
class OutputSettings:
    """Output and trace settings for parallel simulation runs.

    This is a copy of the relevant settings from DeviceConfig, passed explicitly
    to worker processes to avoid importing the config module (which would pull in Qt).
    """

    output_run_messages: bool = True
    output_run_memory_contents: bool = True
    output_run_details: bool = False
    output_compiler_messages: bool = False
    output_compiler_details: bool = False
    trace_manual: bool = False
    trace_cognitive: bool = True
    trace_visual: bool = False
    trace_auditory: bool = False
    trace_ocular: bool = False
    trace_vocal: bool = False
    trace_temporal: bool = False
    trace_device: bool = True

    @classmethod
    def from_device_config(cls, device_cfg) -> "OutputSettings":
        """Create OutputSettings from a DeviceConfig object."""
        return cls(
            output_run_messages=device_cfg.output_run_messages,
            output_run_memory_contents=device_cfg.output_run_memory_contents,
            output_run_details=device_cfg.output_run_details,
            output_compiler_messages=device_cfg.output_compiler_messages,
            output_compiler_details=device_cfg.output_compiler_details,
            trace_manual=device_cfg.trace_manual,
            trace_cognitive=device_cfg.trace_cognitive,
            trace_visual=device_cfg.trace_visual,
            trace_auditory=device_cfg.trace_auditory,
            trace_ocular=device_cfg.trace_ocular,
            trace_vocal=device_cfg.trace_vocal,
            trace_temporal=device_cfg.trace_temporal,
            trace_device=device_cfg.trace_device,
        )


def _update_model_output_settings(model: Model, settings: OutputSettings):
    # set some output and tracing options
    model.set_output_run_messages(settings.output_run_messages)
    model.set_output_run_memory_contents(settings.output_run_memory_contents)
    model.set_output_run_details(settings.output_run_details)
    model.set_output_compiler_messages(settings.output_compiler_messages)
    model.set_output_compiler_details(settings.output_compiler_details)

    model.set_trace_manual(settings.trace_manual)
    model.set_trace_cognitive(settings.trace_cognitive)
    model.set_trace_visual(settings.trace_visual)
    model.set_trace_auditory(settings.trace_auditory)
    model.set_trace_ocular(settings.trace_ocular)
    model.set_trace_vocal(settings.trace_vocal)
    model.set_trace_temporal(settings.trace_temporal)
    model.set_trace_device(settings.trace_device)


class DequeStream:
    """A stream-like object that appends to a deque for capturing output.

    Text is buffered until a newline is found, ensuring only complete lines
    are added to the deque. Call flush() to push any remaining partial text.
    """

    def __init__(self):
        self.deque: deque[str] = deque()
        self._partial_text: str = ""  # Buffer for text without trailing newline

    def write(self, text: str):
        """Append text to the deque, buffering partial lines until newline received."""
        if not text:
            return

        # Prepend any buffered partial text
        if self._partial_text:
            text = self._partial_text + text
            self._partial_text = ""

        # Split keeping line endings to identify partial lines
        lines = text.splitlines(keepends=True)

        for line in lines:
            if line.endswith(("\n", "\r")):
                # Complete line - strip the line ending and add to deque
                self.deque.append(line.rstrip("\r\n"))
            else:
                # Partial line (no newline at end) - buffer it
                self._partial_text = line

    def flush(self):
        """Flush any partial text to the deque."""
        if self._partial_text:
            self.deque.append(self._partial_text)
            self._partial_text = ""

    def close(self):
        pass


@dataclass
class SimulationConfig:
    """Configuration for a single parallel simulation run."""

    device_file: str
    rule_file: str
    parameter_string: str
    output_settings: OutputSettings
    run_command: str = "run_until_done"
    run_command_value: int = 0
    visual_encoder_file: str = ""
    auditory_encoder_file: str = ""
    temp_data_dir: str = ""  # Temp directory for isolated data output


@dataclass
class SimulationResult:
    """Results from a single parallel simulation run."""

    sim_config: SimulationConfig
    success: bool
    error_message: str = ""
    outputs: dict[str, deque] = field(default_factory=dict)
    run_time_seconds: float = 0.0
    simulated_time_ms: int = 0
    data_file: str = ""  # Path to the temp data file produced by this run


def _setup_output_routing() -> dict[str, DequeStream]:
    """
    Set up output routing for a worker process.

    Returns a dict mapping output names to their DequeStream instances.
    """
    # import epiclibcpp.epiclib.output_tee_globals as outputs
    from epiclibcpp.epiclib.output_tee_globals import (
        Debug_out,
        Device_out,
        Exception_out,
        Info_out,
        Normal_out,
        Stats_out,
        Trace_out,
    )
    from epiclibcpp.epiclib.pps_globals import PPS_out

    streams = {
        "Normal_out": DequeStream(),
        "Trace_out": DequeStream(),
        "Debug_out": DequeStream(),
        "Stats_out": DequeStream(),
        "Info_out": DequeStream(),
    }

    # Route Normal_out, Debug_out, Device_out, Exception_out, and PPS_out to the same Normal_out stream
    normal_stream = streams["Normal_out"]
    for tee in [Normal_out, Debug_out, Device_out, Exception_out, PPS_out]:
        tee.clear_py_streams()
        tee.add_py_stream(normal_stream)

    # Route Trace_out separately
    Trace_out.clear_py_streams()
    Trace_out.add_py_stream(streams["Trace_out"])

    # Route Stats_out separately
    Stats_out.clear_py_streams()
    Stats_out.add_py_stream(streams["Stats_out"])

    # Route Info_out separately
    Info_out.clear_py_streams()
    Info_out.add_py_stream(streams["Info_out"])

    return streams


def _load_encoder(encoder_file: str, kind: Literal["Visual", "Auditory"], output_stream) -> tuple:
    """
    Load an encoder from a file, or return a null encoder if no file is provided.
    Returns tuple of (encoder_instance, status_message)
    """
    import importlib
    import sys

    from epicpy.epic.encoder_passthru import NullAuditoryEncoder, NullVisualEncoder

    if not encoder_file:
        # No encoder file provided, use null encoder
        if kind == "Visual":
            return NullVisualEncoder("NullVisualEncoder", None), f"{kind}: No file provided, using null encoder"
        else:
            return NullAuditoryEncoder("NullAuditoryEncoder", None), f"{kind}: No file provided, using null encoder"

    encoder_path = Path(encoder_file)
    if not encoder_path.is_file():
        # File doesn't exist, fall back to null encoder
        if kind == "Visual":
            return NullVisualEncoder("NullVisualEncoder", None), f"{kind}: File not found: {encoder_file}"
        else:
            return NullAuditoryEncoder("NullAuditoryEncoder", None), f"{kind}: File not found: {encoder_file}"

    # Add encoder directory to path
    encoder_dir = str(encoder_path.parent)
    if encoder_dir not in sys.path:
        sys.path.insert(0, encoder_dir)

    try:
        # Import the encoder module
        mod = importlib.import_module(encoder_path.stem)
        mod = importlib.reload(mod)

        # Create encoder instance
        encoder_name = encoder_path.stem.replace("_", " ").title()
        if kind == "Visual":
            encoder = mod.VisualEncoder(encoder_name)
        else:
            encoder = mod.AuditoryEncoder(encoder_name)

        # Set the write attribute for output
        setattr(encoder, "write", output_stream)

        return encoder, f"{kind}: Loaded {encoder_path.name} successfully"
    except Exception as e:
        # Fall back to null encoder on any error
        if kind == "Visual":
            return NullVisualEncoder("NullVisualEncoder", None), f"{kind}: FAILED to load {encoder_file}: {e}"
        else:
            return NullAuditoryEncoder("NullAuditoryEncoder", None), f"{kind}: FAILED to load {encoder_file}: {e}"


def run_single_simulation(sim_config: SimulationConfig) -> SimulationResult:
    """
    Run a single simulation in an isolated process.

    This function is designed to be called via ProcessPoolExecutor.
    Each worker process gets its own copy of epiclibcpp with independent
    global state (Coordinator singleton, output streams, etc.).
    """
    import sys
    import timeit

    # Set matplotlib to non-GUI backend BEFORE any imports that might pull it in.
    # This prevents Qt initialization in worker processes (epicpydevicelib imports matplotlib).
    import matplotlib

    matplotlib.use("Agg")

    # Set up output capture first
    streams = _setup_output_routing()

    result = SimulationResult(
        sim_config=sim_config,
        success=False,
        outputs={name: stream.deque for name, stream in streams.items()},
    )

    try:
        # Import here so each process loads its own epiclibcpp
        from epiclibcpp.epiclib import Coordinator, Model, set_auditory_encoder_ptr, set_visual_encoder_ptr
        from epiclibcpp.epiclib.output_tee_globals import Normal_out

        from epicpy.utils.module_reloader import make_device

        # Load the device
        device_path = Path(sim_config.device_file)
        if not device_path.is_file():
            result.error_message = f"Device file not found: {sim_config.device_file}"
            return result

        # Add device directory to path
        device_dir = str(device_path.parent)
        if device_dir not in sys.path:
            sys.path.insert(0, device_dir)

        # Reset coordinator BEFORE creating device (Device registers Device_processor on creation)
        instance = Coordinator.get_instance()
        instance.reset()

        # Create device (make_device returns tuple of (device, module_name))
        # Device constructor creates Device_processor and registers it with Coordinator
        device, _modname = make_device(
            device_path,
            ot=Normal_out,
            device_folder=device_path.parent,
        )
        if device is None:
            result.error_message = f"Failed to create device from: {sim_config.device_file}"
            return result

        # Redirect device data output to temp directory if specified
        if sim_config.temp_data_dir:
            import hashlib

            param_hash = hashlib.md5(sim_config.parameter_string.encode()).hexdigest()[:12]
            temp_data_filename = f"data_output_{param_hash}.csv"
            device.data_filename = temp_data_filename
            device.data_filepath = Path(sim_config.temp_data_dir) / temp_data_filename

            # Symlink subdirectories from original device folder into temp dir
            # This allows devices that use data_filepath.parent to find input files
            for item in device_path.parent.iterdir():
                if item.is_dir():
                    link_path = Path(sim_config.temp_data_dir) / item.name
                    if link_path.exists():
                        continue  # Already created by another worker
                    try:
                        # target_is_directory=True is required for directory symlinks on Windows
                        os.symlink(item, link_path, target_is_directory=True)
                    except FileExistsError:
                        pass  # Another worker already created this symlink
                    except OSError:
                        # Symlink failed (e.g., Windows without Developer Mode or admin rights)
                        # Fall back to copying the directory
                        import shutil

                        try:
                            shutil.copytree(item, link_path)
                        except FileExistsError:
                            pass  # Another worker already copied this

            device.init_data_output()
            result.data_file = str(device.data_filepath)

        # Create model (this registers Human_processor with the Coordinator)
        model = Model(device)

        # Set up encoders - these connect device output to the model
        visual_encoder, visual_status = _load_encoder(sim_config.visual_encoder_file, "Visual", Normal_out)
        auditory_encoder, auditory_status = _load_encoder(sim_config.auditory_encoder_file, "Auditory", Normal_out)
        encoder_status = f"{visual_status}; {auditory_status}"
        set_visual_encoder_ptr(model, visual_encoder)
        set_auditory_encoder_ptr(model, auditory_encoder)

        # Connect device and human processors for event communication
        model.interconnect_device_and_human()

        # Setup what model output is needed
        _update_model_output_settings(model, sim_config.output_settings)

        # Compile rules
        rule_path = Path(sim_config.rule_file)
        if not rule_path.is_file():
            result.error_message = f"Rule file not found: {sim_config.rule_file}"
            return result

        model.set_prs_filename(str(rule_path))
        if not model.compile():
            result.error_message = f"Rule compilation failed: {sim_config.rule_file}"
            return result

        # Set rule_filename on device (for data output)
        if hasattr(device, "rule_filename"):
            device.rule_filename = rule_path.name

        # Initialize (order matters: instance first, then encoders, then model)
        instance.initialize()

        # Initialize encoders (required for device to receive events)
        if hasattr(visual_encoder, "initialize"):
            visual_encoder.initialize()
        if hasattr(auditory_encoder, "initialize"):
            auditory_encoder.initialize()

        model.initialize()

        # Set parameter string AFTER model.initialize() - this matches the main simulation
        device.set_parameter_string(sim_config.parameter_string)

        run_start = timeit.default_timer()

        # Determine run duration limit
        if sim_config.run_command == "run_until_done":
            run_time_limit = sys.maxsize
        elif sim_config.run_command == "run_for":
            run_time_limit = sim_config.run_command_value
        elif sim_config.run_command == "run_until":
            run_time_limit = sim_config.run_command_value
        elif sim_config.run_command == "run_for_cycles":
            run_time_limit = sim_config.run_command_value * 50
        else:
            run_time_limit = sys.maxsize

        # Run the simulation in chunks (like the main simulation does)
        # This allows the device to process events between chunks
        CHUNK_SIZE = 50  # 50ms per chunk, same as main simulation
        chunk_count = 0
        while True:
            try:
                instance.run_for(CHUNK_SIZE)
            except RuntimeError as e:
                # Capture the error with more context
                current_time = model.get_time()
                raise RuntimeError(
                    f"{e}\n[Debug: chunk={chunk_count}, sim_time={current_time}ms, "
                    f"device_state={device.state}, param='{sim_config.parameter_string}']\n"
                    f"[Encoders: {encoder_status}]"
                ) from None

            current_time = model.get_time()
            chunk_count += 1

            # Check if device has shut down (task complete)
            if device.state == device.SHUTDOWN:
                break

            # Check if we've reached the time limit
            if current_time >= run_time_limit:
                break

            # Safety check - if coordinator is finished, stop
            if instance.is_finished():
                break

        result.run_time_seconds = timeit.default_timer() - run_start
        result.simulated_time_ms = model.get_time()
        result.success = True

        # Clean up simulation
        model.stop()
        instance.stop()

    except Exception as e:
        import traceback

        result.error_message = f"{e}\n{traceback.format_exc()}"

    # Clear Python streams from C++ output tees to prevent GIL issues during
    # process finalization. This must happen outside the try block to ensure
    # cleanup even on error.
    try:
        from epiclibcpp.epiclib.output_tee_globals import (
            Debug_out,
            Device_out,
            Exception_out,
            Info_out,
            Normal_out,
            Stats_out,
            Trace_out,
        )
        from epiclibcpp.epiclib.pps_globals import PPS_out

        for tee in [Normal_out, Debug_out, Device_out, Exception_out, PPS_out, Trace_out, Stats_out, Info_out]:
            tee.clear_py_streams()
    except Exception:
        pass

    return result


def has_permutations(param_string: str) -> bool:
    """Check if a parameter string contains bracket-delimited permutations."""
    return "[" in param_string and "|" in param_string


def expand_permutations(param_string: str) -> list[str]:
    """Expand a parameter string with permutations into all combinations."""
    if not has_permutations(param_string):
        return [param_string]
    return unpack_param_string(param_string)


def merge_data_files(results: list[SimulationResult], output_path: Path) -> int:
    """
    Merge all temp data files from parallel simulations into a single output file.
    """
    data_files = [Path(r.data_file) for r in results if r.data_file and Path(r.data_file).is_file()]
    if not data_files:
        return 0

    rows_written = 0
    header_written = False

    with open(output_path, "w", newline="") as outfile:
        for data_file in data_files:
            with open(data_file, "r", newline="") as infile:
                lines = infile.readlines()
                if not lines:
                    continue

                # Write header only once (from the first file)
                if not header_written:
                    outfile.write(lines[0])
                    header_written = True

                # Write data rows (skip header in subsequent files)
                for line in lines[1:]:
                    outfile.write(line)
                    rows_written += 1

    return rows_written


def run_parallel_simulations(
    sim_configs: list[SimulationConfig],
    max_workers: int = _DEFAULT_MAX_WORKERS,
    on_complete: Callable[[SimulationResult], None] | None = None,
    device_folder: Path | None = None,
) -> list[SimulationResult]:
    """
    Run multiple simulations in parallel using ProcessPoolExecutor.
    """
    # Set up temp directory for data files
    temp_dir = _get_session_temp_dir()
    for cfg in sim_configs:
        cfg.temp_data_dir = str(temp_dir)

    results: list[SimulationResult] = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_single_simulation, cfg): cfg for cfg in sim_configs}

        for future in as_completed(futures):
            cfg = futures[future]
            try:
                result = future.result()
                results.append(result)
                if on_complete:
                    on_complete(result)
            except Exception as e:
                # Create a failure result for unexpected errors
                error_result = SimulationResult(
                    sim_config=cfg,
                    success=False,
                    error_message=f"Worker process error: {e}",
                )
                results.append(error_result)
                if on_complete:
                    on_complete(error_result)

    # Merge data files into device folder
    if device_folder:
        output_path = device_folder / "data_output.csv"
        merge_data_files(results, output_path)

    return results


def create_sim_configs_from_permutations(
    device_file: str,
    rule_file: str,
    base_param_string: str,
    output_settings: OutputSettings,
    run_command: Literal["run_until_done", "run_for", "run_until", "run_for_cycles"] = "run_until_done",
    run_command_value: int = 0,  # only for run_for/run_until/run_for_cycles commands
    visual_encoder_file: str = "",
    auditory_encoder_file: str = "",
) -> list[SimulationConfig]:
    """
    Create a list of SimulationConfig objects from a parameter string with permutations.
    """
    param_variations = expand_permutations(base_param_string)

    return [
        SimulationConfig(
            device_file=device_file,
            rule_file=rule_file,
            parameter_string=param,
            output_settings=output_settings,
            run_command=run_command,
            run_command_value=run_command_value,
            visual_encoder_file=visual_encoder_file,
            auditory_encoder_file=auditory_encoder_file,
        )
        for param in param_variations
    ]
