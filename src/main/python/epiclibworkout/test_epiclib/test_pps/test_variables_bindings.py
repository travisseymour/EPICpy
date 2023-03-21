from cppinclude import epiclib_include
import cppyy
from loguru import logger as log
from pprint import pprint
from apputils import LIBNAME

cppyy.load_library(LIBNAME)

epiclib_include("Framework classes/Parameter.h")
epiclib_include("Utility Classes/Symbol.h")
epiclib_include("Utility Classes/Symbol_utilities.h")
epiclib_include("Utility Classes/Output_tee.h")
epiclib_include("Utility Classes/Geometry.h")
epiclib_include("Utility Classes/Random_utilities.h")
epiclib_include("Standard_Symbols.h")

epiclib_include("PPS/Variables and Bindings/Variables.h")
epiclib_include("PPS/Variables and Bindings/Overlap.h")
epiclib_include("PPS/Variables and Bindings/Binding_pair.h")
epiclib_include("PPS/Variables and Bindings/Binding_set.h")
epiclib_include("PPS/Variables and Bindings/Binding_set_list.h")

from cppyy.gbl import Geometry_Utilities as GU
from cppyy.gbl import Symbol, concatenate_to_Symbol
from cppyy.gbl import is_variable, is_wildcard, full_wildcard_name


class TestVariableUnboundMethods:
    def test_is_variable(self):
        assert is_variable(Symbol('?fixation'))
        assert not is_variable(Symbol('fixation'))
        assert not is_variable(Symbol('???'))
