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

* [EPICpy Source Repository](https://github.com/travisseymour/EPICpy) (this repository)
* [EPICpy Documentation Repository](https://github.com/travisseymour/EPICpyDocs)


---

<mark>IMPORTANT NOTICE<br>Monday March 24, 2025</mark>
As of version 2025.3.25.1, those who have existing copies of the epicpydevice folder, will need to update one of its files:

- Open epicpydevice/epicpy_device_base.py in a text editor.
- Replace the existing definition of the `write` method with this one:

```python
def write(self, text: str):
    """
    Device write method for text that adds newlines properly. 
    This will be dynamically added to the device object after 
    it has been loaded and instantiated.
    """
    self.parent.write(text, copy_to_trace=True)
```

---



### EPCpy Installation

#### System Requirements for EPICpy

- [git](https://git-scm.com/): Git is a distributed version control system. 
  - **Linux**: You almost certainly have this. Otherwise run `sudo apt install git`.
  - **Windows**: Use the installer at https://git-scm.com/
  - **MacOS**: Use the installer at https://git-scm.com/, or run `xcode-select --install`, or install [Homebrew](https://brew.sh/) and then run `brew install git`.

- [uv](https://docs.astral.sh/uv/): uv is a Python package and project manager.
- [xcb](https://xcb.freedesktop.org/): Library implementing the client-side of the X11 display server protocol. 
  - **Linux Only**: `sudo apt install libxcb-cursor0`

#### Python Requirements for EPICpy

- EPICpy requires Python 3.10 (Linux and MacOS) or Python 3.9 (Windows). You will need the path to the appropriate version of Python. 
  - run `uv python list` and copy the path to the Python version you need, e.g., on my Linux install, I can use `/usr/bin/python3.10`.
  - If you don't see an entry for Python 3.10 (Linux & MacOS) or Python 3.9, you can install the version you need:
    - `uv python install 3.10` (Linux & MacOS) or `uv python install 3.9` (Windows), and then run `uv python list` to jot down the path to Python.

#### Install EPICpy

On Linux & MacOS:

```bash
uv tool install git+https://www.github.com/travisseymour/EPICpy.git --python [PATH_TO_YOUR_PYTHON_310]
```
   
On Windows:

```bash
uv tool install git+https://www.github.com/travisseymour/EPICpy.git --python [PATH_TO_YOUR_PYTHON_39]
```
 
For example,

```bash
# Linux or MacOS
uv tool install git+https://www.github.com/travisseymour/EPICpy.git --python /usr/bin/python3.10
# Windows
uv tool install git+https://www.github.com/travisseymour/EPICpy.git --python AppData\Local\Programs\Python\Python310\python.exe
```

