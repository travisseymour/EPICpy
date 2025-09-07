import importlib
import importlib.util
import os
import platform
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

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

uv tool uninstall epicpy

Ultimately, you can (re)install EPICpy using uv (replace 3.13 which any supported version):

uv tool install git+https://github.com/travisseymour/epicpy.git --python 3.13
"""

_console = Console()


def _sysctl(name: str) -> str | None:
    try:
        out = subprocess.run(["sysctl", "-n", name], capture_output=True, text=True, check=False)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def _user_cache_dir() -> Path:
    """
    Cross-platform per-user cache dir for EPICpy.
    Linux/macOS: ~/.cache/epicpy/epiclib
    Windows: %LOCALAPPDATA%\\epicpy\\epiclib
    """
    system = platform.system().lower()
    if system == "windows":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    else:
        base = os.path.expanduser("~/.cache")
    p = Path(base) / "epicpy" / "epiclib"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _find_member_in_zip(zf: zipfile.ZipFile, basename: str) -> str | None:
    """
    Return the first member path in the zip whose basename matches "basename".
    """
    for name in zf.namelist():
        if Path(name).name == basename:
            return name
    return None


def _extract_member(zf: zipfile.ZipFile, member: str, dest_dir: Path) -> Path:
    """
    Extract a single member to dest_dir, preserving basename.
    Always overwrite to avoid stale copies.
    """
    dest_path = dest_dir / Path(member).name
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zf.open(member) as src, open(dest_path, "wb") as dst:
        dst.write(src.read())

    # On POSIX, ensure the .so is executable by the user
    if os.name == "posix":
        try:
            st = os.stat(dest_path)
            os.chmod(dest_path, st.st_mode | stat.S_IXUSR)
        except Exception:
            pass

    return dest_path


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
        # Determine arch suffix
        arm64 = _sysctl("hw.optional.arm64")
        if arm64 == "1":
            extra = "_arm"
        else:
            extra = ""
        # macOS builds use .so in this project
        if py_ver == "3.10":
            modname = f"epiclib_macos{extra}_310.so"
        elif py_ver == "3.11":
            modname = f"epiclib_macos{extra}_311.so"
        elif py_ver == "3.12":
            modname = f"epiclib_macos{extra}_312.so"
        elif py_ver == "3.13":
            modname = f"epiclib_macos{extra}_313.so"
        else:
            _console.print(Markdown(_py_ver_err_msg.format(py_ver, SUPPORTED_PYTHONS)))
            sys.exit(1)

    else:
        _console.print(
            Markdown(
                f"## EPICpy Installation Error\n\n"
                f'EPICpy is not supported on "{system}". '
                f"It is only supported on Linux, MacOS, and Windows."
            )
        )
        sys.exit(1)

    _console.print(f"[green]Using {modname}[/green]")

    try:
        zip_path = get_resource("epiclib", "", "epiclib_versions.zip")
    except Exception:
        zip_path = None

    if not isinstance(zip_path, Path):
        raise FileNotFoundError(
            "Could not locate 'epiclib_versions.zip' via get_resource. " "Ensure it is included in your package data."
        )

    cache_dir = _user_cache_dir()
    with zipfile.ZipFile(zip_path, "r") as zf:
        member = _find_member_in_zip(zf, modname)
        if not member:
            raise FileNotFoundError(
                f"'{modname}' not found inside {zip_path.name}. " "Verify the zip contains the expected binary."
            )
        module_path = _extract_member(zf, member, cache_dir)

    cache_dir = _user_cache_dir()
    with zipfile.ZipFile(zip_path, "r") as zf:
        member = _find_member_in_zip(zf, modname)
        if not member:
            raise FileNotFoundError(
                f"'{modname}' not found inside {zip_path.name}. " "Verify the zip contains the expected binary."
            )
        module_path = _extract_member(zf, member, cache_dir)

        # --- NEW: On Windows, also extract all sibling DLLs next to the .pyd ---
        if system == "windows":
            member_parent = Path(member).parent  # folder inside the zip ('' if at root)
            for name in zf.namelist():
                p = Path(name)
                if p.parent == member_parent and p.suffix.lower() == ".dll":
                    _extract_member(zf, name, cache_dir)

            # Ensure the Windows loader will search this directory for deps
            try:
                os.add_dll_directory(str(cache_dir))
            except Exception:
                pass

    # Load it as a module named 'epicpy.epiclib.epiclib'
    spec = importlib.util.spec_from_file_location("epicpy.epiclib.epiclib", str(module_path))

    # Load it as a module named 'epicpy.epiclib.epiclib'
    spec = importlib.util.spec_from_file_location("epicpy.epiclib.epiclib", str(module_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {modname} from {module_path}")
    print(f"Loading model '{modname}' from path '{module_path}'")
    module = importlib.util.module_from_spec(spec)
    sys.modules["epicpy.epiclib.epiclib"] = module
    spec.loader.exec_module(module)

    # Make it a real attribute of the parent module
    import epicpy.epiclib

    epicpy.epiclib.epiclib = module

    # Test the dynamic import
    try:
        from epicpy.epiclib.epiclib import geometric_utilities as GU  # noqa: F401

        print("Test import from epicpy.epiclib.epiclib successful!")
    except Exception as e:
        raise ImportError(f"Test import from epicpy.epiclib.epiclib failed: {e}")


_load_platform_module()
