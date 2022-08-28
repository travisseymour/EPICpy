import platform
from pathlib import Path

from fbs_runtime.application_context.PyQt5 import ApplicationContext

import config
import pandas as pd
from collections import namedtuple

OS = platform.system()
EPICLIB_INFO = namedtuple("EPICLIB_INFO", "info libname headerpath epiclib_files")


def get_epiclib_files(context: ApplicationContext) -> EPICLIB_INFO:
    """
    type(info)=<class 'pandas.core.series.Series'>
    type(libname)=<class 'str'>
    type(headerpath)=<class 'str'>
    Determine the appropriate EPIClib files for the current OS,
    return this info as a pandas dataframe
    """

    epiclib_files = [
        dict(zip(("libdate", "filename"), file.stem.split("_")[1:] + [file.name]))
        for file in Path(context.get_resource("epiclib")).glob("*.*")
        if file.suffix in (".dylib", ".so", ".dll")
    ]
    epiclib_files = pd.DataFrame(epiclib_files)
    epiclib_files["libdate"] = epiclib_files["libdate"].astype(int)
    epiclib_files["code"] = [
        {20141128: 735565, 20141117: 735565, 20160628: 736143}[libdate]
        for libdate in epiclib_files.libdate
    ]

    """
    E.g. for Linux, epiclib_files should be:
        libdate             filename    code
    0  20160628  libEPIC_20160628.so  736143
    1  20141128  libEPIC_20141128.so  735565
    """

    if config.app_cfg.epiclib_version:
        # if app version isn't blank, then we are in the middle of switching version.
        epiclib_version = int(config.app_cfg.epiclib_version)
        config.app_cfg.epiclib_version = (
            ""  # reset so next time device value will be used
        )
        config.app_cfg.auto_load_last_device = True
    elif config.device_cfg.epiclib_version:
        epiclib_version = int(config.device_cfg.epiclib_version)
    else:
        # this is likely the latest (i.e., '') from the default device config
        epiclib_version = 0

    try:
        # choose specified epiclib version
        info = epiclib_files[epiclib_files["libdate"] == epiclib_version].iloc[-1]
        libname = info.filename
        headerpath = f"EPICLib_{info.code}"
    except IndexError:
        # epiclib_version is null, choose the newest version
        info = epiclib_files.sort_values("libdate", ascending=True).iloc[-1]
        libname = info.filename
        headerpath = f"EPICLib_{info.code}"

    return EPICLIB_INFO(info, libname, headerpath, epiclib_files)
