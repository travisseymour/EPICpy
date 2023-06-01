import ast
import io
import platform
import re
import os
import shutil
from pathlib import Path

from setuptools import find_packages, setup

DEPENDENCIES = [
    "loguru",
    "pyqt5",
    "QScintilla",
    "python-dateutil",
    "ulid",
    "pingouin",
    "plum-dispatch",
    "ascii_frame",
    "ulid2",
]
EXCLUDE_FROM_PACKAGES = [
    "contrib",
    "docs",
    "tests*",
    "test*",
    "build",
    "epicpy.egg-info",
]
CURDIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURDIR, "ReadMe.md"), "r", encoding="utf-8") as f:
    README = f.read()

if platform.system().lower() == "windows":
    PYTHON_VERSION = ">=3.9,<3.10"  # have yet to figure out how to compile epliclib with 3.10+ on windows using MSVC++ 2019
    epiclib_file = "epiclib.pyd"
elif platform.system().lower() == "linux":
    Path("epicpy", "epiclib", "epiclib.so").unlink(missing_ok=True)
    shutil.copyfile(
        Path("epicpy", "epiclib", "epiclib_linux.so"),
        Path("epicpy", "epiclib", "epiclib.so"),
    )
    PYTHON_VERSION = ">=3.10,<3.11"
    epiclib_file = "epiclib.so"
elif platform.system().lower() == "darwin":
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
        f"ERROR: No epiclib library for OS={platform.system()}. Unable to continue setup."
    )


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
    author="Travis Seymour",
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
    entry_points={
        "gui_scripts": ["EPICpy=epicpy.main:main"],
    },
    zip_safe=False,
    install_requires=DEPENDENCIES,
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
