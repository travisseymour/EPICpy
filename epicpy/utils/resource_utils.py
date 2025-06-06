from importlib.resources import files, as_file
from pathlib import Path


def get_resource(*args: str) -> Path:
    """
    Constructs and returns the full absolute path to a resource within 'epicpy/resources'.

    Args:
        *args: A sequence of strings representing the relative path components
               within 'epicpy/resources', e.g., ("other", "devices.zip").

    Returns:
        pathlib.Path: An absolute Path object pointing to the resource that works
                      during development and when packaged.

    Raises:
        FileNotFoundError: If the resource does not exist.
        RuntimeError: If an error occurs while resolving the resource path.
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
