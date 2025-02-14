import ast
import io
import platform
import re
import os
import shutil
from pathlib import Path

from setuptools import find_packages, setup

'''
NOTES:
- Currently using Python 3.10 on linux and macos, but Python 3.9 on Win10
- Currently, the devices in fullbindings are the ones that work
- Fix PyQt6/PySide6 xcb plugin error on Linux by installing: 
  sudo apt install libxcb-cursor0
'''

if platform.system() == 'Darwin' and platform.mac_ver()[0] < '12.0.0':
    qt_package = 'PySide2==5.15.2.1'
else:
    qt_package =  'PySide6==6.8.1.1'  # requires MacOS version 11 or higher

DEPENDENCIES = [
    "loguru==0.7.3",
    "qtpy==2.4.2",
    qt_package,
    "python-dateutil==2.9.0.post0",
    "ulid==1.1",
    "ulid2==0.3.0",
    "numpy==2.0.1",
    "scipy==1.13.1",
    "pingouin==0.5.5",
    "plum-dispatch==2.0.1",
    "ascii_frame==0.0.1",
    "pandas==2.2.3",
    "pyqtdarktheme==2.1.0",
    "fastnumbers==5.1.1"
]
# install these with `pip install .[dev]`
DEVELOPMENT_DEPENDENCIES = [
    [
        "black>=23.3.0",
        "plumbum>=1.8.1",
        "pytest>=7.2.2",
        "qt6-tools==6.4.3.1.3"
    ]
]
EXCLUDE_FROM_PACKAGES = [
    "contrib",
    "docs",
    "tests*",
    "test*",
    "build",
    "epicpy.egg-info"
]

CURDIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURDIR, "ReadMe.md"), "r", encoding="utf-8") as f:
    README = f.read()

if platform.system().lower() == "windows":
    print('setup.py running on Windows.')
    PYTHON_VERSION = ">=3.9,<3.10"
    epiclib_file = "epiclib.pyd"
elif platform.system().lower() == "linux":
    print('setup.py running on Linux.')
    Path("epicpy", "epiclib", "epiclib.so").unlink(missing_ok=True)
    shutil.copyfile(
        Path("epicpy", "epiclib", "epiclib_linux.so"),
        Path("epicpy", "epiclib", "epiclib.so"),
    )
    PYTHON_VERSION = ">=3.10,<3.11"
    epiclib_file = "epiclib.so"
elif platform.system().lower() == "darwin":
    print('setup.py running on MacOS.')
    Path("epicpy", "epiclib", "epiclib.so").unlink(missing_ok=True)
    if "ARM" in os.uname().version.upper():
        shutil.copyfile(
            Path("epicpy", "epiclib", "epiclib_macos_arm.so"),
            Path("epicpy", "epiclib", "epiclib.so"),
        )
    else:
        shutil.copyfile(
            Path("epicpy", "epiclib", "epiclib_macos.so"),
            Path("epicpy", "epiclib", "epiclib.so"),
        )
    PYTHON_VERSION = ">=3.10,<3.11"
    epiclib_file = "epiclib.so"
else:
    raise NotImplementedError(
        f"ERROR: No epiclib library for OS={platform.system()}. Unable to continue EPICpy setup."
    )

# Choose entry point type based on platform
if platform.system() == "Windows":
    entry_point_key = "console_scripts"
else:
    entry_point_key = "gui_scripts"

def get_version():
    main_file = os.path.join(CURDIR, "epicpy", "constants", "version.py")
    _version_re = re.compile(r"__version__\s+=\s+(?P<version>.*)")
    with open(main_file, "r", encoding="utf8") as f:
        match = _version_re.search(f.read())
        version = match.group("version") if match is not None else '"unknown"'
    return str(ast.literal_eval(version))


setup(
    name="epicpy",
    version=get_version(),
    author="Travis L. Seymour, PhD",
    author_email="nogard@ucsc.edu",
    description="Python interface to the EPIC computational cognitive architecture simulation environment.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/travisseymour/EPICpy",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    package_data={"": [epiclib_file]},
    keywords=[],
    scripts=[],

    # entry_points={
    #     "gui_scripts": ["EPICpy=epicpy.main:main"],
    #},

    entry_points={
        entry_point_key: ["EPICpy=epicpy.main:main", "epicpy=epicpy.main:main"],
    },

    zip_safe=False,
    install_requires=DEPENDENCIES,
    extras_require={
        "dev": DEVELOPMENT_DEPENDENCIES
    },
    test_suite="",
    python_requires=PYTHON_VERSION,
    # license and classifier list:
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    license="License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
    ],
    # vvv these 2 lines are required to pull in the resources' folder.
    #     I think essentially this causes setup.py to pull in ANYTHING you
    #     have added to git!
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
)
