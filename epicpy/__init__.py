from epicpy.utils.resource_utils import get_resource


import importlib
import platform
import sys

from epicpy.utils.resource_utils import get_resource


def _load_platform_module():
    major = sys.version_info.major
    minor = sys.version_info.minor
    py_ver = f'{major}.{minor}'
    system = platform.system().lower()

    if system == "windows":
        modname = "epiclib.pyd"
    elif system == "linux":
        if py_ver == '3.10':
            modname = "epiclib_linux_310.so"
        elif py_ver == '3.11':
            modname = "epiclib_linux_311.so"
        elif py_ver == '3.12':
            modname = "epiclib_linux_312.so"
        elif py_ver == '3.13':
            modname = "epiclib_linux_313.so"
        else:
            modname = "epiclib_linux_310.so"
    elif system == "darwin":
        extra = "_arm" if "ARM" in platform.uname().version.upper() else ""
        if py_ver == '3.10':
            modname = f"epiclib_macos{extra}_310.so"
        elif py_ver == '3.11':
            modname = f"epiclib_macos{extra}_311.so"
        elif py_ver == '3.12':
            modname = f"epiclib_macos{extra}_312.so"
        elif py_ver == '3.13':
            modname = f"epiclib_macos{extra}_313.so"
        else:
            modname = f"epiclib_macos{extra}_310.so"
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")

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
