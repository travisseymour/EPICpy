## EPICpy
### A Python Interface for EPIC Computational Cognitive Modeling
Travis L. Seymour, PhD

[![DOI](https://joss.theoj.org/papers/10.21105/joss.04533/status.svg)](https://doi.org/10.21105/joss.04533)

_Seymour, T. L., (2022). **EPICpy: A Python Interface for EPIC Computational Cognitive Modeling**. Journal of Open Source Software, 7(76), 4533, https://doi.org/10.21105/joss.04533_

---

**Background - Previous Way to Model Using EPIC**

EPIC is a computational cognitive architecture that specifies a theory of human performance and a facility to create individual task models constrained by that theory. EPIC compacts decades of psychological theory and findings into a rich set of processors and interactions, including those that model sensory perceptual, motor, cognitive, and memory subsystems of the human mind.

EPIC currently exists as an integration between a computational version of the architecture written in C++ (EPIClib) and a GUI-based simulation environment that uses it, also written in C++ (EPICapp). EPIC only runs on MacOS, and some tasks (e.g., writing virtual tasks, or perceptual encoders) requires knowledge of the C++ programming language.

**EPICpy - A New Way To Do EPIC Modeling Using Python**

EPICpy is a cross-platform Python-based interface to EPIClib that allows programming task devices and perceptual encoders in the Python programming language. However, EPIClib itself is still coded in C++ that is compiled into a Python library using Pybind11.

`This repository contains the source code for EPICpy.`

For more information:

[Detailed EPICpy Documentation](https://travisseymour.github.io/EPICpyDocs/)

Project Sources

* [EPICpy Source Repository](https://github.com/travisseymour/EPICpy) (this repository)
* [EPICpy Documentation Repository](https://github.com/travisseymour/EPICpyDocs)

**<font color="Green"><b>⭐ What's New - Big Changes to EPICpy in the 2023.5.28 Version</b></font>**

The 2023.5.8 version of EPICpy represents some large changes to the repository and codebase:

1. We are no longer creating executables with the [FMan-Build System](https://build-system.fman.io/). The primary reason is the mismatch of using a paid/proprietary system as a major component in an open-source project. In addition, it became cumbersome to create executables for every OS after ever version bump.
2. We are now using [PipX](https://pypa.github.io/pipx/) for distribution and installation. This offers both easier distribution and installation, but the ability for users to upgrade EPICpy in-place.
3. We are no longer using https://cppyy.readthedocs.io/en/latest/ for realtime automatic Python bindings of the C++ EPICLib codebase. Instead, we are compiling Python C-modules for each operating system using [PyBind11](https://pybind11.readthedocs.io/en/stable/index.html). One benefit of this approach is the removal of any need for device and encoder writers to read or write any C++. Now all imports will come from the devicebase support files as standard Python imports.
4. The EPICpy demo models and device-creation support files have been re-written to remove last vestiges of C++ and cppyy references.
5. As a result of the above 3 changes, we are now able to support more operating systems including Linux, MacOS (Intel & M1), and Windows.
6. We've added a built-in editor based on [EPICCoder](https://github.com/travisseymour/epiccoder) that supports syntax-highlighting for EPIC Production Rule files. A right-click menu on the **Normal Output** window allows viewing or editing of the current model's data, production rule file, or Normal Output window contents. When EPICCoder is disabled in settings, EPICpy will instead use to related system defaults.
7. The main menu is now in the same place (atop the Normal Output window) across all versions of EPICpy (previously, the MacOS version was an outlier).
8. It is now possible to *Unload* Visual and Auditory Encoders after they have been loaded.
9. It is no longer possible to switch EPICLib versions, EPICpy now always uses the 2016 version.

