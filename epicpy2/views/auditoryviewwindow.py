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

from copy import deepcopy
from pathlib import Path

from PyQt5.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QFont,
    QColor,
    QResizeEvent,
    QCloseEvent,
    QPixmap,
)
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtWidgets import QMainWindow
from munch import Munch, DefaultMunch
from loguru import logger as log
from epicpy2.utils.apputils import Point, Size, Rect, memoize_class_method
from dataclasses import dataclass
from epicpy2.utils import config

from epicpy2.epiclib.epiclib import Symbol, geometric_utilities as GU

WARNING_ACCUMULATOR = []


@dataclass
class SoundObject:
    kind: str
    name: str
    location: Point
    size: Size
    property: Munch


class AuditoryViewWin(QMainWindow):
    def __init__(self, view_type: str, view_title: str):
        super(AuditoryViewWin, self).__init__()

        # these have to match the channels created on the EpicCLI/Device side,
        # so we have to be strict
        assert view_type in (
            "Auditory Physical",
            "Auditory Sensory",
            "Auditory Perceptual",
        )

        self.view_type = view_type
        self.view_title = view_title
        self.setObjectName(view_type)
        self.dark_mode = config.app_cfg.dark_mode
        self.can_close = False
        self.bg_image_file = ""
        self.bg_image = None
        self.bg_image_scaled = False

        self.enabled = True
        self.can_draw = True

        # min_size = QSize(440, 340)
        min_size = QSize(390, 301)
        self.resize(min_size)
        self.setMinimumSize(min_size)
        self.y_min = 10  # minimum visible y position

        self.scale = config.device_cfg.spatial_scale_degree  # num pixels per DVA
        self.origin = Point(0, 0)
        self.current_time = 0.0
        self.fov_size = Size(1.0, 1.0)
        self.para_size = Size(10.0, 10.0)
        self.eye_pos = Point(0, 0)
        self.painting = False

        # objects
        self.objects = dict()

        self.setWindowTitle(self.view_title.title())

        self.painter = None

        self.initialize()

    def closeEvent(self, event: QCloseEvent):
        if not self.can_close:
            self.hide()
        else:
            QMainWindow.closeEvent(self, event)

    def set_dot_on(self, enabled: bool):
        log.warning(
            "instead of calling set_dot_on(), just set property in config.device_cfg"
        )

    def allow_updates(self, enabled: bool):
        self.enabled = enabled
        self.can_draw = True

    # ========================================================================
    # ViewWindow State Manipulation From VisualView
    # ========================================================================

    def initialize(self):
        self.clear()

    def update_info(self):
        ...

    def set_needs_display(self):
        self.update()

    def draw_content(self):
        ...

    def set_origin(self, x: float, y: float):
        self.origin = Point(x, y)

    def set_scale(self, scale: float):
        log.warning(
            "instead of calling set_scale(), just set property in config.device_cfg"
        )

    def set_grid_on(self, enabled: bool):
        log.warning(
            "instead of calling set_grid_on(), just set property in config.device_cfg"
        )

    def clear(self):
        self.objects = dict()

    def update_time(self, current_time: int):
        self.current_time = current_time

    # ========================================================================
    # Utilities -- keep local for speed (may not be necessary in Py3.8 or 3.9)
    # ========================================================================

    def center_and_scale(self, loc: Point, size: Size) -> Rect:
        x, y = (v * self.scale for v in loc)
        w, h = (v * self.scale for v in size)
        x, y = (x - w / 2) + self.origin.x, (y - h / 2) + self.origin.y
        return Rect(int(x), int(y), int(w), int(h))

    def cache_warn(self, msg: str):
        if msg not in WARNING_ACCUMULATOR:
            WARNING_ACCUMULATOR.append(msg)
            log.warning(msg)

    # ========================================================================
    # ViewWindow Visual Updates From AuditoryView
    # ========================================================================

    def update_eye_position(self, point: GU.Point):
        self.eye_pos = Point(point.x, point.y * -1)

    def create_new_stream(
        self, object_name: Symbol, pitch: float, loudness: float, location: GU.Point
    ):
        self.cache_warn("Unhandled call to create new stream")

    def disappear_stream(self, object_name: str):
        self.cache_warn(f"Unhandled call to disappear stream")

    def create_new_object(
        self,
        object_name: str,
        location: GU.Point,
        size: GU.Size,
        properties: dict = None,
    ):
        if object_name not in self.objects:
            self.objects[object_name] = SoundObject(
                kind="Speech" if "speaker_id" in properties else "Sound",
                name=object_name,
                location=Point(location.x, location.y * -1),
                size=Size(size.h, size.v),
                property=DefaultMunch(None)
                if not properties
                else DefaultMunch(None, properties),
            )
            self.objects[object_name].property["Color"] = (
                Qt.lightGray if "Perceptual" in self.view_type else Qt.green
            )

    def stop_sound(self, object_name: str):
        if object_name in self.objects:
            self.objects[object_name].property["Color"] = Qt.red

    def erase_object(self, object_name: str):
        if object_name in self.objects:
            del self.objects[object_name]

    def change_object_location(self, object_name: str, location: GU.Point):
        if object_name in self.objects:
            self.objects[object_name].location = Point(location.x, location.y * -1)

    def change_object_size(self, object_name: str, size: GU.Size):
        if object_name in self.objects:
            self.objects[object_name].size = Size(size.h, size.v)

    def change_object_property(
        self, object_name: str, prop_name: str, prop_value: Symbol
    ):
        if object_name in self.objects:
            self.objects[object_name].property[prop_name] = prop_value
            if prop_name == "Detection":
                if prop_value == "Onset":
                    self.objects[object_name].property["Color"] = Qt.green
                elif prop_value == "Offset":
                    self.objects[object_name].property["Color"] = Qt.red
            else:
                self.cache_warn(f"AudView Prop Change: {prop_name} - {prop_value}")

    # ========================================================================
    # Drawing Routines
    # ========================================================================

    def paintEvent(self, event):
        if not self.enabled or not self.can_draw:
            return

        if self.painting:
            return
        else:
            self.painting = True

        if not self.painter:
            self.painter = QPainter(self)

        self.scale = config.device_cfg.spatial_scale_degree

        try:
            self.painter.begin(self)

            # draw image underlay
            if config.device_cfg.allow_device_images and self.bg_image:
                self.draw_background_image()

            # draw grid
            if config.device_cfg.calibration_grid:
                self.draw_grid()

            # draw objects
            for object in self.objects.values():
                self.draw_object(object)

            if config.device_cfg.center_dot:
                self.dot()

            # draw info overlay
            self.draw_info_overlay()

        finally:
            self.painter.end()

        self.painting = False
        self.can_draw = False

    def resizeEvent(self, event: QResizeEvent):
        QMainWindow.resizeEvent(self, event)
        self.origin = Point(self.width() // 2, self.height() // 2)
        if self.bg_image_file:
            self.bg_image = QPixmap(str(self.bg_image_file))
            if isinstance(self.bg_image, QPixmap) and self.bg_image_scaled:
                self.bg_image = self.bg_image.scaled(self.width(), self.height())  # , Qt.KeepAspectRatio
        self.update()

    def dot(self):
        dot_color = (
            QColor(255, 255, 255, 255) if self.dark_mode else QColor(0, 0, 0, 255)
        )

        self.painter.setPen(dot_color)
        self.painter.setBrush(dot_color)
        self.painter.drawEllipse(self.origin.x - 1, self.origin.y - 1, 1, 1)

    def draw_info_overlay(self):
        # setup
        self.painter.setPen(Qt.white if self.dark_mode else Qt.black)
        self.painter.setFont(QFont("Arial", 10, QFont.Normal))

        # draw time info
        self.painter.drawText(
            10, self.y_min + 10, f"{int(self.current_time) / 1000:0.2f}"
        )

        # draw view info
        s = (
            f"{self.width() / self.scale:0.2f} X {self.height() / self.scale:0.2f} "
            f"DVA, (0 , 0), {self.scale} p/DVA"
        )
        self.painter.drawText(5, self.height() - 20, s)

    @memoize_class_method()
    def grid_cache(self, w, h, scale) -> QPainterPath:
        """
        Grids are expensive to draw, so we're using the flyweight pattern again.
        """
        cx, cy = w // 2, h // 2
        path = QPainterPath()
        Ys = list(range(cy - scale // 2, 0, -scale))
        Ys += list(range(cy + scale // 2, h, scale))
        Xs = list(range(cx - scale // 2, 0, -scale))
        Xs += list(range(cx + scale // 2, w, scale))
        for y in Ys:
            path.moveTo(0, y)
            path.lineTo(w, y)
        for x in Xs:
            path.moveTo(x, 0)
            path.lineTo(x, h)
        return path

    def draw_grid(self):
        self.painter.setPen(QColor(0, 213, 255, 100))
        self.painter.setBrush(QBrush(Qt.cyan))
        self.painter.drawPath(self.grid_cache(self.width(), self.height(), self.scale))

    def draw_background_image(self):
        if self.bg_image is not None:
            w, h = self.width(), self.height()
            pw, ph = self.bg_image.width(), self.bg_image.height()
            try:
                self.painter.drawPixmap(w // 2 - pw // 2, h // 2 - ph // 2, self.bg_image)
            except Exception as e:
                log.error(f'Unable to draw background: {str(e)}')

    def set_background_image(self, img_file: str, scaled: bool = True):
        if img_file and self.bg_image_file == img_file:
            return
        try:
            if not img_file or not Path(img_file).is_file():
                # erase
                self.bg_image_file = ""
                self.bg_image = None
            else:
                self.bg_image_file = img_file
                self.bg_image = QPixmap(str(img_file))
                if isinstance(self.bg_image, QPixmap) and scaled:
                    self.bg_image = self.bg_image.scaled(self.width(), self.height()) # , Qt.KeepAspectRatio
                self.bg_image_scaled = scaled
        except Exception as e:
            self.bg_image_file = ""
            self.bg_image = None
            log.error(f"Unable to add {img_file} to {self.view_type} window [{e}]")

    # ========================================================================
    # Object Drawing
    # ========================================================================

    # note: status can be Visible, Disappearing, Reappearing, Fading, Audible

    def draw_object(self, obj: SoundObject):
        self.shape_ellipse(obj)
        self.draw_text(obj)

    def obj_pen_brush(self, obj) -> tuple:
        brush_style = Qt.NoBrush
        color = obj.property.Color if obj.property.Color else Qt.lightGray
        pen = QPen(color, 2, Qt.SolidLine)
        brush = QBrush(color, brush_style)
        return pen, brush

    @memoize_class_method()
    def shape_cache(self, shape, x, y, w, h) -> QPainterPath:
        """
        This is my attempt to replicate DK's flyweight pattern for efficient
        object creation. The key is the custom lru_cache!
        """
        path = QPainterPath()
        if shape == "ellipse":
            path.addEllipse(x, y, w, h)
        elif shape == "line":
            box = QRect(x, y, w, h)
            xo = box.width() / 2.0
            yo = box.height() / 2.0
            path.moveTo(box.bottomLeft().x() + xo, box.bottomLeft().y() - yo)
            path.lineTo(box.topRight().x() + xo, box.topRight().y() - yo)
        elif shape == "rectangle":
            path.addRect(x, y, w, h)
        else:
            self.cache_warn(f'shape_cache has no handler for "{shape}"')
        return path

    def shape_ellipse(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("ellipse", x, y, w, h)
        self.painter.drawPath(path)

    def shape_line(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("line", x, y, w, h)
        self.painter.drawPath(path)

    def shape_rectangle(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("rectangle", x, y, w, h)
        self.painter.drawPath(path)

    @memoize_class_method()
    def text_cache(self, x, y, text) -> QPainterPath:
        path = QPainterPath()
        font = QFont("Arial", 10, QFont.Light)
        for row, txt in enumerate(text.splitlines(keepends=False)):
            path.addText(x, y + row * font.pixelSize() * 15, font, txt)
        return path

    def draw_text(self, obj: SoundObject):
        text = ""
        cfg = deepcopy(config.device_cfg)
        if obj.kind == "Sound":
            if cfg.sound_text_kind:
                text += f"Kind: {obj.kind}\n"
            if cfg.sound_text_stream:
                text += f"Stream: {obj.property.stream_name}\n"
            if cfg.sound_text_timbre:
                text += f"Timbre: {obj.property.timbre}\n"
            if cfg.sound_text_loudness:
                text += f"Loudness: {obj.property.loudness} db\n"
        elif obj.kind == "Speech":
            if cfg.speech_text_kind:
                text += f"Kind: {obj.kind}\n"
            if cfg.speech_text_stream:
                text += f"Stream: {obj.property.stream_name}\n"
            if cfg.speech_text_pitch:
                text += f"Pitch: {obj.property.pitch} st\n"
            if cfg.speech_text_loudness:
                text += f"Loudness: {obj.property.loudness} db\n"
            if cfg.speech_text_content:
                text += f"Content: {obj.property.content}\n"
            if cfg.speech_text_speaker:
                text += f"Speaker: {obj.property.speaker_id}\n"
            if cfg.speech_text_gender:
                text += f"Gender: {obj.property.speaker_gender}\n"
        else:
            return

        color = Qt.black if obj.property.Status != "Fading" else Qt.lightGray
        self.painter.setPen(QPen(color, 1, Qt.SolidLine))
        self.painter.setBrush(QBrush(color, Qt.SolidPattern))
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.text_cache(x, y, text.strip())
        self.painter.drawPath(path)
