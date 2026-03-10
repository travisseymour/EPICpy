## EPICpy

### A Python Interface for EPIC Computational Cognitive Modeling

Travis L. Seymour, PhD

[![DOI](https://joss.theoj.org/papers/10.21105/joss.04533/status.svg)](https://doi.org/10.21105/joss.04533)

_Seymour, T. L., (2022). **EPICpy: A Python Interface for EPIC Computational Cognitive Modeling**. Journal of Open Source Software, 7(76), 4533, https://doi.org/10.21105/joss.04533_

---

[![EPICpy Interface](https://travisseymour.github.io/EPICpyDocs/resources/images/custom_layout_choicetask.png)](https://travisseymour.github.io/EPICpyDocs/resources/images/custom_layout_choicetask.png)

**Background - Previous Way to Model Using EPIC**

EPIC is a computational cognitive architecture that specifies a theory of human performance and a facility to create individual task models constrained by that theory. EPIC compacts decades of psychological theory and findings into a rich set of processors and interactions, including those that model sensory perceptual, motor, cognitive, and memory subsystems of the human mind.

EPIC currently exists as an integration between a computational version of the architecture written in C++ (EPIClib) and a GUI-based simulation environment that uses it, also written in C++ (EPICapp). EPIC only runs on MacOS, and some tasks (e.g., writing virtual tasks, or perceptual encoders) requires knowledge of the C++ programming language.

**EPICpy - A New Way To Do EPIC Modeling Using Python**

EPICpy is a cross-platform Python-based interface to EPIClib that allows programming task devices and perceptual encoders in the Python programming language. However, EPIClib itself is still coded in C++ that is compiled into a Python library using Pybind11.

`This repository contains the source code for EPICpy.`

For more information:

[Detailed EPICpy Documentation](https://travisseymour.github.io/EPICpyDocs/)

Project Sources

- [EPICpy Source Repository](https://github.com/travisseymour/EPICpy) (this repository)
- [EPICpy Documentation Repository](https://github.com/travisseymour/EPICpyDocs)

---

### EPCpy Installation

#### System Requirements for EPICpy

- [git](https://git-scm.com/): Git is a distributed version control system.

  - **Linux**: You almost certainly have this. Otherwise run `sudo apt install git`.
  - **Windows**: Use the installer at https://git-scm.com/
  - **MacOS**: Use the installer at https://git-scm.com/, or run `xcode-select --install`, or **[RECOMMENDED]** install [Homebrew](https://brew.sh/) and then run `brew install git`.

- [uv](https://docs.astral.sh/uv/): uv is a Python package and project manager.
- [xcb](https://xcb.freedesktop.org/): Library implementing the client-side of the X11 display server protocol.
  - **Linux Only**: `sudo apt install libxcb-cursor0`

#### Python Requirements for EPICpy

EPICpy requires Python 3.10-3.14 and can be installed on Macos 11+ (Intel or Arm), Linux, and Microsoft Windows version 10+.

#### Install EPICpy

```bash
# uv will automatically install Python if it does not already exist.
uv tool install git+https://www.github.com/travisseymour/EPICpy.git
```

_Or, if you'd prefer to specify the Python version:_

```bash
# Feel free to change 3.12 to 3.10, 3.11, 3.13 or 3.14 if preferred
# If you system lacks the version you specify, uv will automatically install the specified version.
uv tool install git+https://www.github.com/travisseymour/EPICpy.git --python 3.12
```
