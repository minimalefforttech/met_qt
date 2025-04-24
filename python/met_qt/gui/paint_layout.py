# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
""" Simplified wrapper for working with layouts inside a paintevent.
For most cases you can simply use anchor() from paint_utils, this is for 
advanced cases where you require hover support or complex layout management in
a situation where you cannot use normal widgets.
"""
from typing import Optional, Union
from dataclasses import dataclass, field, asdict, replace
from met_qt._internal.qtcompat import QtWidgets, QtCore, QtGui
from enum import Enum, Flag, auto, IntFlag

class ShapeType(Enum):
    Box = 0
    Path = 1

class CornerFlag(IntFlag):
    NoCorners = 0
    TopLeft = auto()
    TopRight = auto()
    BottomLeft = auto()
    BottomRight = auto()
    AllCorners = TopLeft | TopRight | BottomLeft | BottomRight

class PaintOptions(IntFlag):
    NoOptions = 0
    Enabled = auto()
    Hovered = auto()

class BoxPaintLayoutFlag(IntFlag):
    Enabled = auto()
    Visible = auto()
    TransparentForHover = auto()

@dataclass
class PaintStyle:
    brush_color: QtGui.QColor = None  # QColor or None
    brush_role: QtGui.QPalette.ColorRole = None
    pen_color: QtGui.QColor = None
    pen_role: QtGui.QPalette.ColorRole = None
    pen_width: float = 1.0

@dataclass
class PaintItem:
    id: Optional[str] = None
    visible: bool = True
    style: Optional[PaintStyle] = None
    disabled_style: Optional[PaintStyle] = None
    hover_style: Optional[PaintStyle] = None

@dataclass
class BoxShape(PaintItem):
    shape_type: ShapeType = ShapeType.Box
    painter_path: QtGui.QPainterPath = None
    corner_radius: int = 0  # Default to 0 for normal box
    rounded_corners: CornerFlag = CornerFlag.AllCorners
    content_margin: int = 4

    def __post_init__(self):
        if self.style is None:
            self.style = PaintStyle()

@dataclass
class BoxText(PaintItem):
    text: str = ""
    wordWrap: bool = False
    alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignCenter
    colorRole: QtGui.QPalette.ColorRole = QtGui.QPalette.ColorRole.WindowText
    font: QtGui.QFont = field(default_factory=QtGui.QFont)
    elideMode: QtCore.Qt.TextElideMode = QtCore.Qt.TextElideMode.ElideNone

    def __post_init__(self):
        if self.style is None:
            self.style = PaintStyle()

    def sizeHint(self):
        metrics = QtGui.QFontMetrics(self.font)
        lines = self.text.splitlines() or ['']
        width = max(metrics.horizontalAdvance(line) for line in lines)
        height = metrics.height() * len(lines)
        return QtCore.QSize(width, height)

class BoxPaintItem:
    def __init__(self, shape: Union[None, BoxShape] = None, text: Union[str, BoxText] = None):
        self.shape = shape
        if isinstance(text, str):
            text = BoxText(text=text)
        self.text = text

    def paint(self, painter, rect, widget=None, options=PaintOptions.Enabled):
        if self.shape and self.shape.visible:
            self._draw_box(painter, self.shape, rect, widget, options)
        if self.text and self.text.visible and self.text.text:
            self._draw_text(painter, self.text, rect, widget, options)

    def hit_test(self, rect, pos):
        hit = False
        if not self.shape or not self.shape.visible:
            hit = False
        elif self.shape.shape_type == ShapeType.Box:
            hit = rect.contains(pos)
        else:
            path = self._resolve_path(self.shape, rect)
            hit = not path.isEmpty() and path.contains(QtCore.QPointF(pos))
        return hit

    def _resolve_style(self, base: Optional[PaintStyle], disabled_style: Optional[PaintStyle], hover_style: Optional[PaintStyle], options:PaintOptions) -> PaintStyle:
        base = base or PaintStyle()
        if not (options & PaintOptions.Enabled) and disabled_style:
            return replace(base, **{k:v for k, v in asdict(disabled_style).items() if v is not None})
        if (options & PaintOptions.Hovered) and hover_style:
            return replace(base, **{k:v for k, v in asdict(hover_style).items() if v is not None})
        return base

    def _draw_box(self, painter, shape: BoxShape, rect, widget=None, options:PaintOptions=PaintOptions.Enabled):
        painter.save()
        style = self._resolve_style(shape.style, shape.disabled_style, shape.hover_style, options)
        color = style.brush_color
        if color is None and style.brush_role is not None and widget:
            color = widget.palette().color(style.brush_role)
        if color is not None:
            painter.setBrush(QtGui.QBrush(color))
        else:
            painter.setBrush(QtCore.Qt.NoBrush)
        pen_color = style.pen_color
        if pen_color is None and widget and style.pen_role:
            pen_color = widget.palette().color(style.pen_role)
        if not pen_color:
            painter.setPen(QtCore.Qt.NoPen)
        else:
            painter.setPen(QtGui.QPen(pen_color, style.pen_width))
        if shape.shape_type == ShapeType.Box:
            if shape.corner_radius and shape.corner_radius > 0:
                if shape.rounded_corners == CornerFlag.AllCorners:
                    painter.drawRoundedRect(rect, shape.corner_radius, shape.corner_radius)
                else:
                    path = self._resolve_path(shape, rect)
                    if not path.isEmpty():
                        painter.drawPath(path)
            else:
                painter.drawRect(rect)
        elif shape.shape_type == ShapeType.Path and shape.painter_path:
            path = self._resolve_path(shape, rect)
            if not path.isEmpty():
                painter.drawPath(path)
        painter.restore()

    def _draw_text(self, painter, text: BoxText, rect, widget=None, options:PaintOptions=PaintOptions.Enabled):
        painter.save()
        style = self._resolve_style(text.style, text.disabled_style, text.hover_style, options)
        painter.setFont(text.font)
        color = style.brush_color
        palette = widget.palette() if widget else QtWidgets.QApplication.palette()
        if color is None:
            color = palette.color(style.pen_role or QtGui.QPalette.ColorRole.WindowText)
        style_widget = widget.style() if widget else QtWidgets.QApplication.style()
        style_widget.drawItemText(painter, rect, int(text.alignment), color, True, text.text)
        painter.restore()

    def _resolve_path(self, shape, rect):
        # Returns a QPainterPath for the shape in the given rect
        path = QtGui.QPainterPath()
        if shape.shape_type == ShapeType.Box:
            if shape.corner_radius and shape.corner_radius > 0:
                if shape.rounded_corners == CornerFlag.AllCorners:
                    path.addRoundedRect(QtCore.QRectF(rect), shape.corner_radius, shape.corner_radius)
                else:
                    if shape.rounded_corners & CornerFlag.TopLeft:
                        path.moveTo(rect.left() + shape.corner_radius, rect.top())
                    else:
                        path.moveTo(rect.left(), rect.top())
                    if shape.rounded_corners & CornerFlag.TopRight:
                        path.lineTo(rect.right() - shape.corner_radius, rect.top())
                        path.arcTo(
                            rect.right() - shape.corner_radius * 2, rect.top(),
                            shape.corner_radius * 2, shape.corner_radius * 2,
                            90, -90
                        )
                    else:
                        path.lineTo(rect.right(), rect.top())
                    if shape.rounded_corners & CornerFlag.BottomRight:
                        path.lineTo(rect.right(), rect.bottom() - shape.corner_radius)
                        path.arcTo(
                            rect.right() - shape.corner_radius * 2, rect.bottom() - shape.corner_radius * 2,
                            shape.corner_radius * 2, shape.corner_radius * 2,
                            0, -90
                        )
                    else:
                        path.lineTo(rect.right(), rect.bottom())
                    if shape.rounded_corners & CornerFlag.BottomLeft:
                        path.lineTo(rect.left() + shape.corner_radius, rect.bottom())
                        path.arcTo(
                            rect.left(), rect.bottom() - shape.corner_radius * 2,
                            shape.corner_radius * 2, shape.corner_radius * 2,
                            270, -90
                        )
                    else:
                        path.lineTo(rect.left(), rect.bottom())
                    if shape.rounded_corners & CornerFlag.TopLeft:
                        path.lineTo(rect.left(), rect.top() + shape.corner_radius)
                        path.arcTo(
                            rect.left(), rect.top(),
                            shape.corner_radius * 2, shape.corner_radius * 2,
                            180, -90
                        )
                    else:
                        path.lineTo(rect.left(), rect.top())
                    path.closeSubpath()
            else:
                path.addRect(QtCore.QRectF(rect))
        elif shape.shape_type == ShapeType.Path and shape.painter_path:
            source_rect = shape.painter_path.boundingRect()
            path = QtGui.QPainterPath(shape.painter_path)
            if not source_rect.isEmpty():
                transform = QtGui.QTransform()
                scale_x = rect.width() / source_rect.width()
                scale_y = rect.height() / source_rect.height()
                transform.translate(rect.x() - source_rect.x() * scale_x, rect.y() - source_rect.y() * scale_y)
                transform.scale(scale_x, scale_y)
                path = transform.map(path)
        return path


class BoxPaintLayout(QtWidgets.QBoxLayout):
    """
    Layout for painting colored boxes that can also contain other layout items.
    Supports custom painting, hit-testing, and explicit size hints.
    """

    def __init__(self, direction: QtWidgets.QBoxLayout.Direction = QtWidgets.QBoxLayout.Direction.TopToBottom):
        """
        Initialize the BoxPaintLayout.

        Args:
            direction: Layout direction (default: TopToBottom).
        """
        super().__init__(direction)
        self._explicit_size_hint: Optional[QtCore.QSize] = None
        self._explicit_min_size: Optional[QtCore.QSize] = None
        self._explicit_max_size: Optional[QtCore.QSize] = None
        self._paint_items: list[BoxPaintItem] = []
        self._flags: BoxPaintLayoutFlag = BoxPaintLayoutFlag.Enabled | BoxPaintLayoutFlag.Visible

    @QtCore.Property(int)
    def flags(self) -> int:
        """
        Get the current layout flags as an integer.
        """
        return int(self._flags)

    @flags.setter
    def flags(self, value: int):
        """
        Set the layout flags.
        Args:
            value (int): The new flags value.
        """
        self._flags = BoxPaintLayoutFlag(value)
        self.update()
        self.invalidate()

    def setSizeHint(self, size: Union[QtCore.QSize, tuple[int, int], list[int]]):
        """
        Set explicit preferred size hint.
        Args:
            size: The preferred size.
        """
        if isinstance(size, (tuple, list)) and len(size) == 2:
            self._explicit_size_hint = QtCore.QSize(size[0], size[1])
        else:
            self._explicit_size_hint = size

    def setMinimumSize(self, size: Union[QtCore.QSize, tuple[int, int], list[int]]):
        """
        Set explicit minimum size.
        Args:
            size: The minimum size.
        """
        if isinstance(size, (tuple, list)) and len(size) == 2:
            self._explicit_min_size = QtCore.QSize(size[0], size[1])
        else:
            self._explicit_min_size = size

    def setMaximumSize(self, size: Union[QtCore.QSize, tuple[int, int], list[int]]):
        """
        Set explicit maximum size.
        Args:
            size: The maximum size.
        """
        if isinstance(size, (tuple, list)) and len(size) == 2:
            self._explicit_max_size = QtCore.QSize(size[0], size[1])
        else:
            self._explicit_max_size = size

    def sizeHint(self) -> QtCore.QSize:
        """
        Return the preferred size (explicit or calculated).
        The size is determined by the union of all paint items' size hints and margins.
        Returns (0, 0) if there are no paint items.
        """
        if self._explicit_size_hint:
            return self._explicit_size_hint
        if not self._paint_items:
            return QtCore.QSize(0, 0)
        max_width = 0
        max_height = 0
        for item in self._paint_items:
            if item.text and hasattr(item.text, 'sizeHint'):
                text_size = item.text.sizeHint()
            else:
                text_size = QtCore.QSize(0, 0)
            margin = item.shape.content_margin if item.shape and hasattr(item.shape, 'content_margin') else 0
            max_width = max(max_width, text_size.width() + 2 * margin)
            max_height = max(max_height, text_size.height() + 2 * margin)
        base_hint = super().sizeHint()
        return QtCore.QSize(
            max(base_hint.width(), max_width),
            max(base_hint.height(), max_height)
        )

    def minimumSize(self) -> QtCore.QSize:
        """
        Return the minimum size (explicit or calculated).
        """
        if self._explicit_min_size:
            return self._explicit_min_size
        base_min = super().minimumSize()
        return base_min

    def maximumSize(self) -> QtCore.QSize:
        """
        Return the maximum size (explicit or layout's).
        """
        if self._explicit_max_size:
            return self._explicit_max_size
        return super().maximumSize()

    def set_paint_items(self, items: list[BoxPaintItem]):
        """
        Set the list of BoxPaintItem objects to be painted.
        Args:
            items: The paint items.
        """
        self._paint_items = list(items)
        self.update()
        self.invalidate()

    def get_paint_items(self) -> list[BoxPaintItem]:
        """
        Get the list of BoxPaintItem objects.
        """
        return list(self._paint_items)

    def paint(self, painter: QtGui.QPainter, options: PaintOptions, mouse_pos: Optional[QtCore.QPoint] = None):
        """
        Paint all BoxPaintItem objects in the layout.
        Args:
            painter: The painter to use.
            options: Paint options (enabled, hovered, etc).
            mouse_pos: Mouse position for hover detection.
        """
        layout_geom = self.geometry()
        for item in self._paint_items:
            item_flags = PaintOptions.NoOptions
            enabled = options & PaintOptions.Enabled and self.flags & BoxPaintLayoutFlag.Enabled
            if enabled:
                item_flags |= PaintOptions.Enabled
            if options & PaintOptions.Hovered and mouse_pos is not None:
                if item.hit_test(layout_geom, mouse_pos):
                    item_flags |= PaintOptions.Hovered
            item.paint(painter,
                       layout_geom,
                       widget=painter.device() if isinstance(painter.device(), QtWidgets.QWidget) else None,
                       options=item_flags)

    @classmethod
    def _recurse_paint(cls, layout: QtWidgets.QLayout, painter: QtGui.QPainter, mouse_pos: Optional[QtCore.QPoint], hovered_layouts: set['BoxPaintLayout']):
        """
        Recursively paint BoxPaintLayout items.
        Args:
            layout (QLayout): The layout to paint.
            painter (QPainter): The painter to use.
            mouse_pos (QPoint, optional): Mouse position for hover detection.
            hovered_layouts (set[BoxPaintLayout]): Layouts under the mouse.
        """
        if not layout or not layout.geometry().isValid():
            return
        if isinstance(layout, BoxPaintLayout):
            if not layout.flags & BoxPaintLayoutFlag.Visible:
                return
            options = PaintOptions.NoOptions
            if layout.flags & BoxPaintLayoutFlag.Enabled:
                if layout.widget() and layout.widget().isEnabled():
                    options |= PaintOptions.Enabled
            if layout in hovered_layouts:
                options |= PaintOptions.Hovered
            layout.paint(painter, options, mouse_pos)
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and isinstance(item, QtWidgets.QLayoutItem):
                child_layout = item.layout()
                cls._recurse_paint(child_layout, painter, mouse_pos, hovered_layouts)

    @classmethod
    def render(cls, layout: QtWidgets.QLayout, painter: QtGui.QPainter, mouse_pos: Optional[QtCore.QPoint] = None):
        """
        Render the layout and its children, handling hover and transparency.
        Args:
            layout (QLayout): The root layout to render.
            painter (QPainter): The painter to use.
            mouse_pos (QPoint, optional): Mouse position for hover detection.
        """
        layout_geom = layout.geometry()
        rect = layout_geom
        if not rect.isValid() or rect.width() <= 0 or rect.height() <= 0:
            return
        layouts = cls.hit_test(layout, mouse_pos)
        hovered_layouts: set[BoxPaintLayout] = set()
        for each in reversed(layouts):
            hovered_layouts.add(each)
            if each.flags & BoxPaintLayoutFlag.TransparentForHover:
                continue
            for item in each.get_paint_items():
                if item.shape and item.shape.hover_style:
                    break
            else:
                continue
            break
        cls._recurse_paint(layout, painter, mouse_pos, hovered_layouts)

    @staticmethod
    def hit_test(layout: QtWidgets.QLayout, pos: QtCore.QPoint, hit_items: Optional[list['BoxPaintLayout']] = None) -> list['BoxPaintLayout']:
        """
        Recursively check which BoxPaintLayout items contain the point, using painter path if needed.
        Args:
            layout (QLayout): Layout to test (typically a BoxPaintLayout).
            pos (QPoint): Point in widget coordinates.
            hit_items (list, optional): List to append hits to.
        Returns:
            list[BoxPaintLayout]: List of BoxPaintLayout items under the point (outermost to innermost).
        """
        if hit_items is None:
            hit_items = []
        if not layout or not layout.geometry().isValid():
            return hit_items
        if isinstance(layout, BoxPaintLayout):
            rect = layout.geometry()
            for item in layout._paint_items:
                if item.hit_test(rect, pos):
                    hit_items.append(layout)
                    break
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if not item or not item.geometry().isValid():
                continue
            rect = item.geometry()
            if rect.width() <= 0 or rect.height() <= 0:
                continue
            child_layout = item.layout() if isinstance(item, QtWidgets.QLayoutItem) else None
            if child_layout:
                BoxPaintLayout.hit_test(child_layout, pos, hit_items)
        return hit_items