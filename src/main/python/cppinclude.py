import cppyy
from apputils import CONTEXT, HEADERPATH


def epiclib_include(epiclib_header_file: str):
    """
    replacement for cppyy.include(CONTEXT.get_resource(epiclib_header_file)).
    NOTE: header_file needs to start BENEATH the EPICLib folder.
    So
    '/Utility Classes/Symbol.h', or 'Standard_Symbols.h'
    and **NOT**
    'EPICLib/Utility Classes/Symbol.h', or 'EPICLib/Standard_Symbols.h'
    """

    cppyy.include(
        CONTEXT.get_resource(f"{HEADERPATH}/{epiclib_header_file.lstrip('/')}")
    )


def cpp_include(header_file: str):
    """
    replacement for cppyy.include(CONTEXT.get_resource(header_file)).
    *** DO NOT USE FOR EPICLIB HEADER FILES!! ***
    """

    cppyy.include(CONTEXT.get_resource(header_file))
