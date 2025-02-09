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

from functools import lru_cache
from itertools import chain
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QStaticText, QTransform
from qtpy.QtWidgets import QApplication
from qtpy.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QFont,
    QColor,
    QResizeEvent,
    QCloseEvent,
    QPixmap,
    QHideEvent,
    QShowEvent,
    QColorConstants,
)
from qtpy.QtCore import Qt, QRect, QSize
from qtpy.QtWidgets import QMainWindow
from loguru import logger as log

from epicpy.utils.apputils import Point, Size, Rect, conditional_dataclass
from epicpy.utils import config

from epicpy.epiclib.epiclib import Symbol, geometric_utilities as GU

from epicpy.utils.localmunch import DefaultMunch, Munch

WARNING_ACCUMULATOR = set()


def cache_warn(msg: str):
    global WARNING_ACCUMULATOR
    if msg not in WARNING_ACCUMULATOR:
        WARNING_ACCUMULATOR.add(msg)
        log.warning(msg)


@conditional_dataclass
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
        self.can_close = False
        self.bg_image_file = ""
        self.bg_image = None
        self.bg_image_scaled = False

        self.enabled = True
        self.can_draw = True
        self.previously_enabled = self.enabled

        # Precompute sizes
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

        # Cache font early
        base_font = QApplication.instance().font()
        self.setFont(base_font)
        self.overlay_font = QFont(base_font)
        self.overlay_font.setPointSize(self.overlay_font.pointSize() - 2)
        self.bold_font = QFont(base_font)
        self.bold_font.setBold(True)


        self.debug_info = []
        self.objects: dict = {}

        self.shape_router = self.make_shape_router()
        self.setWindowTitle(self.view_title.title())

        self.cached_grid_size = (self.width(), self.height(), self.scale)
        self.cached_grid = self.grid_cache(*self.cached_grid_size)

        self.initialize()

    def reset_font(self):
        self.setFont(QApplication.instance().font())

        self.overlay_font = QFont(self.font())
        self.overlay_font.setPointSize(self.overlay_font.pointSize() - 2)

    def closeEvent(self, event: QCloseEvent):
        if not self.can_close:
            self.hide()
        else:
            QMainWindow.closeEvent(self, event)

    @staticmethod
    def set_dot_on(enabled: bool):
        log.warning(f"instead of calling set_dot_on({enabled}), just set property in config.device_cfg")

    def allow_updates(self, enabled: bool):
        self.enabled = enabled
        self.can_draw = True

    # ========================================================================
    # ViewWindow State Manipulation From VisualView
    # ========================================================================

    def initialize(self):
        self.clear()

    def update_info(self): ...

    def set_needs_display(self):
        self.update()

    def draw_content(self): ...

    def set_origin(self, x: float, y: float):
        self.origin = Point(x, y)

    @staticmethod
    def set_scale(scale: float):
        # self.scale = scale
        log.warning(f"instead of calling set_scale({scale}), just set property in config.device_cfg")

    @staticmethod
    def set_grid_on(enabled: bool):
        log.warning(f"instead of calling set_grid_on({enabled}), just set property in config.device_cfg")

    def clear(self):
        self.objects = {}
        self.update()

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

    # ========================================================================
    # ViewWindow Visual Updates From AuditoryView
    # ========================================================================

    def update_eye_position(self, point: GU.Point):
        self.eye_pos = Point(point.x, point.y * -1)

    @staticmethod
    def create_new_stream(object_name: Symbol, pitch: float, loudness: float, location: GU.Point):
        cache_warn(f"Unhandled call to create_new_stream({object_name}, {pitch}, {loudness}, {location})")

    @staticmethod
    def disappear_stream(object_name: str):
        cache_warn(f"Unhandled call to disappear_stream({object_name})")

    def create_new_object(
        self,
        object_name: str,
        location: GU.Point,
        size: GU.Size,
        properties: Optional[dict] = None,
    ):
        if object_name not in self.objects:
            self.objects[object_name] = SoundObject(
                kind="Speech" if "speaker_id" in properties else "Sound",
                name=object_name,
                location=Point(location.x, location.y * -1),
                size=Size(size.h, size.v),
                property=DefaultMunch(None) if not properties else DefaultMunch(None, properties),
            )
            self.objects[object_name].property["Color"] = (
                QColorConstants.LightGray if "Perceptual" in self.view_type else QColorConstants.Green
            )

    def stop_sound(self, object_name: str):
        if object_name in self.objects:
            self.objects[object_name].property["Color"] = QColorConstants.Red

    def erase_object(self, object_name: str):
        if object_name in self.objects:
            del self.objects[object_name]

    def change_object_location(self, object_name: str, location: GU.Point):
        if object_name in self.objects:
            self.objects[object_name].location = Point(location.x, location.y * -1)

    def change_object_size(self, object_name: str, size: GU.Size):
        if object_name in self.objects:
            self.objects[object_name].size = Size(size.h, size.v)

    def change_object_property(self, object_name: str, prop_name: str, prop_value: Symbol):
        if object_name in self.objects:
            self.objects[object_name].property[prop_name] = prop_value
            if prop_name == "Detection":
                if prop_value == "Onset":
                    self.objects[object_name].property["Color"] = QColorConstants.Green
                elif prop_value == "Offset":
                    self.objects[object_name].property["Color"] = QColorConstants.Red
            else:
                cache_warn(f"AudView Prop Change: {prop_name} - {prop_value}")

    # ========================================================================
    # Drawing Routines
    # ========================================================================

    def paintEvent(self, event):
        if not self.enabled or not self.can_draw:
            self.painting = False
            self.can_draw = False
            return

        if self.painting:
            return  # Prevent re-entry

        self.painting = True
        painter = QPainter(self)  # No need to call begin(self)

        try:
            self.scale = config.device_cfg.spatial_scale_degree

            # draw image underlay
            if config.device_cfg.allow_device_images and self.bg_image:
                self.draw_background_image(painter)

            # draw grid
            if config.device_cfg.calibration_grid:
                self.draw_grid(painter)

            # draw objects
            for obj in self.objects.values():
                self.draw_object(obj, painter)

            if config.device_cfg.center_dot:
                self.dot(painter)

            # draw info overlay
            self.draw_info_overlay(painter)
        finally:
            painter.end()

        self.painting = False
        self.can_draw = False

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.origin = Point(self.width() // 2, self.height() // 2)

        if self.bg_image_file:
            self.bg_image = QPixmap(self.bg_image_file)
            if isinstance(self.bg_image, QPixmap) and self.bg_image_scaled:
                self.bg_image = self.bg_image.scaled(self.width(), self.height())

        # Cache the grid when the window resizes
        self.cached_grid = self.grid_cache(self.width(), self.height(), self.scale)

        self.update()

    def dot(self, painter: QPainter):
        dot_color = QColor(255, 255, 255, 255) if config.app_cfg.dark_mode else QColor(0, 0, 0, 255)

        painter.setPen(dot_color)
        painter.setBrush(dot_color)
        painter.drawEllipse(self.origin.x - 1, self.origin.y - 1, 1, 1)

    def draw_info_overlay(self, painter: QPainter):
        # setup
        painter.setPen(QColorConstants.DarkYellow)
        painter.setFont(self.overlay_font)

        # draw time info
        painter.drawText(10, self.y_min + 10, f"{int(self.current_time) / 1000:0.2f}")

        # draw view info
        s = f"{self.width() / self.scale:0.2f} X {self.height() / self.scale:0.2f} " f"DVA, (0 , 0), {self.scale} p/DVA"
        painter.drawText(5, self.height() - 20, s)

    @staticmethod
    @lru_cache()
    def grid_cache(w, h, scale) -> QPainterPath:
        """
        Grids are expensive to draw, so we're using the flyweight pattern again.
        """
        cx, cy = w // 2, h // 2
        path = QPainterPath()
        y_s = chain(range(cy - scale // 2, 0, -scale), range(cy + scale // 2, h, scale))
        x_s = chain(range(cx - scale // 2, 0, -scale), range(cx + scale // 2, w, scale))
        for y in y_s:
            path.moveTo(0, y)
            path.lineTo(w, y)
        for x in x_s:
            path.moveTo(x, 0)
            path.lineTo(x, h)
        return path

    def draw_grid(self, painter: QPainter):
        painter.setPen(QColor(0, 213, 255, 100))
        painter.setBrush(QBrush(QColorConstants.Cyan))
        painter.drawPath(self.cached_grid)

    def draw_background_image(self, painter: QPainter):
        if self.bg_image is not None:
            w, h = self.width(), self.height()
            pw, ph = self.bg_image.width(), self.bg_image.height()
            try:
                painter.drawPixmap(w // 2 - pw // 2, h // 2 - ph // 2, self.bg_image)
            except Exception as e:
                log.error(f"Unable to draw background: {str(e)}")

    def set_background_image(self, img_file: str, scaled: bool = True):
        if img_file and (self.bg_image_file == img_file):
            return
        try:
            if not img_file or not Path(img_file).is_file():
                # erase
                self.bg_image_file = ""
                self.bg_image = None
            else:
                self.bg_image_file = img_file
                self.bg_image = QPixmap(f"{img_file}")
                if isinstance(self.bg_image, QPixmap) and scaled:
                    self.bg_image = self.bg_image.scaled(self.width(), self.height())  # , Qt.KeepAspectRatio
                self.bg_image_scaled = scaled
        except Exception as e:
            self.bg_image_file = ""
            self.bg_image = None
            log.error(f"Unable to add {img_file} to {self.view_type} window [{e}]")

    # ========================================================================
    # Object Drawing
    # ========================================================================

    # note: status can be Visible, Disappearing, Reappearing, Fading, Audible

    def make_shape_router(self) -> dict:
        return {
            "Ellipse": self.shape_ellipse,
            "Rectangle": self.shape_rectangle,
            "Line": self.shape_line,
        }

    def draw_object(self, obj: SoundObject, painter: QPainter):
        shape = obj.property.get("Shape", "ellipse")  # Default to ellipse
        self.shape_router.get(shape, self.shape_ellipse)(obj, painter)
        self.draw_text(obj, painter)

    @staticmethod
    def obj_pen_brush(obj) -> tuple:
        brush_style = Qt.BrushStyle.NoBrush
        color = obj.property.Color if obj.property.Color else QColorConstants.LightGray
        pen = QPen(color, 2, Qt.PenStyle.SolidLine)
        brush = QBrush(color, brush_style)
        return pen, brush

    @staticmethod
    @lru_cache()
    def shape_cache(shape, x, y, w, h) -> QPainterPath:
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
            cache_warn(f'shape_cache has no handler for "{shape}"')
        return path

    def shape_ellipse(self, obj, painter: QPainter):
        pen, brush = self.obj_pen_brush(obj)
        painter.setPen(pen)
        painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("ellipse", x, y, w, h)
        painter.drawPath(path)

    def shape_line(self, obj, painter: QPainter):
        pen, brush = self.obj_pen_brush(obj)
        painter.setPen(pen)
        painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("line", x, y, w, h)
        painter.drawPath(path)

    def shape_rectangle(self, obj, painter: QPainter):
        pen, brush = self.obj_pen_brush(obj)
        painter.setPen(pen)
        painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("rectangle", x, y, w, h)
        painter.drawPath(path)

    @staticmethod
    @lru_cache()
    def text_cache(x, y, text, scale) -> QPainterPath:
        path = QPainterPath()
        font = QFont(QApplication.instance().font())
        font.setPointSize(round(scale * 0.8))
        font.setWeight(QFont.Weight.Light)
        for row, txt in enumerate(text.splitlines(keepends=False)):
            path.addText(x, y + row * font.pixelSize() * 15, font, txt)
        return path

    def draw_text(self, obj: SoundObject, painter: QPainter):
        text = ""
        cfg = config.device_cfg
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

        text = text.strip()
        if not text:
            return

        # Choose color based on status.
        color = (QColorConstants.Black if obj.property.Status != "Fading"
                 else QColorConstants.LightGray)
        painter.setPen(QPen(color, 1, Qt.PenStyle.SolidLine))

        # Compute the drawing position.
        x, y, w, h = self.center_and_scale(obj.location, obj.size)

        # Set up the font.
        font = QFont(self.bold_font)
        # Use the same scaling as before.
        font.setPointSize(round(self.scale * 0.8))
        painter.setFont(font)

        # Split the text into individual lines.
        lines = text.splitlines()

        # Create a list for the QStaticText objects and record each line's height.
        static_texts = []
        line_heights = []
        max_width = 0
        for line in lines:
            st = QStaticText(line)
            st.setTextFormat(Qt.TextFormat.PlainText)
            # Prepare the static text with an identity transform and the custom font.
            st.prepare(QTransform(), font)
            static_texts.append(st)
            size = st.size()  # QSizeF
            line_heights.append(size.height())
            if size.width() > max_width:
                max_width = size.width()

        # Compute total height of the text block.
        total_height = sum(line_heights)

        # Compute the starting drawing position such that the text block is centered.
        draw_x = x - max_width / 2
        draw_y = y - total_height / 2

        # Draw each line, incrementing the y position.
        current_y = draw_y
        for st in static_texts:
            painter.drawStaticText(draw_x, current_y, st)
            current_y += st.size().height()

    """
    Attempt to avoid drawing to closed windows
    """

    def hideEvent(self, event: QHideEvent) -> None:
        self.previously_enabled = self.enabled
        self.enabled = False
        QMainWindow.hideEvent(self, event)

    def showEvent(self, event: QShowEvent) -> None:
        self.enabled = self.previously_enabled
        QMainWindow.showEvent(self, event)
