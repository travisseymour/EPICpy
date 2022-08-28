
# EPICpy Changelog
#### (lasted updated Sun Aug 28 15:40:35 2022)

---

#### 1. FIXED: editor won't close automatically if any open file has changed.

#### 2. NEW FEATURE: Built-in editor is available (based on the EPICcoder project)

#### 3. CHANGE: EPICpy license changed to GPLv3 due to use of PyQT5.

#### 4. CHANGE: EPICpy GUI qt-bindings switched from Pyside2 to PyQt5


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
