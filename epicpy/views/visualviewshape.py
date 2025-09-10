import sys
import random
import time
from functools import lru_cache
from timeit import default_timer
from typing import Union

from qtpy.QtCore import QRectF, Qt, QTimer
from qtpy.QtGui import (
    QPainter,
    QPainterPath,
    QTransform,
    QColor,
    QPen,
    QBrush,
    QStaticText,
    QFont,
)
from qtpy.QtWidgets import QApplication, QWidget

from itertools import count

endless_ints = (i for i in count())

# Global configuration
NUM_SHAPES = 25
NUM_ITERATIONS = 10


# --------------------------------------------------
# Custom Rect Class
# --------------------------------------------------
class Rect:
    """
    Rect class with property and iterable access.
    """

    __slots__ = "x", "y", "w", "h"

    def __init__(
        self,
        x: Union[float, int],
        y: Union[float, int],
        w: Union[float, int],
        h: Union[float, int],
    ):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __iter__(self):
        return iter((self.x, self.y, self.w, self.h))

    def __str__(self):
        return f"Rect(Point({self.x}, {self.y}), Rect({self.w}, {self.h}))"


# --------------------------------------------------
# Normalized Shape Functions (cached)
# --------------------------------------------------
@lru_cache(maxsize=32)
def normalized_circle() -> QPainterPath:
    path = QPainterPath()
    # Draw a circle in the unit square from (0,0) to (1,1)
    path.addEllipse(QRectF(0, 0, 1, 1))
    return path


@lru_cache(maxsize=64)
def normalized_triangle() -> QPainterPath:
    path = QPainterPath()
    # Define a triangle in normalized coordinates.
    path.moveTo(0.5, 0)
    path.lineTo(1, 1)
    path.lineTo(0, 1)
    path.closeSubpath()
    return path


# --------------------------------------------------
# Function to Scale, Transform, and Draw Normalized Shapes
# --------------------------------------------------
def draw_normalized_shape(
    shape: str, rect: Rect, painter: QPainter, color: Union[QColor, None] = None
):
    """
    Draws a normalized shape (either 'Circle' or 'Triangle') into the given rect.
    If color is provided, the pen (thickness 2) and brush are set to that color (filled shape);
    if color is None, the pen is set to black (thickness 2) and no brush is used (unfilled shape).
    """
    if color is None:
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
    else:
        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(color))

    # Create a transform: translate then scale the normalized shape.
    transform = QTransform()
    transform.translate(rect.x, rect.y)
    transform.scale(rect.w, rect.h)

    if shape == "Circle":
        normalized_shape = normalized_circle()
    elif shape == "Triangle":
        normalized_shape = normalized_triangle()
    else:
        raise ValueError(f"Unexpected shape: {shape}")

    path = transform.map(normalized_shape)
    painter.drawPath(path)


# --------------------------------------------------
# Optimized Text Drawing Function
# --------------------------------------------------
def draw_optimized_text(
    painter: QPainter,
    text: str,
    x: float,
    y: float,
    bold: bool = True,
    color: Union[QColor, None] = None,
    font: QFont = None,
):
    """
    Draws text using QStaticText for caching.
    Parameters:
      - text: The string to draw.
      - x, y: The top-left position.
      - bold: Boolean flag to render the text in bold.
      - color: The text color (default is black if None).
      - font: Optionally, a preconfigured QFont is used.
    """
    static_text = QStaticText(text)
    static_text.setTextFormat(Qt.TextFormat.PlainText)
    # Use the provided font if available; otherwise, modify the painter's font.
    if font is None:
        font = painter.font()
        font.setBold(bold)
    painter.setFont(font)
    if color is None:
        pen_color = Qt.GlobalColor.black
    else:
        pen_color = color
    painter.setPen(QPen(pen_color))
    painter.drawStaticText(int(x), int(y), static_text)


# --------------------------------------------------
# Custom Widget That Runs the Simulation
# --------------------------------------------------
class ShapeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulation: Normalized Shapes")
        self.setMinimumSize(800, 600)
        self.iteration = 1
        self.shapes = []
        self.generate_shapes()
        # Precompute a bold font from the widget's font.
        self.bold_font = QFont(self.font())
        self.bold_font.setBold(True)
        # We no longer start the iteration timer here.

    def generate_shapes(self):
        """
        Generate NUM_SHAPES random shapes (either 'Circle' or 'Triangle') with random
        positions, sizes, and colors. With a 50% chance, the shape will be filled
        with a random color; otherwise, it will be unfilled.
        """
        self.shapes = []
        width, height = self.width() or 800, self.height() or 600
        margin = 50
        for _ in range(NUM_SHAPES):
            shape_type = random.choice(["Circle", "Triangle"])
            x = random.uniform(margin, width - margin)
            y = random.uniform(margin, height - margin)
            w = random.uniform(20, 100)
            h = random.uniform(20, 100)
            # 50% chance to use a random color; otherwise, None for unfilled.
            if random.choice([True, False]):
                color = QColor(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                )
            else:
                color = None
            self.shapes.append((shape_type, Rect(x, y, w, h), color))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Clear the display.
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        # Draw the shapes.
        for shape_type, rect, color in self.shapes:
            draw_normalized_shape(shape_type, rect, painter, color)
        # Draw the iteration and current time at the top left.
        info_text = f"Iteration Number = {self.iteration} | time = {time.ctime()}"
        draw_optimized_text(
            painter,
            info_text,
            10,
            10,
            bold=True,
            color=QColor("darkblue"),
            font=self.bold_font,
        )
        painter.end()
        print(f"paint_event #{next(endless_ints)}")

    def next_iteration(self):
        """
        Advance the simulation by one iteration: regenerate shapes, update the iteration count,
        and trigger a repaint. The simulation stops after NUM_ITERATIONS iterations.
        """
        if self.iteration < NUM_ITERATIONS:
            self.iteration += 1
            self.generate_shapes()
            self.update()  # Request a repaint
            # Schedule the next iteration in 100 ms.
            QTimer.singleShot(100, self.next_iteration)
        else:
            # Final update so that the last iteration is visible.
            self.update()
            finish_time = default_timer()
            total_time = finish_time - self.start_time
            iteration_time = total_time / NUM_ITERATIONS
            print(
                f"Total Time = {total_time:0.4f} sec. | Iteration Time = {iteration_time:0.4f} sec."
            )

    def showEvent(self, event):
        """
        Start the simulation iterations only once the window is visible.
        """
        super().showEvent(event)
        self.start_time = default_timer()
        QTimer.singleShot(0, self.next_iteration)


# --------------------------------------------------
# Main Application
# --------------------------------------------------
if __name__ == "__main__":
    from qtpy.QtGui import QColorConstants

    app = QApplication(sys.argv)
    g = QColorConstants.Green.name()
    print(f"{g=}")
    widget = ShapeWidget()
    widget.show()
    sys.exit(app.exec())
