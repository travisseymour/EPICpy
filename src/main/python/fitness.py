import re
import tempfile
import time
import timeit
import zipfile
from pathlib import Path
from typing import Tuple, Optional
import webbrowser

import pandas as pd
import requests
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QAction, QMainWindow
from pynput.keyboard import Key, Controller

from cachedplaintextedit import CachedPlainTextEdit

"""
Code for testing various EPICpy functionality
"""

keyboard = Controller()
TEST_RESULTS = []
TEMP_DIR = tempfile.mkdtemp()
BUSY = False
TEST_DEVICE_FOLDER = ""

"""
helper functions
"""


def setup_test_device_folder(window: QMainWindow):
    global TEST_DEVICE_FOLDER, TEMP_DIR
    window.write("Initializing EPICpy Testing...")
    if TEST_DEVICE_FOLDER and Path(TEST_DEVICE_FOLDER).is_dir():
        window.write("  Testing already initialized.")
        return True

    try:
        assert Path(TEMP_DIR).is_dir()
    except AssertionError:
        TEMP_DIR = tempfile.mkdtemp()

    window.write("  Retrieving Files For EPICpy Testing...")
    url = "https://people.ucsc.edu/~nogard/software/epicpy/devices.zip"
    response = requests.get(url)
    if not response.ok:
        window.write(
            f'ERROR: Unable to download test device package from website: "{response.reason}". Unable to perform test.'
        )
        return False

    try:
        with open(Path(TEMP_DIR, "devices.zip"), "wb") as outfile:
            outfile.write(response.content)
        assert Path(
            TEMP_DIR, "devices.zip"
        ).is_file(), (
            "Downloaded file devices.zip could not be located in temporary folder."
        )
    except Exception as e:
        window.write(f"ERROR: {e}")
        return False

    window.write("  Unzipping test device package...")
    try:
        with zipfile.ZipFile(Path(TEMP_DIR, "devices.zip"), "r") as infile:
            infile.extractall(Path(TEMP_DIR))
        assert Path(
            TEMP_DIR, "devices"
        ).is_dir(), (
            "Uncompressed folder devices could not be located in temporary folder."
        )
    except Exception as e:
        window.write(f"ERROR: {e}")
        return False

    TEST_DEVICE_FOLDER = str(Path(TEMP_DIR, "devices").resolve())

    window.write("  Completed Successfully!")
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
                font-family: arial, sans-serif;
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
            <body>
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

    html_file = Path(TEMP_DIR, "results.html")
    html_file.write_text(html)

    webbrowser.open(html_file.as_uri())


def add_string(name: str):
    global TEST_RESULTS
    TEST_RESULTS.append(
        {"Name": f"<b>{name}</b>", "Worked": "", "Outcome": "", "Kind": "String"}
    )


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


def enter_sequence(
    sequence: list,
    key_delay_sec: float = 0,
    window_for_delay: Optional[QMainWindow] = None,
):
    using_delay = key_delay_sec and window_for_delay is not None
    for item in sequence:
        if isinstance(item, str):
            keyboard.type(item)
        else:
            keyboard.press(item)
            keyboard.release(item)
        if using_delay:
            start = timeit.default_timer()
            while timeit.default_timer() - start < key_delay_sec:
                window_for_delay.context.app.processEvents()


def wait(window: QMainWindow, duration: float):
    start = timeit.default_timer()
    while True:
        window.context.app.processEvents()
        if timeit.default_timer() - start > duration:
            break


def wait_for_output(
    window: QMainWindow,
    text_edit: CachedPlainTextEdit,
    target: str,
    sigil: Optional[str] = None,
    timeout_secs: float = 0.0,
) -> Tuple[bool, str]:
    _timeout = timeout_secs if timeout_secs else 20.0
    start = timeit.default_timer()
    while True:
        window.context.app.processEvents()
        if timeit.default_timer() - start > _timeout:
            result = False
            outcome = "Operation Timed Out."
            break
        elif all(
            [
                re.findall(pattern, text_edit.toPlainText())
                for pattern in target.split("||")
            ]
        ):
            result = True
            outcome = "Success"
            break
        elif all(
            [
                re.findall(pattern, text_edit.toPlainText())
                for pattern in sigil.split("||")
            ]
        ):
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
    window.findChild(QAction, "actionClear_Output_Windows").trigger()

    # init
    device_loaded, rules_compiled, settings_entered, model_run = None, None, None, None

    # clear out old data
    data_file = Path(TEST_DEVICE_FOLDER, "choice/data_output.csv")
    data_file.unlink(missing_ok=True)

    # Load Device
    device_loaded, outcome = test_load_device(window)
    add_result("Loading Device", device_loaded, outcome)

    if device_loaded:
        # Load Rules
        rules_compiled, outcome = test_compile_rules(window)
        add_result("Compiling Rules", rules_compiled, outcome)

        if rules_compiled:
            # Enter Settings
            settings_entered, outcome = test_settings_dialog(window)
            add_result("Enter Settings", settings_entered, outcome)

            if settings_entered:

                if load_encoders:
                    encoder_loaded, outcome = test_load_encoder(window)
                    add_result("Load Encoder", encoder_loaded, outcome)
                else:
                    encoder_loaded = False

                if encoder_loaded or not load_encoders:
                    # Run Model
                    model_run, outcome = test_run_model(window)
                    add_result("Run Model", model_run, outcome)

                    if model_run:
                        # Check Stats output
                        # "N=10, CORRECT=5 INCORRECT=0 MEAN_RT=573 ACCURACY=100.00%"
                        text = window.stats_win.ui.statsTextBrowser.toPlainText()
                        correct_N = "N=10" in text
                        correct_ACCURACY = "ACCURACY=100.00" in text
                        if load_encoders:
                            correct_ACCURACY = not correct_ACCURACY

                        add_result(
                            "StatsWindow: N == 10",
                            correct_N,
                            "Success" if correct_N else "Failed",
                        )
                        add_result(
                            f"StatsWindow: ACC {'!=' if load_encoders else '=='} 100.00%",
                            correct_ACCURACY,
                            "Success" if correct_N else "Failed",
                        )

                        # Saved Data
                        data_file_exists = data_file.is_file()
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
                                correct_accuracy_range = sorted(set(data.Accuracy)) == [
                                    "CORRECT"
                                ]
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
                            f"DataFile: {'NOT' if load_encoders else ''} "
                            f"All trial 'CORRECT'",
                            correct_accuracy_range,
                            "Success" if correct_accuracy_range else "Failed",
                        )

    if see_results:
        wait(window, 2)
        show_results()

    if close_on_finish:
        window.findChild(QAction, "actionQuit").trigger()

    return model_run


def run_all_model_tests(
    window: QMainWindow, close_on_finish: bool = True, see_results: bool = True
):
    add_string("RUNNING MODEL WITHOUT ENCODER")
    _ = run_model_test(
        window, load_encoders=False, close_on_finish=False, see_results=False
    )

    wait(window, 2)
    add_string("RUNNING MODEL WITH ENCODER")
    _ = run_model_test(
        window, load_encoders=True, close_on_finish=False, see_results=False
    )

    if see_results:
        wait(window, 2)
        show_results()

    wait(window, 2)
    if close_on_finish:
        window.findChild(QAction, "actionQuit").trigger()


"""
Component Tests
"""


def test_load_device(window: QMainWindow) -> Tuple[bool, str]:
    dev_path = str(Path(TEST_DEVICE_FOLDER, "choice/choice_device.py").resolve())
    QTimer.singleShot(1000, lambda: keyboard.type(dev_path + "\n"))

    window.findChild(QAction, "actionLoad_Device").trigger()

    return wait_for_output(
        window=window,
        text_edit=window.ui.plainTextEditOutput,
        target="Successfully initialized device",
        sigil="Failed to create new EpicDevice",
        timeout_secs=5.0,
    )


def test_compile_rules(window: QMainWindow) -> Tuple[bool, str]:
    rule_path = str(
        Path(TEST_DEVICE_FOLDER, "choice/rules/choicetask_rules_VM.prs").resolve()
    )
    QTimer.singleShot(1000, lambda: keyboard.type(rule_path + "\n"))

    window.findChild(QAction, "actionCompile_Rules").trigger()

    return wait_for_output(
        window=window,
        text_edit=window.ui.plainTextEditOutput,
        target=r"Rule file .+[ \n]+compiled successfully!",
        sigil="Unable to (re)compile ruleset",
        timeout_secs=5.0,
    )


def test_load_encoder(window: QMainWindow) -> Tuple[bool, str]:
    encoder_path = str(
        Path(TEST_DEVICE_FOLDER, "choice/encoders/donders_visual_encoder.py").resolve()
    )
    QTimer.singleShot(1000, lambda: keyboard.type(encoder_path + "\n"))

    window.findChild(QAction, "actionLoad_Visual_Encoder").trigger()

    return wait_for_output(
        window=window,
        text_edit=window.ui.plainTextEditOutput,
        target="Visualencoder was created successfully",
        sigil="Failed to create new Visual encoder",
        timeout_secs=5.0,
    )


def test_settings_dialog(window: QMainWindow) -> Tuple[bool, str]:
    down = Key.down
    up = Key.up
    tab = Key.tab
    enter = Key.enter

    sequence = [
        down,
        down,
        down,
        down,
        tab,
        down,
        down,
        tab,
        down,
        down,
        up,
        tab,
        "2",
        tab,
        "0",
        tab,
        tab,
        tab,
        "10 4 Hard Draft",
        tab,
        enter,
        tab,
        enter,
        tab,
        enter,
    ]

    sequence = [
        down,
        down,
        down,
        tab,
        down,
        down,
        up,
        up,
        tab,
        down,
        down,
        up,
        tab,
        "2",
        tab,
        "0",
        tab,
        tab,
        tab,
        "10 4 Hard Draft",
        tab,
        tab,
        tab,
        enter,
    ]

    QTimer.singleShot(1500, lambda: enter_sequence(sequence, 0, window))

    window.findChild(QAction, "actionRun_Settings").trigger()

    return wait_for_output(
        window=window,
        text_edit=window.ui.plainTextEditOutput,
        target="Settings changes accepted",
        sigil="Settings changes ignored",
        timeout_secs=5.0,
    )


def test_run_model(window: QMainWindow) -> Tuple[bool, str]:
    window.findChild(QAction, "actionRunAll").trigger()

    return wait_for_output(
        window=window,
        text_edit=window.ui.plainTextEditOutput,
        target=r"Run of .+\.prs Finished.",
        sigil="Stopped With Error",
        timeout_secs=15.0,
    )
