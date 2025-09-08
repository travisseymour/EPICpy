from __future__ import annotations

import importlib
import importlib.util
from importlib.metadata import version as _dist_version, PackageNotFoundError, packages_distributions

from typing import Optional
import ctypes
import os
import platform
import stat
import subprocess
import sys
import time
import zipfile
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

from epicpy.utils.resource_utils import get_resource

_console = Console()

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@  PREVENT SILENT CRASH @@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# Crash/exception logging (Windows native crashes included)
import faulthandler, signal


def _install_crash_logging(log_path: str = None) -> None:
    if log_path is None:
        # per-Python/per-version log inside cache root
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
        log_path = str(
            Path(base) / "epicpy" / "epiclib" / f"crash-py{sys.version_info.major}{sys.version_info.minor}.log"
        )
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    f = open(log_path, "w", buffering=1, encoding="utf-8")
    faulthandler.enable(file=f, all_threads=True)
    # Ctrl+Break prints stacks on Windows
    try:
        faulthandler.register(getattr(signal, "SIGBREAK"), file=f, all_threads=True)
    except Exception:
        pass

    # Also capture uncaught Python exceptions
    def _excepthook(t, e, tb):
        import traceback

        traceback.print_exception(t, e, tb, file=f)

    sys.excepthook = _excepthook


_install_crash_logging()


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@  SETUP VERSION ACCESS @@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


def _dist_name_for(package: str) -> str:
    # Map import package -> distribution name (handles dash/underscore differences)
    top = package.split(".")[0]
    return packages_distributions().get(top, [top])[0]


def _read_pyproject_version(start: Path) -> Optional[str]:
    cand = Path(__file__).parent.parent / "pyproject.toml"
    if cand.is_file():
        try:
            try:
                import tomllib as toml  # Python 3.11+
            except ModuleNotFoundError:  # Python 3.10
                import tomli as toml  # pip install tomli for dev/runtime
            with cand.open("rb") as fh:
                data = toml.load(fh)
            v = (data.get("project") or {}).get("version")
            if isinstance(v, str) and v.strip():
                return v.strip()
        except Exception:
            # Ignore and fall through
            pass
    _console.print(f"[red]UNABLE TO READ PYPROJECT VERSION![/red]")
    return None


def get_version(package: str) -> str:
    try:
        return _dist_version(_dist_name_for(package))
    except PackageNotFoundError:
        v = _read_pyproject_version(Path(__file__).resolve())
        return v or "0.0.0+local"


__version__ = get_version(__package__)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@  SETUP EPICLIB VERSION @@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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


def _sysctl(name: str) -> str | None:
    try:
        out = subprocess.run(["sysctl", "-n", name], capture_output=True, text=True, check=False)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def _cache_root() -> Path:
    """
    Cross-platform per-user cache root for EPICpy.
    Linux/macOS: ~/.cache/epicpy/epiclib
    Windows: %LOCALAPPDATA%\\epicpy\\epiclib
    """
    system = platform.system().lower()
    if system == "windows":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    else:
        base = os.path.expanduser("~/.cache")
    root = Path(base) / "epicpy" / "epiclib"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _versioned_cache_dir(zip_path: Path) -> Path:
    """Make a per-python, per-app-version, per-zip-mtime cache directory."""
    py_tag = f"py{sys.version_info.major}{sys.version_info.minor}"
    app_ver = __version__ if isinstance(__version__, str) else "0.0.0"
    try:
        mtime_ns = zip_path.stat().st_mtime_ns
    except Exception:
        mtime_ns = 0
    d = _cache_root() / f"{py_tag}-{app_ver}-{mtime_ns:x}"
    d.mkdir(parents=True, exist_ok=True)
    return d


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
    - Skip writing if identical size already exists.
    - If overwrite is blocked (locked DLL), fall back to a per-process subdir.
    - Retry briefly to dodge transient locks (e.g., AV scanners).
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    target_name = Path(member).name
    dest_path = dest_dir / target_name

    # Skip if same size (cheap identical check)
    try:
        info = zf.getinfo(member)
        if dest_path.exists() and dest_path.stat().st_size == info.file_size:
            return dest_path
    except KeyError:
        pass

    # Try to remove existing file if present
    if dest_path.exists():
        try:
            os.chmod(dest_path, stat.S_IWRITE | stat.S_IREAD)
            dest_path.unlink()
        except PermissionError:
            # Fall back to unique per-process subdir to avoid locked files
            alt_dir = dest_dir / f"run-{os.getpid()}"
            alt_dir.mkdir(parents=True, exist_ok=True)
            dest_path = alt_dir / target_name

    # Small retry loop for transient PermissionError
    last_exc = None
    for _ in range(3):
        try:
            with zf.open(member) as src, open(dest_path, "wb") as dst:
                dst.write(src.read())
            last_exc = None
            break
        except PermissionError as e:
            last_exc = e
            time.sleep(0.25)
    if last_exc:
        raise last_exc

    # On POSIX, ensure the .so is executable by the user
    if os.name == "posix":
        try:
            st = os.stat(dest_path)
            os.chmod(dest_path, st.st_mode | stat.S_IXUSR)
        except Exception:
            pass

    return dest_path


def _probe_import_in_subprocess(module_path: Path, fqname: str) -> None:
    """
    Try importing the extension in a fresh Python process.
    Captures crashes and surfaces the real error to the parent.
    """
    code = f"""
import os, sys, ctypes, importlib.util, traceback, faulthandler
faulthandler.enable(all_threads=True)
try:
    os.add_dll_directory(r"{module_path.parent.resolve()}")
except Exception:
    pass
# Preload all DLLs to surface dependency errors
for name in sorted(os.listdir(r"{module_path.parent.resolve()}")):
    if name.lower().endswith(".dll"):
        try:
            ctypes.WinDLL(os.path.join(r"{module_path.parent.resolve()}", name))
        except OSError as e:
            traceback.print_exc()
            sys.exit(1)
try:
    spec = importlib.util.spec_from_file_location("{fqname}", r"{module_path.resolve()}")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    print("SUBPROCESS_IMPORT_OK")
except Exception:
    traceback.print_exc()
    sys.exit(1)
"""
    r = subprocess.run([sys.executable, "-X", "faulthandler", "-c", code], capture_output=True, text=True)
    if r.returncode != 0 or "SUBPROCESS_IMPORT_OK" not in r.stdout:
        raise ImportError(
            "Subprocess import of epiclib failed on this Python version.\n" f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
        )


def _load_platform_module():
    major = sys.version_info.major
    minor = sys.version_info.minor
    py_ver = f"{major}.{minor}"
    system = platform.system().lower()
    extra = ""

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

    _console.print(f"[green]Using {modname} ({py_ver}, {system}{extra})[/green]")

    # Locate the zip in package resources
    try:
        zip_path = get_resource("epiclib", "", "epiclib_versions.zip")
    except Exception:
        zip_path = None

    if not isinstance(zip_path, Path):
        raise FileNotFoundError(
            "Could not locate 'epiclib_versions.zip' via get_resource. Ensure it is included in your package data."
        )

    # Build a versioned cache dir (prevents overwriting in-use DLLs)
    cache_dir = _versioned_cache_dir(zip_path)
    print(f"library cache_dir: {str(cache_dir)}")

    # Extract the chosen module and (on Windows) sibling DLLs
    with zipfile.ZipFile(zip_path, "r") as zf:
        member = _find_member_in_zip(zf, modname)
        if not member:
            raise FileNotFoundError(
                f"'{modname}' not found inside {zip_path.name}. Verify the zip contains the expected binary."
            )

        # Extract the module
        module_path = _extract_member(zf, member, cache_dir)

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
