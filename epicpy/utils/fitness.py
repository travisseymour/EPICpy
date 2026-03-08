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

from __future__ import annotations

import datetime
import platform
import re
import shutil
import time
import timeit
import webbrowser
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

# from numpy import isin
import pandas as pd
from epiclibcpp.epiclib.output_tee_globals import Info_out
from platformdirs import user_documents_path
from qtpy.QtCore import QCoreApplication, QEventLoop, QTimer

from epicpy.utils.app_utils import hcolor
from epicpy.widgets.custom_text_edit import CustomQTextEdit

if TYPE_CHECKING:
    from epicpy.windows.main_window import MainWin

import epicpy.utils.config as config
from epicpy.utils.app_utils import extract_from_zip
from epicpy.utils.resource_utils import get_resource
from epicpy.widgets.mem_large_text_view import MemLargeTextView

"""
Code for testing various EPICpy functionality
"""

TEST_RESULTS = []
BUSY = False
DEVICE_BASE_FOLDER: Path
TEST_DEVICE_FOLDER: Path

"""
helper functions
"""


def _snapshot_cfg_fields(cfg):
    """
    Take a shallow snapshot of simple fields on device_cfg.
    Avoids deepcopy to prevent copying Qt / C++ handles.
    """
    # Most of your fields are primitives/str/bool/float, so shallow is fine.
    # If device_cfg is a plain object, vars(cfg) works; fallback to dir-based.
    try:
        d = dict(vars(cfg))
    except TypeError:
        # Fallback: collect public attrs
        d = {k: getattr(cfg, k) for k in dir(cfg) if not k.startswith("_") and hasattr(cfg, k)}
    return d


def _restore_cfg_fields(cfg, snapshot: dict):
    # Only restore keys that still exist; don't clobber newly-added attrs.
    for k, v in snapshot.items():
        try:
            setattr(cfg, k, v)
        except Exception:
            # Ignore non-restorable fields
            pass


@contextmanager
def temporary_device_cfg(overrides_func):
    """
    Context manager that snapshots current device_cfg fields,
    applies overrides (via setup_test_device_config), and then restores them.
    """
    snap = _snapshot_cfg_fields(config.device_cfg)
    try:
        overrides_func()
        yield
    finally:
        _restore_cfg_fields(config.device_cfg, snap)


def setup_test_device_config():
    config.device_cfg.log_normal_out = False
    config.device_cfg.log_trace_out = False
    config.device_cfg.run_command = "run_until_done"
    config.device_cfg.run_command_value = 10
    config.device_cfg.display_refresh = "after_each_step"
    config.device_cfg.text_refresh = "none_during_run"
    config.device_cfg.display_refresh_value = 10
    config.device_cfg.text_refresh_value = 2
    config.device_cfg.trace_visual = False
    config.device_cfg.trace_auditory = False
    config.device_cfg.trace_cognitive = True
    config.device_cfg.trace_ocular = False
    config.device_cfg.trace_manual = False
    config.device_cfg.trace_vocal = False
    config.device_cfg.trace_temporal = False
    config.device_cfg.trace_device = True
    config.device_cfg.trace_pps = True
    config.device_cfg.output_compiler_messages = False
    config.device_cfg.output_compiler_details = False
    config.device_cfg.output_run_messages = True
    config.device_cfg.output_run_details = False
    config.device_cfg.output_run_memory_contents = True
    config.device_cfg.sound_text_kind = True
    config.device_cfg.sound_text_stream = False
    config.device_cfg.sound_text_timbre = True
    config.device_cfg.sound_text_loudness = False
    config.device_cfg.speech_text_kind = True
    config.device_cfg.speech_text_stream = False
    config.device_cfg.speech_text_pitch = False
    config.device_cfg.speech_text_loudness = False
    config.device_cfg.speech_text_content = True
    config.device_cfg.speech_text_speaker = False
    config.device_cfg.speech_text_gender = False
    config.device_cfg.step_time_delay = 0
    config.device_cfg.setting_run_for_real_secs = 50
    config.device_cfg.setting_run_until_msecs = 600
    config.device_cfg.setting_run_cycles = 1
    config.device_cfg.setting_refresh_secs = 1.0
    config.device_cfg.device_params = "10 4 Hard [P1|P2|P3|P4]"
    config.device_cfg.spatial_scale_degree = 10
    config.device_cfg.calibration_grid = False
    config.device_cfg.center_dot = False
    config.device_cfg.describe_parameters = False
    config.device_cfg.allow_device_images = False
    config.device_cfg.allow_parallel_runs = False


def setup_test_device_folder(window: MainWin):
    global TEST_DEVICE_FOLDER, DEVICE_BASE_FOLDER
    Info_out("Initializing EPICpy Testing...\n")

    # because we've updated how device stats work, we need to re-create old Documents\EPICpy folders
    device_base_folder = Path(user_documents_path(), "EPICpy")
    if device_base_folder.is_dir():
        folder_creation_time = device_base_folder.stat().st_ctime
        cutoff_date = datetime.datetime(2026, 3, 1).timestamp()
        if folder_creation_time < cutoff_date:
            shutil.rmtree(device_base_folder)
            TEST_DEVICE_FOLDER = None  # type: ignore[assignment]
            DEVICE_BASE_FOLDER = None  # type: ignore[assignment]

    # maybe we already have a test device folder?
    try:
        assert isinstance(TEST_DEVICE_FOLDER, Path) and TEST_DEVICE_FOLDER.is_dir()
        Info_out("- Test device folder already exists, no need to re-create it.\n")
        return True
    except Exception:
        Info_out("- Test device folder is missing, will create a new one.\n")

    # make sure EPICpy folder exists in Documents
    try:
        # using this approach because initially DEVICE_BASE_FOLDER isn't even defined
        assert isinstance(DEVICE_BASE_FOLDER, Path) and DEVICE_BASE_FOLDER.is_dir()
    except Exception:
        DEVICE_BASE_FOLDER = Path(user_documents_path(), "EPICpy")
        DEVICE_BASE_FOLDER.mkdir(exist_ok=True)

    Info_out(f"- Test devices will be located here: {str(DEVICE_BASE_FOLDER)}\n")

    # make sure we have access to devices zip file
    try:
        devices = get_resource("other", "devices.zip")
    except Exception as e:
        Info_out(f"- Unable to locate test device archive inside application package! {e}. Contact project maintainer.\n")
        return False

    Info_out("- Unzipping test device archive...\n")
    try:
        extract_from_zip(
            zip_path=Path(devices),
            target_path=Path(DEVICE_BASE_FOLDER, "devices"),
            start_path="devices",  # Start extraction at this folder inside the archive
        )

        assert Path(DEVICE_BASE_FOLDER, "devices").is_dir(), (
            f"Uncompressed test device folder could not be located in the device base folder ({str(DEVICE_BASE_FOLDER)})."
        )
    except Exception as e:
        Info_out(f"ERROR: {e}\n")
        return False

    TEST_DEVICE_FOLDER = Path(DEVICE_BASE_FOLDER, "devices")
    if isinstance(TEST_DEVICE_FOLDER, Path) and TEST_DEVICE_FOLDER.is_dir():
        Info_out(f"- Successfully setup test device in {DEVICE_BASE_FOLDER}.\n")
        return True
    else:
        Info_out(hcolor(f"- Failed to setup test device in {DEVICE_BASE_FOLDER}.\n", "red"))
        return False


def show_results():
    global TEST_RESULTS

    tab5 = "\t" * 5
    tab6 = "\t" * 6
    table = ""

    for item in TEST_RESULTS:
        if item["Kind"] == "String":
            table += f"{tab5}<tr>\n"
            table += f'{tab6}<td colspan="3">{item["Name"]}</td>\n'
            table += f"{tab5}<tr>\n"
        else:
            color = "Green" if item["Worked"] else "Red"
            table += f"{tab5}<tr>\n"
            table += f'{tab6}<td><font color="{color}">{item["Name"]}</font></td>\n'
            table += f'{tab6}<td><font color="{color}">{item["Worked"]}</font></td>\n'
            table += f'{tab6}<td><font color="{color}">{item["Outcome"]}</font></td>\n'
            table += f"{tab5}<tr>\n"

    html = """
    <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>EPICpy Test Results</title>
            <style>
            table {
                font-family: "Courier New", Courier, monospace;
                border-collapse: collapse;
                <!-- width: 100%; -->
            }
            
            td, th {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            
            tr:nth-child(even) {
                background-color: #dddddd;
            }
            </style>
            </head>
            <body>fitness
                <h1>EPICpy Test Results</h1>
                <hr>
                <table>
                    <tr>
                        <th>Name</th>
                        <th>Worked</th>
                        <th>Outcome</th>
                    </tr>
                [[TABLE_ROWS]]
                </table>
            </body>
        </html>
    """

    html = html.replace("[[TABLE_ROWS]]", table)

    html_file = Path(DEVICE_BASE_FOLDER, "results.html")
    html_file.write_text(html)

    if platform.system() == "Darwin":
        # without this, webbrowser.open() crashed trying to find chrome.
        # rather than solve that issue, just force Safari use
        webbrowser.get(using="Safari").open(html_file.as_uri(), new=0, autoraise=True)
    else:
        webbrowser.open(html_file.as_uri(), new=0, autoraise=True)


def add_string(name: str):
    global TEST_RESULTS
    TEST_RESULTS.append({"Name": f"<b>{name}</b>", "Worked": "", "Outcome": "", "Kind": "String"})


def clear_results():
    global TEST_RESULTS
    TEST_RESULTS = []


def add_result(name: str, worked: bool, outcome: str):
    global TEST_RESULTS
    TEST_RESULTS.append(
        {
            "Name": f"<b>{name}</b>",
            "Worked": str(worked),
            "Outcome": outcome,
            "Kind": "Result",
        }
    )


def wait(duration: float, msg: str = ""):
    """Wait for duration seconds while processing Qt events."""
    start = timeit.default_timer()
    if msg:
        Info_out(msg)
    while True:
        QCoreApplication.processEvents()
        if timeit.default_timer() - start > duration:
            break


def wait_for_output(
    text_edit: MemLargeTextView | CustomQTextEdit,
    target: str,
    sigil: Optional[str] = None,
    timeout_secs: float = 0.0,
) -> Tuple[bool, str]:
    """
    Wait for target text to appear in a text widget.
    - a target is a Regex pattern(s) to be matched (use || to separate multiple patterns that must all match)
    - a sigil is a Regex pattern(s) that indicates failure (use || to separate multiple)
    """
    _timeout = timeout_secs if timeout_secs else 10.0
    start = timeit.default_timer()
    target_parts = target.split("||") if target else []
    sigil_parts = sigil.split("||") if sigil else []

    # Result container for nested function access
    result: list[Tuple[bool, str]] = []
    loop = QEventLoop()

    def get_text() -> str:
        if isinstance(text_edit, MemLargeTextView):
            return text_edit.get_text()
        return text_edit.toPlainText()

    def check_content():
        """Check if target or sigil is found. Sets result and quits loop if done."""
        text = get_text()

        if target_parts and all(re.findall(p, text) for p in target_parts):
            result.append((True, "Success"))
            loop.quit()
            return True

        if sigil_parts and all(re.findall(p, text) for p in sigil_parts):
            result.append((False, "Fail"))
            loop.quit()
            return True

        # Check timeout
        now = timeit.default_timer()
        if now - start > _timeout:
            result.append((False, f"Operation Timed Out. {now=} > {_timeout}"))
            loop.quit()
            return True

        return False

    def on_content_changed(*_args):
        """
        Called when content changes in either widget type.
        There may be a better way to do this?
        """
        check_content()

    def on_timeout():
        if not result:
            result.append((False, f"Operation Timed Out after {_timeout}s"))
            loop.quit()

    # Check immediately in case target is already present
    if check_content():
        return result[0]

    # Connect to the appropriate signal
    if isinstance(text_edit, MemLargeTextView):
        text_edit.content_changed.connect(on_content_changed)
    else:
        text_edit.textChanged.connect(on_content_changed)

    # Set up timeout
    QTimer.singleShot(int(_timeout * 1000), on_timeout)

    # Wait for signal or timeout
    loop.exec()

    # Disconnect to avoid accumulating connections
    try:
        if isinstance(text_edit, MemLargeTextView):
            text_edit.content_changed.disconnect(on_content_changed)
        else:
            text_edit.textChanged.disconnect(on_content_changed)
    except RuntimeError:
        pass  # Already disconnected

    return result[0] if result else (False, "Unknown error")


def wait_for_stats_window(window: MainWin, timeout_secs: float = 60.0) -> str:
    """
    Wait for the stats window (QWebEngineView) to have content and return it.
    """
    start = time.time()
    poll_interval_ms = 250  # Check every 250ms

    while time.time() - start < timeout_secs:
        # Process events to allow loadFinished to fire
        QCoreApplication.processEvents()

        # Check if content is available
        text = window.get_stats_text()
        if text:
            return text

        # Wait a bit before next check using QEventLoop + timer
        # This keeps the UI responsive while waiting
        loop = QEventLoop()
        QTimer.singleShot(poll_interval_ms, loop.quit)
        loop.exec()

    return ""


"""
Test Collections
"""


def run_model_test(
    window: MainWin,
    load_encoders: bool = False,
    close_on_finish: bool = True,
    see_results: bool = True,
):
    # Clear Output Windows
    # window.clear_output_windows()

    # init
    device_loaded, rules_compiled, model_run = None, None, None

    # clear out old data
    data_file = Path(TEST_DEVICE_FOLDER, "choice", "data_output.csv")
    data_file.unlink(missing_ok=True)

    # save app_settings last device, so we can put it back
    last_device_file = config.app_cfg.last_device_file

    # Load Device
    device_loaded, outcome = test_load_device(window)
    add_result("Loading Device", device_loaded, outcome)

    if device_loaded:
        # Load Rules
        rules_compiled, outcome = test_compile_rules(window)
        add_result("Compiling Rules", rules_compiled, outcome)

        if rules_compiled:
            # Apply overrides inside a context that restores fields afterwards
            with temporary_device_cfg(setup_test_device_config):
                try:
                    if load_encoders:
                        encoder_loaded, outcome = test_load_encoder(window)
                        add_result("Load Encoder", encoder_loaded, outcome)
                    else:
                        encoder_loaded = False

                    if encoder_loaded or not load_encoders:
                        try:
                            window.delete_datafile()
                        except AttributeError:
                            ...
                        # Run Model
                        model_run, outcome = test_run_model(window)
                        add_result("Run Model", model_run, outcome)

                        if model_run:
                            # Wait for stats window population using loadFinished signal
                            Info_out("Waiting for stats window to populate...\n")
                            start = time.time()
                            text = wait_for_stats_window(window, timeout_secs=60.0)
                            elapsed = time.time() - start
                            if text:
                                Info_out(f"\nGot access to stats window text after {elapsed:0.4f} sec:\n{text}\n")
                            else:
                                Info_out(hcolor("\nFAILED to retrieve text from stats window after test!!\n", "red"))

                            correct_N = "N=40" in text  # 10 trials for 4 runs
                            correct_ACCURACY = "ACCURACY=100.00" in text
                            if load_encoders:
                                correct_ACCURACY = not correct_ACCURACY

                            add_result(
                                "StatsWindow: N == 40",
                                correct_N,
                                "Success" if correct_N else "Failed",
                            )
                            add_result(
                                f"StatsWindow: ACC {'!=' if load_encoders else '=='} 100.00%",
                                correct_ACCURACY,
                                "Success" if correct_ACCURACY else "Failed",
                            )

                            # Saved Data checks (unchanged)
                            try:
                                data = pd.read_csv(data_file)
                                can_read_data = True
                                expected_header = [
                                    "RunID",
                                    "Trial",
                                    "Task",
                                    "Difficulty",
                                    "StimColor",
                                    "StimPos",
                                    "CorrectResponse",
                                    "Response",
                                    "Modality",
                                    "RT",
                                    "Accuracy",
                                    "Tag",
                                    "Device",
                                    "Rules",
                                    "Date",
                                ]
                                correct_header = list(data.columns) == expected_header
                                if load_encoders:
                                    correct_accuracy_range = sorted(set(data.Accuracy)) == [
                                        "CORRECT",
                                        "INCORRECT",
                                    ]
                                else:
                                    correct_accuracy_range = sorted(set(data.Accuracy)) == ["CORRECT"]
                            except Exception:
                                can_read_data = False
                                correct_header = False
                                correct_accuracy_range = False
                            add_result(
                                "DataFile: Able To Read Data",
                                can_read_data,
                                "Success" if can_read_data else "Failed",
                            )
                            add_result(
                                "DataFile: Data Has Correct Header",
                                correct_header,
                                "Success" if correct_header else "Failed",
                            )
                            add_result(
                                f"DataFile: {'NOT' if encoder_loaded else ''} All trial 'CORRECT'",
                                correct_accuracy_range,
                                "Success" if correct_accuracy_range else "Failed",
                            )
                finally:
                    # restore app's last device setting (do NOT replace device_cfg object)
                    config.app_cfg.last_device_file = last_device_file

    if see_results:
        wait(2, "Creating Results Output, Please wait...\n")
        show_results()
        Info_out("Test Complete.\n")

    if close_on_finish:
        window.close()

    return model_run


def run_all_model_tests(window: MainWin, close_on_finish: bool = True, see_results: bool = True):
    add_string("RUNNING MODEL WITHOUT ENCODER (Expecting 100% Accuracy)")
    _ = run_model_test(window, load_encoders=False, close_on_finish=False, see_results=False)

    # If you *must* stop, guard it — but generally unnecessary after a clean finish.
    # try:
    #     if getattr(window, "actionStop", None):
    #         window.actionStop.trigger()
    # except Exception:
    #     ...

    wait(2)
    add_string("RUNNING MODEL WITH VISUAL ENCODER (Expecting < 100% Accuracy)")
    _ = run_model_test(window, load_encoders=True, close_on_finish=False, see_results=False)

    if see_results:
        wait(2, "Creating Results Output, Please wait...\n")
        show_results()
        Info_out("Test Finished.\n")

    wait(2)
    if close_on_finish:
        window.close()


"""
Component Tests
"""


def test_load_device(window: MainWin) -> Tuple[bool, str]:
    dev_path = Path(TEST_DEVICE_FOLDER, "choice", "choice_device.py")
    window.on_load_device(file=str(dev_path.resolve()))

    return wait_for_output(
        # window=window,
        text_edit=window.infoTextOutput,
        target="Successfully initialized device",
        sigil="Failed to create new EpicDevice",
        timeout_secs=15.0,
    )


def test_compile_rules(window: MainWin) -> Tuple[bool, str]:
    rule_path = Path(TEST_DEVICE_FOLDER, "choice", "rules", "choicetask_rules_VM.prs")
    window.simulation.choose_rules(files=[str(rule_path.resolve())])

    return wait_for_output(
        # window=window,
        text_edit=window.infoTextOutput,
        target=r"Rule file .+[ \n]+compiled successfully!",
        sigil="Unable to (re)compile ruleset",
        timeout_secs=15.0,
    )


def test_load_encoder(window: MainWin) -> Tuple[bool, str]:
    encoder_path = Path(TEST_DEVICE_FOLDER, "choice", "encoders", "donders_visual_encoder.py")
    window.simulation.on_load_encoder(kind="Visual", file=str(encoder_path.resolve()))

    return wait_for_output(
        text_edit=window.infoTextOutput,  # Info_out writes to infoTextOutput
        target="Visualencoder was created successfully",
        sigil="Failed to create new Visual encoder",
        timeout_secs=15.0,
    )


def test_run_model(window: MainWin) -> Tuple[bool, str]:
    window.run_normal(parallel=False)

    return wait_for_output(
        # window=window,
        text_edit=window.normalTextOutput,
        target=r"Run of .+\.prs Finished.",
        sigil="Stopped With Error",
        timeout_secs=15.0,
    )
