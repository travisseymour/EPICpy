from typing import Optional, Dict
import sys
from epicpy2.widgets.cachedplaintextedit import CachedPlainTextEdit

class EPICLib_Output_Sorter:
    def __init__(self):
        self.window: Dict[str,Optional[CachedPlainTextEdit]] = {}

    def write(self, text:str):
        try:
            kind = text[0]
        except IndexError:
            return
        try:
            self.window[kind].write(text[1:])
        except (KeyError, AttributeError):
            if kind and kind in 'NTPD':
                sys.stderr.write(f"{kind} | {text[1:]}\n")
            else:
                sys.stderr.write(text+'\n')

    def flush(self):
        ...
        # for win in self.window.values():
        #     try:
        #         win.flush()
        #     except AttributeError:
        #         ...

OUTPUT_SORTER = EPICLib_Output_Sorter()