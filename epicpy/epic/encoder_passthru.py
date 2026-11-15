# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from epiclibcpp.epiclib import Auditory_encoder_base, Visual_encoder_base

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
