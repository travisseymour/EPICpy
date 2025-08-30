from epicpy.utils.resource_utils import get_resource

import importlib
import platform
import sys
from rich.console import Console
from rich.markdown import Markdown

from epicpy.utils.resource_utils import get_resource

SUPPORTED_PYTHONS = ">=3.10;<3.14"

_py_ver_err_msg = """
## EPICpy Installation Error

There was an error loading EPICpy's epiclib library for Python {}. 
Only Python versions {} are supported. If you already have
EPICpy installed using an unsupported version of python,
you can uninstall it using uv, e.g.:

```bash
uv tool uninstall epicpy
```

Ultimately, you can (re)install EPICpy using uv (replace 3.13 which any supported version):

```bash
uv tool install git+https://github.com/travisseymour/epicpy.git --python 3.13
```
"""

_console = Console()


def _load_platform_module():
    major = sys.version_info.major
    minor = sys.version_info.minor
    py_ver = f"{major}.{minor}"
    system = platform.system().lower()

    if system == "windows":
        if py_ver == "3.10":
            modname = "epiclib_windows_310.pyd"
        elif py_ver == "3.11":
            modname = "epiclib_windows_311.pyd"
        elif py_ver == "3.12":
            modname = "epiclib_windows_312.pyd"
        elif py_ver == "3.13":
            modname = "epiclib_windows_313.pyd"
        else:
            _console.print(Markdown(_py_ver_err_msg.format(py_ver, SUPPORTED_PYTHONS)))
            sys.exit(1)
    elif system == "linux":
        if py_ver == "3.10":
            modname = "epiclib_linux_310.so"
        elif py_ver == "3.11":
            modname = "epiclib_linux_311.so"
        elif py_ver == "3.12":
            modname = "epiclib_linux_312.so"
        elif py_ver == "3.13":
            modname = "epiclib_linux_313.so"
        else:
            _console.print(Markdown(_py_ver_err_msg.format(py_ver, SUPPORTED_PYTHONS)))
            sys.exit(1)
    elif system == "darwin":
        if py_ver == "3.10":
            modname = f"epiclib_macos_310.so"
        elif py_ver == "3.11":
            modname = f"epiclib_macos_311.so"
        elif py_ver == "3.12":
            modname = f"epiclib_macos_312.so"
        elif py_ver == "3.13":
            modname = f"epiclib_macos_313.so"
        else:
            _console.print(Markdown(_py_ver_err_msg.format(py_ver, SUPPORTED_PYTHONS)))
            sys.exit(1)
    else:
        _console.print(
            Markdown(
                f"## EPICpy Installation Error\n"
                f"\n"
                f'EPICpy is not supported on "{system}". '
                f"It is only supported on Linux, MacOS, and Windows."
            )
        )
        sys.exit(1)

    _console.print(f"[green]Using {modname}[/green]")

    # Get the full path to the correct binary from resources
    module_path = get_resource("epiclib", modname)

    # Load it as a module named 'epiclib'
    spec = importlib.util.spec_from_file_location("epicpy.epiclib.epiclib", str(module_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {modname}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["epicpy.epiclib.epiclib"] = module
    spec.loader.exec_module(module)

    # Make it a real attribute of the parent module
    import epicpy.epiclib

    epicpy.epiclib.epiclib = module

    # Test the dynamic import
    try:
        from epicpy.epiclib.epiclib import geometric_utilities as GU

        print("Test import from epicpy.epiclib.epiclib successful!")
    except Exception as e:
        raise ImportError(f"Test import from epicpy.epiclib.epiclib failed: {e}")


_load_platform_module()
