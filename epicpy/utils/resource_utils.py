# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from importlib.resources import as_file, files
from pathlib import Path


def get_resource(*args: str) -> Path:
    """
    Constructs and returns the full absolute path to a resource within 'epicpy/resources'.
    """
    try:
        # Base directory for resources in the package
        base = files("epicpy").joinpath("resources")

        # Construct the resource path relative to the base
        resource_path = base.joinpath(*args)

        # Ensure the resource path is accessible as a file
        with as_file(resource_path) as resolved_path:
            return Path(resolved_path).resolve()  # Ensure the path is absolute
    except FileNotFoundError:
        raise FileNotFoundError(f"Resource not found: {'/'.join(args)}")
    except Exception as e:
        raise RuntimeError(f"Error accessing resource: {e}")
