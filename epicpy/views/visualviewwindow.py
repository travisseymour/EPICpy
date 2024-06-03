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

from itertools import chain
from pathlib import Path
from typing import Optional

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
    QPolygonF,
    QHideEvent,
    QShowEvent,
    QColorConstants,
)
from qtpy.QtCore import Qt, QPoint, QRect, QRectF, QSize, QPointF
from qtpy.QtWidgets import QMainWindow, QGraphicsTextItem
from loguru import logger as log

from epicpy import app_font
from epicpy.utils.apputils import Point, Size, Rect, memoize_class_method
from dataclasses import dataclass
from functools import partial

from epicpy.utils.localmunch import Munch, DefaultMunch
from epicpy.views.epiccolors import epic_colors as colors
from epicpy.utils import config

from epicpy.epiclib.epiclib import geometric_utilities as GU


WARNING_ACCUMULATOR = []


@dataclass
class VisualObject:
    kind: str
    name: str
    location: Point
    size: Size
    property: Munch


class VisualViewWin(QMainWindow):
    def __init__(self, view_type: str, view_title: str):
        super(VisualViewWin, self).__init__()

        # these have to match the channels created on the EpicCLI/Device side,
        #  so we have to be strict
        assert view_type in ("Visual Physical", "Visual Sensory", "Visual Perceptual")

        self.view_type = view_type
        self.view_title = view_title
        self.setObjectName(view_type)
        self.dark_mode = config.app_cfg.dark_mode  # local lookup...
        self.can_close = False
        self.bg_image_file = ""
        self.bg_image = None
        self.bg_image_scaled = False

        self.enabled = True
        self.can_draw = True
        self.previously_enabled = self.enabled

        # self.setObjectName("VisualViewWindow")

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

        self.painter = None
        self.painting = False
        self.overlay_font = QFont(app_font)
        self.overlay_font.setPointSize(10)

        self.debug_info = list()

        # objects
        self.objects = {}
        self.shape_router = self.make_shape_router()

        # self.destroyed.connect(self.cleanup)

        self.setWindowTitle(self.view_title.title())

        self.initialize()

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

    def update_info(self):
        ...

    def set_needs_display(self):
        self.update()

    def draw_content(self):
        ...

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

    @staticmethod
    def cache_warn(msg: str):
        global WARNING_ACCUMULATOR
        if msg not in WARNING_ACCUMULATOR:
            WARNING_ACCUMULATOR.append(msg)
            log.warning(msg)

    # ========================================================================
    # ViewWindow Visual Updates From VisualView
    # ========================================================================

    def update_eye_position(self, point: GU.Point):
        self.eye_pos = Point(point.x, point.y * -1)

    def create_new_object(
        self,
        object_name: str,
        location: GU.Point,
        size: GU.Size,
        properties: Optional[dict] = None,
    ):
        if object_name not in self.objects:
            self.objects[object_name] = VisualObject(
                kind="Visual",
                name=object_name,
                location=Point(location.x, location.y * -1),
                size=Size(size.h, size.v),
                property=DefaultMunch(None) if not properties else DefaultMunch(None, properties),
            )

    def erase_object(self, object_name: str):
        if object_name in self.objects:
            del self.objects[object_name]

    def change_object_location(self, object_name: str, location: GU.Point):
        if object_name in self.objects:
            self.objects[object_name].location = Point(location.x, location.y * -1)

    def change_object_size(self, object_name: str, size: GU.Size):
        if object_name in self.objects:
            self.objects[object_name].size = Size(size.h, size.v)

    def change_object_property(self, object_name: str, prop_name: str, prop_value: str):
        # note: at the moment, I'm only letting through a few properties,
        #  all with string values!
        if object_name in self.objects:
            if prop_name == "Shape":
                filled = True
                shape_name = prop_value
                if "Filled_" in shape_name:
                    shape_name = shape_name.replace("Filled_", "")
                elif "Empty_" in shape_name:
                    filled = False
                    shape_name = shape_name.replace("Empty_", "")
                self.objects[object_name].property[prop_name] = shape_name
                self.objects[object_name].property["Filled"] = filled
            else:
                self.objects[object_name].property[prop_name] = prop_value

    # ========================================================================
    # Drawing Routines
    # ========================================================================

    def paintEvent(self, event):
        if not self.enabled or not self.can_draw:
            self.painting = False
            self.can_draw = False
            return

        if self.painting:
            return
        else:
            self.painting = True

        if not self.painter:
            self.painter = QPainter(self)

        try:
            self.painter.begin(self)

            self.scale = config.device_cfg.spatial_scale_degree

            # draw image underlay
            if config.device_cfg.allow_device_images and self.bg_image:
                self.draw_background_image()

            # draw grid
            if config.device_cfg.calibration_grid:
                self.draw_grid()

            # draw objects
            for obj in self.objects.values():
                self.draw_object(obj)

            # draw eye and dot
            self.dot_and_eye()

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
            self.bg_image = QPixmap(f"{self.bg_image_file}")
            if isinstance(self.bg_image, QPixmap) and self.bg_image_scaled:
                self.bg_image = self.bg_image.scaled(self.width(), self.height())  # , Qt.KeepAspectRatio
        self.update()

    def dot_and_eye(self):
        dot_color = QColor(255, 255, 255, 255) if self.dark_mode else QColor(0, 0, 0, 255)
        fov_color = QColor.fromRgbF(0.75, 0.75, 0.75, 0.5) if self.dark_mode else QColor.fromRgbF(0.5, 0.5, 0.5, 0.3)
        para_color = QColorConstants.LightGray if self.dark_mode else QColorConstants.Gray

        self.painter.setPen(fov_color)
        self.painter.setBrush(fov_color)
        x, y, w, h = self.center_and_scale(self.eye_pos, self.fov_size)
        self.painter.drawEllipse(x, y, w, h)

        self.painter.setPen(para_color)
        self.painter.setBrush(Qt.BrushStyle.NoBrush)
        x, y, w, h = self.center_and_scale(self.eye_pos, self.para_size)
        self.painter.drawEllipse(x, y, w, h)

        if config.device_cfg.center_dot:
            self.painter.setPen(dot_color)
            self.painter.setBrush(dot_color)
            self.painter.drawEllipse(self.origin.x - 1, self.origin.y - 1, 1, 1)

    def draw_info_overlay(self):
        # setup
        self.painter.setPen(QColorConstants.White if self.dark_mode else QColorConstants.Black)
        self.painter.setFont(self.overlay_font)

        # draw time info
        self.painter.drawText(10, self.y_min + 10, f"{int(self.current_time) / 1000:0.2f}")

        # draw view info
        s = f"{self.width() / self.scale:0.2f} X {self.height() / self.scale:0.2f} " f"DVA, (0 , 0), {self.scale} p/DVA"
        self.painter.drawText(5, self.height() - 20, s)

    @memoize_class_method()
    def grid_cache(self, w, h, scale) -> QPainterPath:
        """
        Grids are expensive to draw, so we're using the flyweight pattern again.
        """
        cx, cy = w // 2, h // 2
        path = QPainterPath()
        Ys = chain(range(cy - scale // 2, 0, -scale), range(cy + scale // 2, h, scale))
        Xs = chain(range(cx - scale // 2, 0, -scale), range(cx + scale // 2, w, scale))
        for y in Ys:
            path.moveTo(0, y)
            path.lineTo(w, y)
        for x in Xs:
            path.moveTo(x, 0)
            path.lineTo(x, h)
        return path

    def draw_grid(self):
        self.painter.setPen(QColor(0, 213, 255, 100))
        self.painter.setBrush(QBrush(QColorConstants.Cyan))
        self.painter.drawPath(self.grid_cache(self.width(), self.height(), self.scale))

    def draw_background_image(self):
        if self.bg_image is not None:
            w, h = self.width(), self.height()
            pw, ph = self.bg_image.width(), self.bg_image.height()
            try:
                self.painter.drawPixmap(w // 2 - pw // 2, h // 2 - ph // 2, self.bg_image)
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

    def draw_object(self, obj: VisualObject):
        if not obj.property:
            # just onset, no properties yet
            self.shape_nil(obj)
        else:
            if "Shape" in obj.property:
                self.draw_shape(obj)
            if "Text" in obj.property:
                self.draw_text(obj)

    @staticmethod
    def obj_pen_brush(obj) -> tuple:
        """
        Consult object and properties to determine appropriate pen and brush to use
        """
        if not obj.property.Filled:
            brush_style = Qt.BrushStyle.NoBrush
        else:
            if f"{obj.property.Status}" == "Disappearing":
                brush_style = Qt.BrushStyle.Dense4Pattern
            else:
                brush_style = Qt.BrushStyle.SolidPattern

        color = colors[obj.property.Color] if obj.property.Color in colors else QColorConstants.LightGray
        pen = QPen(color, 2, Qt.PenStyle.SolidLine)
        brush = QBrush(color, brush_style)
        return pen, brush

    # ------------- Draw Command Routing ---------------------------------

    def make_shape_router(self) -> dict:
        return {
            "Nil": self.shape_nil,
            "Nada": self.shape_nil,
            "Triangle": self.shape_triangle,
            "Circle": self.shape_ellipse,
            "Ellipse": self.shape_ellipse,
            "Square": self.shape_rectangle,
            "Rectangle": self.shape_rectangle,
            "Keyboard_Button": self.shape_keyboard_button,
            "Button": self.shape_button,
            "Diamond": self.shape_diamond,
            "Cross_Hairs": self.shape_cross_hairs,
            "Cross": self.shape_cross,
            "Top_Semicircle": self.shape_arc,
            "Bar": self.shape_bar,
            "Up_Arrow": partial(self.shape_right_arrow, rotation=-90),
            "Down_Arrow": partial(self.shape_right_arrow, rotation=90),
            "Left_Arrow": partial(self.shape_right_arrow, rotation=180),
            "Right_Arrow": partial(self.shape_right_arrow, rotation=0),
            "NN_Arrow": partial(self.shape_right_arrow, rotation=-90),
            "SS_Arrow": partial(self.shape_right_arrow, rotation=90),
            "WW_Arrow": partial(self.shape_right_arrow, rotation=180),
            "EE_Arrow": partial(self.shape_right_arrow, rotation=0),
            "NE_Arrow": partial(self.shape_right_arrow, rotation=-45),
            "NW_Arrow": partial(self.shape_right_arrow, rotation=225),
            "SE_Arrow": partial(self.shape_right_arrow, rotation=45),
            "SW_Arrow": partial(self.shape_right_arrow, rotation=135),
            "Cursor_Arrow": partial(self.shape_right_arrow, rotation=240),
            "Line": self.shape_line,
            "T000": self.shape_t_object,
            "T090": self.shape_t_object,
            "T135": self.shape_t_object,
            "T180": self.shape_t_object,
            "T270": self.shape_t_object,
            "L000": self.shape_l_object,
            "L090": self.shape_l_object,
            "L135": self.shape_l_object,
            "L180": self.shape_l_object,
            "L270": self.shape_l_object,
            "Inv_Hill": self.shape_inv_hill,
            "Hill": self.shape_hill,
            "Clover": self.shape_clover,
            "House": self.shape_house,
        }

    def draw_shape(self, obj: VisualObject):
        try:
            self.shape_router[obj.property.Shape](obj=obj)
        except KeyError:
            self.cache_warn(f"VisualObject received unhandled Shape value {obj.property.Shape}")
            self.shape_nil(obj)

    # ------------- Shape Drawing Cache ---------------------------------

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
        elif shape == "triangle":
            box = QRect(x, y, w, h)
            path.addPolygon(
                QPolygonF(
                    (
                        QPointF(box.bottomLeft()),
                        QPointF(box.center().x(), box.y()),
                        QPointF(box.bottomRight()),
                        QPointF(box.bottomLeft()),
                    )
                )
            )
        elif shape == "diamond":
            box = QRect(x, y, w, h)
            path.addPolygon(
                QPolygonF(
                    (
                        QPointF(box.left(), box.center().y()),
                        QPointF(box.center().x(), box.y()),
                        QPointF(box.right(), box.center().y()),
                        QPointF(box.center().x(), box.bottomLeft().y()),
                        QPointF(box.left(), box.center().y()),
                    )
                )
            )
        elif shape == "cross":
            box = QRect(x, y, w, h)
            qtr_w = box.width() // 4
            qtr_h = box.height() // 4
            a = QPointF(box.left() + qtr_w, box.bottomLeft().y())
            b = QPointF(box.bottomRight().x() - qtr_w, box.bottomRight().y())
            c = QPointF(b.x(), b.y() - qtr_h)
            d = QPointF(box.bottomRight().x(), c.y())
            e = QPointF(d.x(), box.topRight().y() + qtr_h)
            f = QPointF(c.x(), e.y())
            g = QPointF(f.x(), box.topRight().y())
            H = QPointF(a.x(), g.y())
            i = QPointF(a.x(), f.y())
            j = QPointF(box.topLeft().x(), i.y())
            k = QPointF(j.x(), c.y())
            l = QPointF(a.x(), c.y())
            path.addPolygon(QPolygonF((a, b, c, d, e, f, g, H, i, j, k, l, a)))
        elif shape == "arc":
            box = QRect(x, y, w, h)
            path = QPainterPath()
            # old approach
            # path.moveTo(QPoint(box.left(), box.center().y()))
            # path.cubicTo(QPoint(box.left(), box.center().y()),
            #              QPoint(box.center().x(), box.top()),
            #              QPoint(box.right(), box.center().y()))
            # DK approach
            path.moveTo(box.center())
            path.arcTo(QRectF(x, y, w, h), 5, 170)
            path.closeSubpath()
        elif shape == "bar":
            box = QRect(x, y, w, h)
            a = QPointF(box.left(), box.bottomLeft().y() - box.height() // 4)
            b = QPointF(box.right(), a.y())
            c = QPointF(b.x(), box.topRight().y() + box.height() // 4)
            d = QPointF(a.x(), c.y())
            path.addPolygon(QPolygonF((a, b, c, d, a)))
        elif shape == "cross_hairs":
            box = QRect(x, y, w, h)
            gap = 1
            a = QPointF(box.center().x() - gap, box.bottomLeft().y())
            b = QPointF(a.x() + gap, a.y())
            c = QPointF(b.x(), box.center().y() + gap)
            d = QPointF(box.right(), c.y())
            e = QPointF(d.x(), d.y() - gap)
            f = QPointF(c.x(), e.y())
            g = QPointF(f.x(), box.topRight().y())
            h = QPointF(a.x(), g.y())
            i = QPointF(a.x(), e.y())
            j = QPointF(box.left(), i.y())
            k = QPointF(j.x(), c.y())
            l = QPointF(a.x(), k.y() + gap)
            path.addPolygon(QPolygonF((a, b, c, d, e, f, g, h, i, j, k, l, a)))
        elif shape == "right_arrow":
            box = QRect(x, y, w, h)
            a = QPointF(box.right(), box.center().y())
            b = QPointF(box.center().x(), box.topRight().y())
            c = QPointF(b.x(), a.y() - box.height() // 5)
            d = QPointF(box.left(), c.y())
            e = QPointF(d.x(), box.center().y() + box.height() // 5)
            f = QPointF(b.x(), e.y())
            g = QPointF(b.x(), box.bottomLeft().y())
            path.addPolygon(QPolygonF((a, b, c, d, e, f, g, a)))
            path.closeSubpath()
        elif shape == "button":
            corner_size = h * 0.30 if h < w else w * 0.30
            path.addRoundedRect(x, y, w, h, corner_size, corner_size)
        elif shape == "keyboard_button":
            path.addRect(x, y, w, h)
            path.addRect(x, y, w * 0.9, h * 0.9)
        elif shape == "t_object":
            box = QRectF(x, y, w, h)
            path.moveTo(box.topLeft())
            path.lineTo(box.topRight())
            path.moveTo(box.center().x(), box.top())
            path.lineTo(box.center().x(), box.bottom())
        elif shape == "l_object":
            box = QRectF(x, y, w, h)
            path.moveTo(box.topLeft())
            path.lineTo(box.bottomLeft())
            path.lineTo(box.bottomRight())
        elif shape == "hill":
            box = QRectF(x, y, w, h)
            cpx = box.center().x()
            cpy = box.bottomRight().y() + box.height()
            path.moveTo(box.topRight())
            path.cubicTo(box.topRight(), QPoint(cpx, cpy), box.topLeft())
            path.closeSubpath()
        elif shape == "inv_hill":
            box = QRectF(x, y, w, h)
            cpx = box.center().x()
            cpy = box.topRight().y() - box.height()
            path.moveTo(box.bottomRight())
            path.cubicTo(box.bottomRight(), QPoint(cpx, cpy), box.bottomLeft())
            path.closeSubpath()
        elif shape == "house":
            box = QRectF(x, y, w, h)
            path.moveTo(box.bottomLeft())
            path.lineTo(box.left(), box.center().y())
            path.lineTo(box.center().x(), box.top())
            path.lineTo(box.right(), box.center().y())
            path.lineTo(box.bottomRight())
            path.closeSubpath()
        elif shape == "clover":
            box = QRectF(x, y, w, h)
            cx, cy = box.center().x(), box.center().y()
            # draw petals
            offset = w / 4 if w < h else h / 4
            _offset = offset - offset // 4
            petal = QPoint(cx - _offset, cy - _offset)
            path.addEllipse(petal, offset, offset)
            petal = QPoint(cx - _offset, cy + _offset)
            path.addEllipse(petal, offset, offset)
            petal = QPoint(cx + _offset, cy - _offset)
            path.addEllipse(petal, offset, offset)
            petal = QPoint(cx + _offset, cy + _offset)
            path.addEllipse(petal, offset, offset)
            # draw stem
            path.addRect(cx - offset // 2, box.bottom() - offset // 2, offset, offset)
        else:
            self.cache_warn(f'shape_cache has no handler for "{shape}"')
        return path

    # ------------- Draw Command Functions ---------------------------------

    @staticmethod
    def add_leader(x, y, w, h, leader: str, path: QPainterPath, inverted: bool = False):
        """
        A fixed leader is a line from the location of the object in one of the four
        specified directions, with a length equal to twice the greatest of the object
        width or height.
        """
        box = QRectF(x, y, w, h)
        center = box.center()
        length = 1.5 * (w if w > h else h)
        _leader = leader.split("_")[0]
        if inverted:
            _leader = {
                "North": "South",
                "South": "North",
                "East": "West",
                "West": "East",
                "NorthEast": "SouthWest",
                "SouthEast": "NorthWest",
                "NorthWest": "SouthEast",
                "SouthWest": "NorthEast",
            }[_leader]
        if _leader == "North":
            path.moveTo(center.x(), center.y())
            path.lineTo(center.x(), center.y() - length)
        elif _leader == "East":
            path.moveTo(center.x(), center.y())
            path.lineTo(center.x() + length, center.y())
        elif _leader == "South":
            path.moveTo(center.x(), center.y())
            path.lineTo(center.x(), center.y() + length)
        elif _leader == "West":
            path.moveTo(center.x(), center.y())
            path.lineTo(center.x() - length, center.y())
        elif _leader == "NorthWest":
            path.moveTo(center.x(), center.y())
            path.lineTo(center.x() - length, center.y() - length)
        elif _leader == "NorthEast":
            path.moveTo(center.x(), center.y())
            path.lineTo(center.x() + length, center.y() + length)
        elif _leader == "SouthWest":
            path.moveTo(center.x(), center.y())
            path.lineTo(center.x() - length, center.y() - length)
        elif _leader == "SouthEast":
            path.moveTo(center.x(), center.y())
            path.lineTo(center.x() + length, center.y() - length)
        else:
            return

    def shape_nil(self, obj: VisualObject):
        self.painter.setPen(QPen(QColorConstants.LightGray, 2, Qt.PenStyle.SolidLine))
        self.painter.setBrush(Qt.BrushStyle.NoBrush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        self.painter.drawEllipse(x, y, w, h)

    def shape_ellipse(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("ellipse", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
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
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_triangle(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("triangle", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_diamond(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("diamond", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_cross(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("cross", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_arc(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("arc", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_bar(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("bar", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_cross_hairs(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("cross_hairs", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_right_arrow(self, obj, rotation: int = 0):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("right_arrow", x, y, w, h)
        if rotation:
            shape_center = QRect(x, y, w, h).center()
            self.painter.translate(shape_center.x(), shape_center.y())
            self.painter.rotate(rotation)
            self.painter.translate(shape_center.x() * -1, shape_center.y() * -1)

        self.painter.drawPath(path)
        self.painter.resetTransform()

        if obj.property.Leader:
            path = QPainterPath()
            self.add_leader(x, y, w, h, obj.property.Leader, path)
            self.painter.drawPath(path)

    def shape_button(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        pen = QColorConstants.Black
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("button", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_keyboard_button(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        pen = QColorConstants.Black
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("keyboard_button", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_t_object(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("t_object", x, y, w, h)
        # rotation = int(obj.property.Shape[1:])
        rotation = 45  # TEMP FIX
        if rotation:
            shape_center = QRect(x, y, w, h).center()
            self.painter.translate(shape_center.x(), shape_center.y())
            self.painter.rotate(rotation)
            self.painter.translate(shape_center.x() * -1, shape_center.y() * -1)

        self.painter.drawPath(path)
        self.painter.resetTransform()

        if obj.property.Leader:
            path = QPainterPath()
            self.add_leader(x, y, w, h, obj.property.Leader, path)
            self.painter.drawPath(path)

    def shape_l_object(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("l_object", x, y, w, h)
        # rotation = int(obj.property.Shape[1:])
        rotation = 45  # TEMP FIX
        if rotation:
            shape_center = QRect(x, y, w, h).center()
            self.painter.translate(shape_center.x(), shape_center.y())
            self.painter.rotate(rotation)
            self.painter.translate(shape_center.x() * -1, shape_center.y() * -1)

        self.painter.drawPath(path)
        self.painter.resetTransform()

        if obj.property.Leader:
            path = QPainterPath()
            self.add_leader(x, y, w, h, obj.property.Leader, path)
            self.painter.drawPath(path)

    def shape_hill(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        pen = QColorConstants.Black
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("hill", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_inv_hill(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        pen = QColorConstants.Black
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("inv_hill", x, y, w, h)
        if obj.property.Leader:
            self.add_leader(x, y, w, h, obj.property.Leader, path)
        self.painter.drawPath(path)

    def shape_clover(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("clover", x, y, w, h)
        rotation = 180 if "Inv" in obj.property.Shape else 0
        if rotation:
            shape_center = QRect(x, y, w, h).center()
            self.painter.translate(shape_center.x(), shape_center.y())
            self.painter.rotate(rotation)
            self.painter.translate(shape_center.x() * -1, shape_center.y() * -1)

        self.painter.drawPath(path)
        self.painter.resetTransform()

        if obj.property.Leader:
            path = QPainterPath()
            self.add_leader(x, y, w, h, obj.property.Leader, path)
            self.painter.drawPath(path)

    def shape_house(self, obj):
        pen, brush = self.obj_pen_brush(obj)
        self.painter.setPen(pen)
        self.painter.setBrush(brush)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.shape_cache("house", x, y, w, h)
        rotation = 180 if "Inv" in obj.property.Shape else 0
        if rotation:
            shape_center = QRect(x, y, w, h).center()
            self.painter.translate(shape_center.x(), shape_center.y())
            self.painter.rotate(rotation)
            self.painter.translate(shape_center.x() * -1, shape_center.y() * -1)

        self.painter.drawPath(path)
        self.painter.resetTransform()

        if obj.property.Leader:
            path = QPainterPath()
            self.add_leader(x, y, w, h, obj.property.Leader, path)
            self.painter.drawPath(path)

    @memoize_class_method()
    def text_cache(self, x, y, text) -> QPainterPath:
        # TODO: This isn't *quite* centered right on (x,y)
        path = QPainterPath()
        font = QFont(app_font)
        font.setPointSize(round(self.scale * 0.8))
        try:
            font.setWeight(QFont.Light)  # PySide6
        except TypeError:
            font.setWeight(100)  # PyQt6
        self.setFont(font)
        font_height = QGraphicsTextItem("TEXT4HEIGHT").boundingRect().height()
        path.addText(x, y + font_height / 2, font, str(text))
        return path

    def draw_text(self, obj: VisualObject):
        # TODO: Need diff approach for text vs an object with some text.
        #        The former should be sized to the object size. The latter should
        #        probably be a standard size?
        self.painter.setPen(
            QColorConstants.Black if obj.property.Status != "Disappearing" else QColorConstants.LightGray
        )
        self.painter.setBrush(Qt.BrushStyle.SolidPattern)
        x, y, w, h = self.center_and_scale(obj.location, obj.size)
        path = self.text_cache(x, y, obj.property.Text)
        self.painter.drawPath(path)

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
