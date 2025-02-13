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

from epicpy.views.auditoryviewwindow import AuditoryViewWin
from loguru import logger as log

from epicpy.epiclib.epiclib import (
    View_base,
    Speech_word,
    geometric_utilities as GU,
    Symbol,
)


class EPICAuditoryView(View_base):
    def __init__(self, view_window: AuditoryViewWin):
        super(EPICAuditoryView, self).__init__()
        self.view_window = view_window
        self.changed = False  # *
        self.curr_time = 0

    def initialize(self):
        self.view_window.initialize()

    def set_changed(self):  # *
        if not self.changed:
            self.changed = True
            self.view_window.update_time(self.curr_time)
            self.view_window.set_needs_display()
            self.changed = False

    # def draw_content(self):
    #     # never getting called
    #     self.view_window.draw_content()

    # def set_origin(self, x: float, y: float):
    #     # currently this is hard coded at 0,0
    #     self.view_window.set_origin(x, y)
    #
    # def set_scale(self, scale: float):
    #     # this is handled via config option in EPICpy
    #     self.view_window.set_scale(scale)
    #
    # def set_grid_on(self, grid_on: bool):
    #     # this is handled via config option in EPICpy
    #     self.view_window.set_grid_on(grid_on)

    def clear(self):
        if self.view_window.enabled:
            self.view_window.clear()
            self.set_changed()

    def notify_eye_movement(self, new_eye_location: GU.Point):
        if self.view_window.enabled:
            self.view_window.update_eye_position(new_eye_location)
            self.set_changed()

    # this creation functions do nothing if the named object already exists.
    # The architecture elsewhere will signal an error.

    def notify_auditory_stream_appear(self, object_name: Symbol, pitch: float, loudness: float, location: GU.Point):
        if self.view_window.enabled:
            self.view_window.create_new_stream(object_name.str(), pitch, loudness, location)
            self.set_changed()

    def notify_auditory_sound_start(
        self,
        object_name: Symbol,
        stream_name: Symbol,
        time_stamp: int,
        location: GU.Point,
        timbre: Symbol,
        loudness: float,
    ):
        if self.view_window.enabled:
            keys = ("stream_name", "time_stamp", "timbre", "loudness")
            values = (stream_name.str(), time_stamp, timbre.str(), loudness)
            props = dict(zip(keys, values))
            self.view_window.create_new_object(
                object_name=object_name.str(),
                location=location,
                size=GU.Size(2, 2),
                properties=props,
            )
            self.set_changed()

    def notify_auditory_speech_start(self, word: Speech_word):
        if self.view_window.enabled:
            keys = (
                "stream_name",
                "time_stamp",
                "pitch",
                "loudness",
                "duration",
                "content",
                "speaker_gender",
                "speaker_id",
            )
            values = (
                word.stream_name.str(),
                word.time_stamp,
                word.pitch,
                word.loudness,
                word.duration,
                word.content.str(),
                word.speaker_gender.str(),
                word.speaker_id.str(),
            )
            props = dict(zip(keys, values))
            self.view_window.create_new_object(
                object_name=word.name.str(),
                location=word.location,
                size=GU.Size(2, 2),
                properties=props,
            )
            self.set_changed()

    # These functions should do nothing if the referred to object does not exist.
    # The architecture elsewhere will signal an error. Currently, leaving it up to
    # self.view_window to deal with any invalid object_names that get through.
    # ----------------------------------------------------------------------------------

    def notify_auditory_stream_disappear(self, object_name: Symbol):
        if self.view_window.enabled:
            self.view_window.disappear_stream(object_name.str())
            self.set_changed()

    # def notify_auditory_stream_location_changed(self, object_name: Symbol, location: GU.Point):
    #     if self.view_window.enabled:
    #         # self.view_window.change_auditory_stream_location(object_name.str(), location)
    #         log.warning(f'unhandled function called with {object_name.str(), location}')
    #
    # def notify_auditory_stream_pitch_changed(self, object_name: Symbol, pitch: float):
    #     if self.view_window.enabled:
    #         # self.view_window.change_auditory_stream_pitch(object_name.str(), pitch)
    #         log.warning(f'unhandled function called with {object_name.str(), pitch}')
    #
    # def notify_auditory_stream_loudness_changed(self, object_name: Symbol, loudness: float):
    #     if self.view_window.enabled:
    #         # self.view_window.change_auditory_stream_loudness(object_name.str(), loudness)
    #         log.warning(f'unhandled function called with {object_name.str(), loudness}')
    #
    # def notify_auditory_stream_size_changed(self, object_name: Symbol, size: GU.Size):
    #     if self.view_window.enabled:
    #         # self.view_window.change_auditory_stream_size(object_name.str(), size)
    #         log.warning(f'unhandled function called with {object_name.str(), size}')
    #
    # def notify_auditory_stream_property_changed(self, object_name: Symbol, prop_name: Symbol, prop_value: Symbol):
    #     if self.view_window.enabled:
    #         # self.view_window.change_auditory_stream_property(object_name.str(), prop_name.str(), prop_value)
    #         log.warning(f'unhandled function called with {object_name.str(), prop_name.str(), prop_value}')

    def notify_auditory_sound_stop(self, object_name: Symbol):
        if self.view_window.enabled:
            self.view_window.stop_sound(object_name.str())
            self.set_changed()

    def notify_erase_sound(self, object_name: Symbol):
        if self.view_window.enabled:
            self.view_window.erase_object(object_name.str())
            self.set_changed()

    def notify_auditory_sound_property_changed(self, object_name: Symbol, prop_name: Symbol, prop_value: Symbol):
        if self.view_window.enabled:
            # NOTE: Currently only expecting property values that can be represented as string
            #       event.g., {'Offset', 'Nil', 'Onset'}. If numeric or other types are needed, then prop_value.str()
            #       needs to be re-evaluated!
            self.view_window.change_object_property(object_name.str(), prop_name.str(), prop_value.str())
            self.set_changed()

    # def notify_append_text(self, text: str):
    #     pass

    # def notify_time(self, current_time: int):
    #     self.curr_time = current_time

    def __lshift__(self, *args, **kwargs):
        log.warning(f"epicpy_auditoryview.py:__lshift__() called with these parameters: {kwargs}")

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            log.error("--------------------------------------------------")
            log.error("A missing method was called.")
            log.error(f"The object was {self}, the method was {name}. ")
            log.error(f"It was called with {args} and {kwargs} as arguments\n")

        return _missing
