from epicpy.utils.resource_utils import get_resource


import importlib
import platform
import sys

from epicpy.utils.resource_utils import get_resource


def _load_platform_module():
    system = platform.system().lower()

    if system == "windows":
        modname = "epiclib.pyd"
    elif system == "linux":
        modname = "epiclib_linux.so"
    elif system == "darwin":
        if "ARM" in platform.uname().version.upper():
            modname = "epiclib_macos_arm.so"
        else:
            modname = "epiclib_macos.so"
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
