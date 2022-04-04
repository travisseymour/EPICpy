import platform
import subprocess

from loguru import logger as log
from pathlib import Path
import os
import sys
import shutil

"""
Copy required cppyy-related files into resources folder (for development)
Really only needed once per OS when changing Python versions
1 python3.X folder (one with C sources like Python.h)
2 cppyy_backend folder (likely one installed into virtual environment)
3 CPyCppyy folder (likely one installed into virtual environment)
"""

OS = platform.system()
PV = '.'.join(platform.python_version().split('.')[:2])

log.remove()
log.add(sys.stderr, format="{message}", level='INFO')

log.info('ONETIME RESOURCE SETUP FOR EPICPY')
log.info('---------------------------------')
log.info('Run when:')
log.info('1. you change Python source or version')
log.info('2. you change or reinstall cppyy (or any of it\'s components)')
log.info('3. you are setting up a dev environment on another machine or OS')
log.info('')
log.info('====================')
log.info(f'@@@@ Operating System Type: {OS} @@@@')
log.info(f'@@@@ Python Version: {PV=} @@@@')
log.info('====================')
log.info('')
# Derive VENV folder name
python_in_use = subprocess.check_output("which python".split(" "))
VIRTUAL_ENVIRONMENT_FOLDER = Path(
    python_in_use.decode().splitlines(False)[0]
).parent
if VIRTUAL_ENVIRONMENT_FOLDER.name == "bin":
    VIRTUAL_ENVIRONMENT_FOLDER = VIRTUAL_ENVIRONMENT_FOLDER.parent

if not VIRTUAL_ENVIRONMENT_FOLDER.is_dir():
    log.error(
        f"Derived virtual environment folder {str(VIRTUAL_ENVIRONMENT_FOLDER)} "
        f"does not appear to exist or is not readable."
    )
    sys.exit()

# source locations
log.debug(f"{VIRTUAL_ENVIRONMENT_FOLDER=}")
# getting python3X_folder can be a little tricky...if so, hard code yourself!!??
#    It's the one that contains Python.h. Location may depend on
#    how you set up your dev environment
python_executable = Path(VIRTUAL_ENVIRONMENT_FOLDER, "bin", f"python{PV}")
log.debug(f"{python_executable=}")
log.debug(f"{python_executable.is_symlink()=}")
if python_executable.is_symlink():
    real_python_executable = Path(os.path.realpath(python_executable))
else:
    real_python_executable = python_executable
log.debug(f"{real_python_executable=}")

python3X_folder = Path(real_python_executable.parent.parent,
                       "include", f"python{PV}").resolve()
log.debug(f"{python3X_folder=}")

cppyy_backend_folder = Path(
    VIRTUAL_ENVIRONMENT_FOLDER, "lib", f"python{PV}", "site-packages", "cppyy_backend"
)
CPyCppyy_folder = Path(
    VIRTUAL_ENVIRONMENT_FOLDER, "include", "site", f"python{PV}", "CPyCppyy"
)

missing = [
    folder.name
    for folder in (python3X_folder, cppyy_backend_folder, CPyCppyy_folder)
    if not folder.is_dir()
]

for folder in (python3X_folder, cppyy_backend_folder, CPyCppyy_folder):
    log.debug(f"{folder.is_dir()=} {folder.is_symlink()=} {folder}")

log.info("The following source folders must exist in order to continue:")
log.info(f"python folder: {str(python3X_folder)}")
log.info(f"cppyy_backend folder: {str(cppyy_backend_folder)}")
log.info(f"CPyCppyy folder: {str(CPyCppyy_folder)}")
if missing:
    log.error(f"Unable to find these required source folders: {','.join(missing)}")
    sys.exit()
else:
    log.info("All source folders found!")

# target locations
project_resources_folder = Path("src", "main", "resources",
                                {"Linux": "linux", "Darwin": "mac"}[OS])

missing = [
    folder.name for folder in (project_resources_folder,) if not folder.is_dir()
]
log.info("The following target folders must exist in order to continue:")
log.info(f"project resources folder: {str(project_resources_folder)}")
if missing:
    log.error(f"Unable to find these target source folders: {','.join(missing)}")
    # sys.exit()
else:
    log.info("All target folders found!")

# Destination Folders
python3X_dest = Path(project_resources_folder, f"python{PV}")
cppyy_backend_dest = Path(project_resources_folder, "cppyy_backend")
CPyCppyy_dest = Path(project_resources_folder, "CPyCppyy")

# Update required files in project resources folder

log.info("Removing old destination folders in project resources")
for folder in (python3X_dest, cppyy_backend_dest, CPyCppyy_dest):
    if not folder.is_dir():
        continue
    msg = f"removing {str(folder)}..."
    try:
        shutil.rmtree(folder)
        msg += "FOUND and REMOVED"
        log.info(msg)
    except FileNotFoundError as e:
        msg += f"NOT FOUND ({e})"
        log.warning(msg)

# Copy sources to target if they already exist:
log.info("Recreating destination folders in project resources")
for source, dest in zip(
    (python3X_folder, cppyy_backend_folder, CPyCppyy_folder),
    (python3X_dest, cppyy_backend_dest, CPyCppyy_dest),
):
    if not source.is_dir():
        log.warning(f'ignoring {source}, folder not found.')
        continue
    msg = f"copying {str(source)} to {str(dest)}..."
    try:
        shutil.copytree(source, dest)
        msg += "SUCCESSFUL"
        log.info(msg)
    except FileNotFoundError as e:
        msg += f"FAILED ({e})"
        log.error(msg)


sys.exit(0)
