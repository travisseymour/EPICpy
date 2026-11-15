# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import hashlib
import importlib.util
import sys
import types
from pathlib import Path
from typing import Type

from epicpydevicelib.epicpy_auditory_encoder_base import EPICPyAuditoryEncoder
from epicpydevicelib.epicpy_device_base import EpicPyDevice
from epicpydevicelib.epicpy_visual_encoder_base import EPICPyVisualEncoder


def _unique_modname(file: Path) -> str:
    # Unique per content+path+mtime so reloading new code gets a new module
    p = file.resolve()
    h = hashlib.blake2b(digest_size=10)
    h.update(str(p).encode())
    try:
        st = p.stat()
        h.update(str(st.st_mtime_ns).encode())
        h.update(str(st.st_size).encode())
    except OSError:
        pass
    return f"_epic_device_{p.stem}_{h.hexdigest()}"


def load_module(file: Path) -> types.ModuleType:
    file = Path(file)
    if not file.is_file():
        raise FileNotFoundError(file)

    modname = _unique_modname(file)
    spec = importlib.util.spec_from_file_location(modname, file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create spec for {file}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod  # ensure proper relative imports within the file
    spec.loader.exec_module(mod)  # executes the code
    return mod


def unload_module(modname: str) -> None:
    # Best-effort cleanup; let GC handle instances you've released.
    sys.modules.pop(modname, None)


def unload_directory_modules(directory: Path) -> None:
    """
    Remove from sys.modules any modules whose file resides in *directory*.

    This clears cached device-local modules (e.g. graph_maker) so that
    switching devices forces a fresh import from the new device folder.
    """
    resolved = directory.resolve()
    to_remove = [
        name
        for name, mod in sys.modules.items()
        if getattr(mod, "__file__", None) and Path(mod.__file__).resolve().parent == resolved
    ]
    for name in to_remove:
        del sys.modules[name]


# ------------
# EpicPyDevice
# ------------


def find_device_class(mod: types.ModuleType) -> Type[EpicPyDevice]:
    EpicDeviceClass = getattr(mod, "EpicDevice", None)
    if EpicDeviceClass is None or not issubclass(EpicDeviceClass, EpicPyDevice):
        raise ImportError("Module does not define EpicDevice(EpicPyDevice)")
    return EpicDeviceClass


def make_device(file: Path, **ctor_kwargs) -> EpicPyDevice:
    mod = load_module(file)
    Device = find_device_class(mod)
    return Device(**ctor_kwargs), mod.__name__


# -------------------
# EPICPyVisualEncoder
# -------------------


def find_visual_encoder_class(mod: types.ModuleType) -> Type[EPICPyVisualEncoder]:
    EPICVisualEncoderClass = getattr(mod, "VisualEncoder", None)
    if EPICVisualEncoderClass is None or not issubclass(EPICVisualEncoderClass, EPICPyAuditoryEncoder):
        raise ImportError("Module does not define VisualEncoder(EPICPyVisualEncoder)")
    return EPICVisualEncoderClass


def make_avisual_encoder(file: Path, **ctor_kwargs) -> EPICPyVisualEncoder:
    mod = load_module(file)
    Device = find_device_class(mod)
    return Device(**ctor_kwargs), mod.__name__


# -------------------
# EPICPyAuditoryEncoder
# -------------------


def find_auditory_encoder_class(mod: types.ModuleType) -> Type[EPICPyAuditoryEncoder]:
    EPICAuditoryEncoderClass = getattr(mod, "AuditoryEncoder", None)
    if EPICAuditoryEncoderClass is None or not issubclass(EPICAuditoryEncoderClass, EPICPyAuditoryEncoder):
        raise ImportError("Module does not define AuditoryEncoder(EPICPyAuditoryEncoder)")
    return EPICAuditoryEncoderClass


def make_auditory_encoder(file: Path, **ctor_kwargs) -> EPICPyAuditoryEncoder:
    mod = load_module(file)
    Device = find_device_class(mod)
    return Device(**ctor_kwargs), mod.__name__
