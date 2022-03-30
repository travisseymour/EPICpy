import os
from collections import namedtuple
from pathlib import Path
from typing import Optional

from fbs_runtime.application_context.PySide2 import ApplicationContext
from loguru import logger as log

from epiclibfiles import get_epiclib_files

os.environ["CLING_STANDARD_PCH"] = "none"

EPICLIB_INFO = namedtuple("EPICLIB_INFO", "info libname headerpath epiclib_files")


def setup_cppyy(context: ApplicationContext) -> Optional[EPICLIB_INFO]:
    # before we can even import cppyy, we need to setup an env variable
    os.environ["CPPYY_API_PATH"] = str(Path(context.get_resource("CPyCppyy")).resolve())
    import cppyy

    # setup some cppyy paths
    tstreamer_header = context.get_resource(
        "cppyy_backend", "include", "TStreamerInfo.h"
    )
    cppyy.include(tstreamer_header)
    cppyy.add_include_path(context.get_resource("CPyCppyy"))
    cppyy.add_include_path(context.get_resource("python3.9"))

    info, libname, headerpath, epiclib_files = get_epiclib_files(context)

    log.debug(f"Attempting to load EPICLib file {libname}")
    log.debug(f"Using EPICLib header files in {headerpath}")

    try:
        cppyy.load_library(context.get_resource(f"epiclib/{libname}"))
        return EPICLIB_INFO(info, libname, headerpath, epiclib_files)
    except FileNotFoundError as e:
        log.error(
            f"Trying to load EPICLib library 'epiclib/{libname}' "
            f"into cppyy, but file not found!"
        )
        return None
