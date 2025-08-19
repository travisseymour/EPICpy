import platform
import re
import time
import timeit
from copy import deepcopy
from pathlib import Path
from typing import Tuple, Optional
import webbrowser

import pandas as pd
from platformdirs import user_documents_path
from qtpy.QtCore import QCoreApplication
from qtpy.QtGui import QAction
from qtpy.QtWidgets import QMainWindow

import epicpy.utils.config as config
from epicpy.utils.apputils import extract_from_zip
from epicpy import get_resource
from epicpy.widgets.largetextview import LargeTextView

from epicpy.epiclib.epiclib.output_tee_globals import (Normal_out, Trace_out, Exception_out)

"""
Code for testing various EPICpy functionality
"""

TEST_RESULTS = []
BUSY = False
DEVICE_BASE_FOLDER: Optional[Path] = None
TEST_DEVICE_FOLDER: Optional[Path] = None

"""
helper functions
"""


def setup_test_device_config():
    config.device_cfg.log_normal_out = False
    config.device_cfg.log_trace_out = False
    config.device_cfg.run_command = "run_until_done"
    config.device_cfg.run_command_value = 1
    config.device_cfg.display_refresh = "after_each_step"
    config.device_cfg.text_refresh = "after_each_step"
    config.device_cfg.display_refresh_value = 1
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


def setup_test_device_folder(window: QMainWindow):
    global TEST_DEVICE_FOLDER, DEVICE_BASE_FOLDER
    Normal_out("Initializing EPICpy Testing...")
    if TEST_DEVICE_FOLDER and TEST_DEVICE_FOLDER.is_dir():
        Normal_out("  Test files already created.")
        return True

    try:
        assert DEVICE_BASE_FOLDER.is_dir()
    except (AttributeError, AssertionError):
        DEVICE_BASE_FOLDER = Path(user_documents_path(), "EPICpy")
        DEVICE_BASE_FOLDER.mkdir(exist_ok=True)

    try:
        devices = get_resource("other", "devices.zip")
    except Exception as e:
        Normal_out(
            f"  Unable to locate test device archive inside application package! {e}. Contact project maintainer."
        )
        return False

    Normal_out("  Unzipping test device package...")
    try:
        extract_from_zip(
            zip_path=Path(devices),
            target_path=DEVICE_BASE_FOLDER,
            start_path="devices",  # Start extraction at this folder inside the archive
        )

        assert Path(
            DEVICE_BASE_FOLDER, "devices"
        ).is_dir(), "Uncompressed folder devices could not be located in Documents folder."
    except Exception as e:
        Normal_out(f"ERROR: {e}")
        return False

    TEST_DEVICE_FOLDER = Path(DEVICE_BASE_FOLDER, "devices")
    if not TEST_DEVICE_FOLDER.is_dir():
        Normal_out(f"  Failed to setup test device in {DEVICE_BASE_FOLDER}.")
        return False
    else:
        Normal_out(f"  Successfully setup test device in {DEVICE_BASE_FOLDER}.")
        return True


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


def wait(window: QMainWindow, duration: float, msg: str = ""):
    start = timeit.default_timer()
    if msg:
        Normal_out(msg)
    while True:
        QCoreApplication.processEvents()
        if timeit.default_timer() - start > duration:
            break


def wait_for_output(
    window: QMainWindow,
    text_edit: LargeTextView,
    target: str,
    sigil: Optional[str] = None,
    timeout_secs: float = 0.0,
) -> Tuple[bool, str]:
    _timeout = timeout_secs if timeout_secs else 20.0
    start = timeit.default_timer()
    while True:
        QCoreApplication.processEvents()
        text = text_edit.get_text()
        if timeit.default_timer() - start > _timeout:
            result = False
            outcome = "Operation Timed Out."
            break
        elif all([re.findall(pattern, text) for pattern in target.split("||")]):
            result = True
            outcome = "Success"
            break
        elif all([re.findall(pattern, text) for pattern in sigil.split("||")]):
            result = False
            outcome = "Fail"
            break

    return result, outcome


"""
Test Collections
"""


def run_model_test(
    window: QMainWindow,
    load_encoders: bool = False,
    close_on_finish: bool = True,
    see_results: bool = True,
):
    # Clear Output Windows
    # window.findChild(QAction, "actionClear_Output_Windows").trigger()

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
            # Store Current Device Run Settings...we have to put them back
            device_run_settings = deepcopy(config.device_cfg)
            # Fiddle With Device Run Settings
            setup_test_device_config()
            try:
                # Do Test(s)
                if load_encoders:
                    encoder_loaded, outcome = test_load_encoder(window)
                    add_result("Load Encoder", encoder_loaded, outcome)
                else:
                    encoder_loaded = False

                if encoder_loaded or not load_encoders:
                    # Clear Data File
                    try:
                        window.delete_datafile()
                    except AttributeError:
                        ...
                    # Run Model
                    model_run, outcome = test_run_model(window)
                    add_result("Run Model", model_run, outcome)

                    if model_run:
                        # Check Stats output
                        # "N=10, CORRECT=5 INCORRECT=0 MEAN_RT=573 ACCURACY=100.00%"

                        print("\nWaiting for stats window to populate...")
                        text = ""
                        start = time.time()
                        while time.time() - start < 10.0:
                            text = window.stats_win.plain_text()
                            if text:
                                break
                            QCoreApplication.processEvents()
                        if text:
                            print(f"\n\nGot access to stats window text after {time.time()-start:0.4f} sec:\n{text}\n")
                        else:
                            print(f"\n\nFAILED to retrieve text from stats window after test!!\n\n")

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
                            "Success" if correct_N else "Failed",
                        )

                        # Saved Data
                        # data_file_exists = data_file.is_file()
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
                        except:
                            can_read_data = False
                            correct_header = False
                            correct_accuracy_range = False
                        add_result(
                            f"DataFile: Able To Read Data",
                            can_read_data,
                            "Success" if can_read_data else "Failed",
                        )
                        add_result(
                            "DataFile: Data Has Correct Header",
                            correct_header,
                            "Success" if correct_header else "Failed",
                        )

                        add_result(
                            f"DataFile: {'NOT' if encoder_loaded else ''} " f"All trial 'CORRECT'",
                            correct_accuracy_range,
                            "Success" if correct_accuracy_range else "Failed",
                        )
            finally:
                # restore app's' last device setting
                config.app_cfg.last_device_file = last_device_file
                # restore device run settings
                config.device_cfg = device_run_settings

    if see_results:
        wait(window, 2, "\nCreating Results Output, Please wait...")
        show_results()
        Normal_out("Test Complete.")

    if close_on_finish:
        window.close()

    return model_run


def run_all_model_tests(window: QMainWindow, close_on_finish: bool = True, see_results: bool = True):
    add_string("RUNNING MODEL WITHOUT ENCODER (Expecting 100% Accuracy)")
    _ = run_model_test(window, load_encoders=False, close_on_finish=False, see_results=False)

    wait(window, 2)
    add_string("RUNNING MODEL WITH VISUAL ENCODER (Expecting < 100% Accuracy)")
    _ = run_model_test(window, load_encoders=True, close_on_finish=False, see_results=False)

    if see_results:
        wait(window, 2, "\nCreating Results Output, Please wait...")
        show_results()
        Normal_out("Test Finished.")

    wait(window, 2)
    if close_on_finish:
        window.findChild(QAction, "actionQuit").trigger()


"""
Component Tests
"""


def test_load_device(window: QMainWindow) -> Tuple[bool, str]:
    dev_path = Path(TEST_DEVICE_FOLDER, "choice", "choice_device.py")
    window.on_load_device(file=str(dev_path.resolve()))

    return wait_for_output(
        window=window,
        text_edit=window.normalPlainTextEditOutput,
        target="Successfully initialized device",
        sigil="Failed to create new EpicDevice",
        timeout_secs=5.0,
    )


def test_compile_rules(window: QMainWindow) -> Tuple[bool, str]:
    rule_path = Path(TEST_DEVICE_FOLDER, "choice", "rules", "choicetask_rules_VM.prs")
    window.simulation.choose_rules(files=[str(rule_path.resolve())])

    return wait_for_output(
        window=window,
        text_edit=window.normalPlainTextEditOutput,
        target=r"Rule file .+[ \n]+compiled successfully!",
        sigil="Unable to (re)compile ruleset",
        timeout_secs=5.0,
    )


def test_load_encoder(window: QMainWindow) -> Tuple[bool, str]:
    encoder_path = Path(TEST_DEVICE_FOLDER, "choice", "encoders", "donders_visual_encoder.py")
    window.simulation.on_load_encoder(kind="Visual", file=str(encoder_path.resolve()))

    return wait_for_output(
        window=window,
        text_edit=window.normalPlainTextEditOutput,
        target="Visualencoder was created successfully",
        sigil="Failed to create new Visual encoder",
        timeout_secs=5.0,
    )


def test_run_model(window: QMainWindow) -> Tuple[bool, str]:
    window.run_all()

    return wait_for_output(
        window=window,
        text_edit=window.normalPlainTextEditOutput,
        target=r"Run of .+\.prs Finished.",
        sigil="Stopped With Error",
        timeout_secs=15.0,
    )
