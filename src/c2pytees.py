

from typing import Optional

from views.epicpy_textview import EPICTextViewCachedWrite

"""
Contains  globals that point to various EPICTextViewCachedWrite objects.
epiclib will call their various write_char methods when it wants to send info via Normal_out, Trace_out, PPS_out,
and Debug_out, depending on which ones have been set up earlier via calls to epiclib's py_streamer interface.
"""

NORMAL_OUT: Optional[EPICTextViewCachedWrite] = None
TRACE_OUT: Optional[EPICTextViewCachedWrite] = None
PPS_OUT: Optional[EPICTextViewCachedWrite] = None
DEBUG_OUT: Optional[EPICTextViewCachedWrite] = None