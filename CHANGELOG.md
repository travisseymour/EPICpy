
# EPICpy Changelog


---

## VERSION: 2025.3.24.6

1. **FIXED**: Launcher check error on Windows.


---

## VERSION: 2025.3.24.3

1. **FIXED**: Launcher code was using wrong case for Icon.x.

---

## VERSION: 2025.3.24.2

1. **FIXED**: Problems with ui saving.
2. **FIXED**: Problems with test runner.
3. **UPDATED**: Overhauled User Interface. Instead of multiple windows, uses a unified dockable interface.
4. Added code to create app launcher following first load.
5. Allows launcher cleanup via "cleanup" argument on commandline. 
6. Added epicpydevice notice to StatsOutput.

---

## VERSION: 2025.3.14.1

1. **FIXED**: Window geometry settings were being ignored on Fedora under GNOME 47.

---


## VERSION: 2025.3.11.2

1. **CHANGED**: Preferring Sans-Serif system font default after issues with monospace rendering on some systems.
2. **FIXED**: Problem with menu access to output window text search functionality (keyboard was already working).


---

## VERSION: 2025.3.5.1

1. **FIXED**: Problem with view background images was fixed.
2. **ADDED**: added ParameterString tool-tip in run-settings dialog.


---

## VERSION: 2025.2.26.4

1. **ADDED**: Ability to copy current line of output window.
2. **FIXED**: Fixed bugs in custom textedit used in output windows.
3. **UPDATE**: Updated device loader to a more secure method. 
4. **FIXED**: Started moving broken text boxes. 
5. **FIXED**: Remove redundant timer calls.

---

## VERSION: 2025.2.13.5

1. **ADDED**: Due to slow startup on mac and windows, adding splash screen so they at least know the startup worked. If splash doesn't start early enough on those systems, this feature may be removed.
2. **FIXED**: Fixed misc references to pyqt directly, instead of using qtpy
3. **FIXED**: Updated old mac check to better decide between pyside2 and pyside6
4. **PINNED**: Pinned some dependencies to provide max compatability for Python 3.9 and 3.10 on Linux, Windows, and MacOS BigSur to Sonoma+

---

## VERSION: 2025.2.10.1

1. **FIXED**: Fixed some issues with view drawing strategy. Slightly faster, overlap now in one color for light and dark modes.
2. **FIXED**: Restored broken text printing on visual view windows.

---

## VERSION: 2025.2.8.5

1. **CHANGED**: In attempt to restore console output on Windows, I'm altering setup.py to start EPICpy as a console app on Windows only. This change will only take effect on install or re-install.

---

## VERSION: 2025.2.8.4

1. **CHANGED**: Changed stats window to be more content aware and provide context-specific actions text and figures via right-click menu.
2. **FIXED**: Updated dataclass behavior to skip specifying slots=True on Windows because EPICpy must use Python 3.9 on Windows, which does not support this parameter in dataclass initialization.

---

## VERSION: 2025.2.6.4

1. **FIXED**: Fixed several issues with text output skipping lines.

---

## VERSION: 2025.2.6.3

1. **FIXED**: More efficient batching approach to text updates.
2. **FIXED**: Incorrect text generation in test case.
3. **CHANGED**: Temporarily ignoring debug message from epiclib

---

## VERSION: 2025.2.6.2

1. **FIXED**: epiccoder fallback now working on Linux and MacOS (no test on Windows). If config entry "text_editor" is either empty or contains "default" __and__ epiccoder has been installed, then epiccoder is used for text and prs editing. Otherwise, EPICpy attempts to launch the sytem default (if set).
2. **CHANGED**: default font family is monospace, not sans-serif
3. **FIXED**: fixed extention fallback when saving stats window content to external file.
---

## VERSION: 2025.2.5.3

1. **CHANGED**: When running external apps to edit simulation text files; a) if app path is set  in global config for text, it is used. b) If noting is set, but epiccoder is installed, it is used. c) otherwise, default app for text is called. d) for data file editing, default app is always called.
2. **FIXED**: Removed all emoji and ascii_box for windows due to corresponding issue exporting text from output windows. Will try to recover this functionality on windows shortly.

---

## VERSION: 2025.2.5.2

1. **FIXED**: Encoding error when saving output windows to text on MacOS.
2. **CHANGED**: Better cross os control of font and font size changes across ui. 
3. **CHANGED**: Faster lru_cache behavior for flywheel patterns.

---

## VERSION: 2025.1.11.4

1. **FIXED**: There was a syntax error in setup.py, fixed. 
2. **CHANGED**: Re-added pingouin to see if this was part of the problem addressed by 2025.1.9.1
3. **FIXED**: Fixed bug rated to issues with older pinned project requirements resulting in tying.Self error.
4. **FIXED**: Issue on older MacOS versions where normal output window context window glitched (exec/exec_ error).

---

## VERSION: 2025.1.8.5

1. **FIXED**: epiclib library not being copied properly on MacOS and Windows. Using more robust scheme for referencing app resources when packaged.





