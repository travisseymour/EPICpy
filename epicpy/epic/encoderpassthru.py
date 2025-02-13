"""
This file is part of the EPICpy source code. EPICpy is a tool for simulating
human performance tasks using the EPIC computational cognitive architecture
(David Kieras and David Meyer 1997a) using the Python programming language.
Copyright (C) 2022 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from epicpy.epiclib.epiclib import Visual_encoder_base, Auditory_encoder_base


# ---------------------------------------------------------------------------
#   Dummy Encoders for when we need to *REMOVE* an encoder.
#   There's no easy way to do that, so instead we assign a new
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
