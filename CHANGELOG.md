
# EPICpy Changelog
#### (lasted updated Wed Jan 11 2025)

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





