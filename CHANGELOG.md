
# EPICpy Changelog
#### (lasted updated Sun Aug 25 00:46:51 2024)

---


## VERSION: 2024.6.8

---
1. **FIXED**: Output save action complained about using the selectedFilter parameter. Removed it for now.

2. Minor: using print for initial cml message, instead of using log.

## VERSION: 2024.6.3.2

---

## VERSION: 2024.6.3.1

---
1. **FIXED**: Windows epiclib dll was missing describe_parameters_u function causing EPICpy to crash. Now ignores this call if it can't be found. Note that Windows EPICpy will not be able to dump parameters.


## VERSION: 2024.6.3

---
1. **CHANGE**: view and text display options have been reduced to either always on or always off. Updated resettings dialog to reflect this.

2. **FIXED**: Post halt_simulation messages now wait for output text to be idle so that the messages are always visible at the end of the trace.

3. Changelog saved.

## VERSION: 2024.6.2

---
1. Adjusted choicetask device uses for tests to remove depreciated stuff. Also fixed graph yaxis behavior.
2. Formatted code using black. fixed problem with tests. fixed problem with loading scripts and saving outputs.
3. Wording fix.
4. Fixed search issues. only using concurrent search when number of lines is very large.
5. Working except for search in tracewin.
6. Seems to work.
7. Fixed clear and search methods in LargeTextView.
8. Definitely faster. as much functionality as can be restored given that we are no longer using plaingtextedit, has been. with the exception of F3 and ShftF3 to continue search and a horiz scrollbar.
9. Got context menu working again. efficient search works. copy to clipboard works.
10. Simulation handles enable and disable of text output when using LargeTextView. Better logic for hidden and unhidden windows. Fixed lack of inspection for late added LargeTextView to main and trace windows.
11. Much faster text display enabled. various issues need to be resolved.
12. Turned off text save debug messages. fixed requirements.
13. **FIXED**: requirements.txt had version error

14. **FIXED**: requirements.txt did not seem to be a complete set of what was required.

15. **FIXED**: save normal and trace output dialogs working properly now.

16. Fixed 1) problem opening text files in default app from GUI on Windows. 2) printing of default epic params on model start.
17. Fixed Qt import.

## VERSION: 2023.6.1

---
1. Attempting to use PySide6 on any OS except MacOs 10.x and below.
2. Using qtpy instead of specific reference to pyside6 or pyqt6.
3. Changed pyqt5 to pyside6 in setup.py, also added pyqtdarktheme and pandas explicitly.
4. Fixed some QFileDialog.getOpenFileName calls and removed last bastion of code referencing the editor window.
5. Nailed down minimal reqs. worked on getting duration to show after all other text. not succeeded but dumping it to console and trace window help for now.
6. Added: Spinning cursor during device load.
7. Quick format.
8. PySide6 seems to be working fine.
9. **CHANGE**: Using better approach to darkmode. Also has Auto mode that follows system settings.

10. **CHANGE**: Removed built-in editor and menu to toggle it!

11. Put last_config delete in try-except block - seems to be needed when going from old version of config file to new one.
12. **FIXED**: ui settings changes are properly rolled back if user presses Cancel button.

13. **CHANGE**: internally, updating config properties automatically saves config to disk.

14. **CHANGE**: Updated EPICpy from PyQt5 to PyQt6


## VERSION: 2023.5.29

---
1. Added GUI image to ReadMe.md.
2. Cannot pipx install from github unless epiclib binaries are therel. so I put them there despite this not being exactly best practices. my rationale is that they are unlikely to change frequently.
3. Changed temp epicpy2 name to epicpy throughout project.
4. Updated ReadMe.md.

## VERSION: 2023.5.28

---
1. Epiccoder font fix and requirements fix.
2. Changed default fontsize to 12pt.
3. Make sure correct epiclib file is used when runnning in IDE.

## VERSION: 2023.5.22

---
1. Updated: 1. Demo choice and detection devices will show image underlay if enabled in display_controls. 2. Last device noted when app first starts.
2. **CHANGE**: view windows no longer updated when closed.

3. **CHANGE**: trace window no longer written to when closed.

4. Corrected typo on about screen and ran black.
5. **FIXED**: Trace settings now saves changes.

6. Added a few simple optimizations.
7. Fixed - Normal Output text stream was broken, now fixed.
8. Bumped version to 2023.5.21.
9. **FIXED**: Initial and reset layouts work in a more accurate and consistent way across OSs.

10. **CHANGE**: for proper operation on windows,had to move back to local copy of munch module.

11. Layout_reset draft change completed, needs testing on smaller desktops.
12. Now forcing sync after layout save.
13. **FIXED**: Now using a less problematic lru_cache.

14. **CHANGE**: Localmunch scheme replaced by just importing the munch library from pypi.

15. **FIXED**: More gracefully handling SEGSEGV caused by epiclib.


## VERSION: 2023.5.16

---
1. Updated setup.py for windows pipx install.
2. **CHANGE**: Now using udp broadcasting to get normal and trace outputs to GUI. Debug and PPS outs are untested.

3. Quick cleanup.
4. **FIXED**: had to deal with qscintilla issue with older versions of glibc on linux. now handles this gracefully.

5. **CHANGE**: unified menu bar on mac, now at normal output window like windows and linux.

6. Fix setup.py to properly notice mac and win hosts.

## VERSION: 2023.5.6

---
1. **FIXED**: pipx working with resources folder in tact. removed old pyinstaller tools. Pinned requirements.

2. Another resource movement but still pipx isnt pulling it in.
3. **CHANGE**: ReArranged everything to work properly with pipx. includes devices, encoders, and text devices. everything put into subfolders except for main.py

4. Installs but having import issue with modules in root folder.
5. Done encoders now work. printing of model parameters also works.
6. Remove some debug messages prior to attempting to remove the need to ever call model.get_human_ptr.
7. **CHANGE**: Clearing of stats ui before each sim run has been REINSTATED.

8. **FIXED**: default window sizing uses more reasonable defaults and includes or removes windows depending on available real-estate

9. Edited freezing and packaging scripts.
10. Updated changelog.

## VERSION: 2023.4.15

---
1. Added sigsegv ignore just in case it helps on mac - does nothing on linux.
2. Pystreamer update is done. output_tee related sigbart is gone.
3. Seems to work but still getting fault on quit.
4. **CHANGE**: stats output window no longer clears when running multiple simulations back to back. if all sims produce stats output, they get APPENDED to what's already there. A new run, single or multiple, will still clear stats output window.

5. Test run now works without neededing to pull devices from internet. also added 4 virtual subjects so stat test in choice_task stats output will work.
6. No longer makes a federal case if rule file is not found on device reload.
7. Getting EPICpy2 to work with epiclib on linux mac and windows.
8. Remove article folder.
9. **CHANGE**: Major Changes: 1) Replaced use of cppyy with a pre-compiled Python module compiled using PyBind11. I.e., the project contains no more C++ code. This has led to major changes to the project file structure. 2) Several minor but unavoidable changes to device and encoders. 3) EPICpy is now using Python 3.10.

10. **CHANGE**: Major Dev update: Abandoned use of FBSpro (paid) and now using only pyinstaller (free and opensource) to generate binaries. Significant changes to folder structure.

11. Added pyinstaller to requirements.txt and updated exact_requirements.txt.
12. Reimplemented logging facility. also changes to logging properly saved to config.
13. Disabled menu item for altering the EPICLib version. Removed mention of cppyy from About screen.
14. Fixed error in dialog initializations as well as removed extraneous output from epiclib's pystreamer interface.
15. Fixed view and encoder bases and now choicetask runs! NOTE: runs slower (10 trials of hard choice with live output: old=.68sec new=.71sec), (10 trials of hard choice with cached output: old=.21sec new=.32sec).
16. Made a pass on epicsimulation but not sure if it works yet.
17. Finally ready to tackle epicsimulation which may need structural changes for the new pybind11 interface to epiclib.
18. Updated main app code to work with epiclib including removing various cppyy related modules.
19. Getting ready to pivot to epiclib python module.
20. **CHANGE**: No longer relying on FBS for build - now using plain pyinstaller. Also, major folder re-organization.

21. Removed fbs frm reqs.
22. Removed former epiclibworkout stuff, will add proper tests shortly.
23. I made an error -- I forgot which branch I was in. These changes primarily have to do with removing the dependency on fbs pro. there is also a bit of epiclib testing that was never finished.
24. Removed some apparently unnecessary EPIClib imports from python code. done with branch for now.
25. Removing apparently unnecessary model check in epicsimulation.
26. **FIXED**: problem setting break states in break-state dialog window

27. **FIXED**: now including greatgrandparent to path adjustment for device load.

28. Removed: epicsim stub to reset path was unnecessary.

## VERSION: 2022.12.11

---
1. **FIXED**: Various features of Normal Output popup window. Added: First pass of run-script feature. Fixed: Extra spaces in Trace Window.

2. Last script now being saved in app config.
3. Script feature seems to be working. only tested for now as far as I need for grading final exam.
4. Script run works with hardcoded script path. also fixed default filename when exporting stats window.
5. Successfully reading in well-formed script file or else alerting user of issue.
6. Replaced simple list of rule paths with RunInfo objects and core func for single and multiple rule loading seems intact.
7. Created menu changes prior to implementing run_script functionality.
8. Removed some improperly added files from main.
9. Accidentally staged files needed for next feature!
10. **FIXED**: NO popup edit options availability makes better use of run_state. fixed: Ability to edit rules following rule load error restored.

11. Added: NO popup menu has option to open device folder.
12. **FIXED**: null action warning on popup. added: popup to search, copy, and clear tracewindow text.

13. **FIXED**: eliminated big blank sections in trace output.


## VERSION: 2022.11.25

---
1. **CHANGE**: new approach to loading devices and encoders no longer requires creating temp files.


## VERSION: 11.18.2022

---
1. Fixed background images not showing up, fixed background images not resizing.
2. Moved tests to submenu under help menu.
3. Font size menu example now updates as you change font size.
4. Rearranged NO popup, fixed NO edit file availaibility in popup, changed editor modes to either built-in or system default. no more entering an editor file path.
5. Updated EPICCoder to v1.1.0.
6. Going to merge these tools useful for bug finding in pyEPIC project.
7. Moved to own subfolder - split up gym and workout - added comparisons.
8. Working - can now see numbers being used.
9. Working - only issue is calls with random obj gen are opaque and depend on matching randomization seeds.
10. Seems to be actually working for classes structs and namespaces!
11. Almost ready to run but issue with how im trying to make calls from strings.
12. Have system for obtaining sufficient call information for exercising EPICLib objects properties and methods.
13. Removed CITATION.cff in favor of explicit citation note in README.md.
14. Exact_requirements.txt was getting out of date (e.g., we're now using PyQt5).

## VERSION: 2022.8.2

---
1. Manually renaming erronous 2022.10.1 version in changelog - should have been 2202.8.1.
2. **FIXED**: editor won't close automatically if any open file has changed.

3. **NEW FEATURE**: Built-in editor is available (based on the EPICcoder project)

4. **CHANGE**: EPICpy license changed to GPLv3 due to use of PyQT5.

5. **CHANGE**: EPICpy GUI qt-bindings switched from Pyside2 to PyQt5


## VERSION: 2022.8.1

---
1. Fixed typo in EVERY instance of short license statement.
2. Can select Built-In-Editor or choose external one but BIE not yet implemented.
3. Added some citation info now that article is published.
4. Right-click on normal output correctly uses specified external editor.
5. User can now specify built-in text editor or point to one on disk.
6. Pull request didn't go through. trying again.
7. Capitalized word.
8. Corrected spelling of a word and punctuation of another.
9. Removed redundant Figure names, clarified Figure captions, other typos and clarifications.
10. Fixed a few typos. Clarified OS versions in 2 of places.
11. Allowing encoders that derrive from new epicpy encoder bases.
12. Normalized font for new datafile delete menu item. Also added dynamic enabling/disabling depending on sim run state.
13. Added way to delete datafile without opening the run settings menu.
14. Added ability to draw full cardinal set of leader positions. Shortened leader length slightly.

## VERSION: 2022.4.1

---
1. Improved search dialog. backwards button plus enter to close.
2. Repositioned Quit on NormOutWin context popup to prevent accidental exits.
3. Reclassified debug logs in cpyysetup to info logs.
4. Removed forgotten debug logs from config module.
5. Added full complement of directional arrows to shape router. No new shpae code needed, just had to specify angular offsets.
6. More emoji_box changes -- moved things to be more vertical than horizontal to accommodate thinner output windows.
7. Fixed problem with prs errors not showing up. also fixed problem with misaligned emoji_boxes.
8. Removed author note.
9. Added article for review at JOSS.
10. Added subheading to readme.
11. Invited contributions to issue tracker and discussion page on github.
12. Re-allow run tests in docker containers. Cleaned up log statements in resource setup.
13. New version - Now features test run menu for goodness of fit runs.
14. Removed imports and uses of pynput from fitness.py.
15. Properly restoring choice task settings after test run.
16. Solved load_xxx problem on mac. solved browser load problem on mac.
17. Ui tests don't work properly on Docker, so disabling them when run from container with RUNCONTEXT=DOCKER set.
18. Tests now auto-download devices from website. Fixes logic for basic run feedback.
19. Added Facility To Test App Functionality from Tests Menu.
20. Created guide for contributing to project.

## VERSION: 2022.3.5

---
1. First draft of EPICpy created between 12/2020 and 3/2022 prior to 1st commit on GitHub.

_yes, this is basically just `git log --pretty=oneline --no-merges` with a few notes thrown in_
