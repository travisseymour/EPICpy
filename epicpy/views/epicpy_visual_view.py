# SPDX-FileCopyrightText: EPICpy | Copyright (c) 2022-2026 Travis L. Seymour, PhD <nogard@ucsc.edu>
# SPDX-License-Identifier: GPL-3.0-or-later

from epiclibcpp.epiclib import Symbol, View_base
from epiclibcpp.epiclib import geometric_utilities as GU
from loguru import logger as log

from epicpy.views.visual_view_window import VisualViewWin


class EPICVisualView(View_base):
    def __init__(self, view_window: VisualViewWin):
        super(EPICVisualView, self).__init__()
        self.view_window = view_window
        self.changed = False  # *
        self.curr_time = 0

    def get_current_time(self):
        return self.current_time

    def initialize(self):
        # Never getting called!
        self.view_window.initialize()

    def set_changed(self):  # *
        if not self.changed:
            self.changed = True
            self.view_window.update_time(self.curr_time)
            self.view_window.set_needs_display()
            self.changed = False

    def clear(self):
        if self.view_window.enabled:
            self.view_window.clear()
            self.set_changed()

    def notify_eye_movement(self, new_eye_location: GU.Point):
        if self.view_window.enabled:
            self.view_window.update_eye_position(new_eye_location)
            self.set_changed()

    def notify_object_appear(self, object_name: Symbol, location: GU.Point, size: GU.Size):
        # this function does nothing if the named object already exists.
        # The architecture elsewhere will signal an error.
        if self.view_window.enabled:
            self.view_window.create_new_object(object_name.str(), location, size)
            self.set_changed()

    # These functions should do nothing if the referred to object does not exist.
    # The architecture elsewhere will signal an error. Currently, leaving it up to
    # self.view_window to deal with any invalid object_names that get through.
    # ----------------------------------------------------------------------------------

    # def notify_object_disappear(self, object_name: Symbol):
    #     # I can get this info from the property changes
    #     pass
    #
    # def notify_object_reappear(self, object_name: Symbol):
    #     # I can get this info from the property changes
    #     pass

    def notify_erase_object(self, object_name: Symbol):
        if self.view_window.enabled:
            self.view_window.erase_object(object_name.str())
            self.set_changed()

    def notify_visual_location_changed(self, object_name: Symbol, location: GU.Point):
        if self.view_window.enabled:
            self.view_window.change_object_location(object_name.str(), location)
            self.set_changed()

    def notify_visual_size_changed(self, object_name: Symbol, size: GU.Size):
        if self.view_window.enabled:
            self.view_window.change_object_size(object_name.str(), size)
            self.set_changed()

    def notify_visual_property_changed(self, object_name: Symbol, prop_name: Symbol, prop_value: Symbol):
        if self.view_window.enabled:
            if prop_name.str() in ("Status", "Color", "Shape", "Text", "Leader"):
                self.view_window.change_object_property(object_name.str(), prop_name.str(), prop_value.str())
                self.set_changed()

    # def notify_append_text(self, text: str):
    #     pass

    # def notify_time(self, current_time: int):
    #     self.curr_time = current_time

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            log.error("--------------------------------------------------")
            log.error("A missing method was called.")
            log.error(f"The object was {self}, the method was {name}. ")
            log.error(f"It was called with {args} and {kwargs} as arguments\n")

        return _missing
