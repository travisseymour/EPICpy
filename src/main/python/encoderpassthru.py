"""
This file is part of EPICpy, Created by Travis L. Seymour, PhD.

EPICpy is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

EPICpy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Foobar.
If not, see <https://www.gnu.org/licenses/>.
"""

import cppyy
from apputils import LIBNAME
from cppinclude import epiclib_include

# ------------------------------------------------------
# Load Various Include files and objects we will need
# The location of the library depends on OS, this is
# figured out in main.py which sets apputils.LIBNAME
# so that the correctly library can be loaded when this
# module is imported.
# ------------------------------------------------------


cppyy.load_library(LIBNAME)

epiclib_include("Framework classes/Auditory_encoder_base.h")
epiclib_include("Framework classes/Visual_encoder_base.h")
epiclib_include("Framework classes/Output_tee_globals.h")
epiclib_include("Utility Classes/Symbol.h")
epiclib_include("Standard_Symbols.h")

from cppyy.gbl import Visual_encoder_base, Auditory_encoder_base, Symbol


# ---------------------------------------------------------------------------
#   Dummy Encoders for when we need to *REMOVE* an encoder.
#   There's no easy way to do that, so isntead we assign a new
#   encoder that does nothing.
# ---------------------------------------------------------------------------


class NullVisualEncoder(Visual_encoder_base):
    def __init__(self, encoder_name: str, parent):
        super(NullVisualEncoder, self).__init__(encoder_name)
        self.parent = parent
        self.encoder_name = "NullVisualEncoder"
        self.is_null_encoder = True  # don't add this attribute to real encoders!!!


class NullAuditoryEncoder(Auditory_encoder_base):
    def __init__(self, encoder_name: str, parent):
        super(NullAuditoryEncoder, self).__init__(encoder_name)
        self.parent = parent
        self.encoder_name = "NullAuditoryEncoder"
        self.is_null_encoder = True  # don't add this attribute to real encoders!!!
