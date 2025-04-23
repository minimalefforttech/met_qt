from typing import Optional
from dataclasses import dataclass, field, asdict, replace
from PySide6 import QtWidgets, QtCore, QtGui
from enum import Enum, Flag, auto
import sys

class ShapeType(Enum):
    Box = 0
    Path = 1

class CornerFlag(Flag):
    TopLeft = auto()
    TopRight = auto()
    BottomLeft = auto()
    BottomRight = auto()
    AllCorners = TopLeft | TopRight | BottomLeft | BottomRight

@dataclass
class PaintStyle:
    brush_color: QtGui.QColor = None  # QColor or None
    brush_role: QtGui.QPalette.ColorRole = None
    pen_color: QtGui.QColor = field(default_factory=lambda: QtGui.QColor(QtCore.Qt.GlobalColor.black))
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
    def __init__(self, shape: Optional[BoxShape] = None, text: Optional[BoxText] = None, draw_text=True):
        self.shape = shape
        self.text = text
        self.draw_text = draw_text

    def __repr__(self):
        return (f"<BoxPaintItem shape={self.shape!r} text={getattr(self.text, 'text', None)!r} "
                f"draw_text={self.draw_text} at {hex(id(self))}>")

    def paint(self, painter, rect, widget=None, enabled=True, hovered=False):
        if self.shape and self.shape.visible:
            self._draw_box(painter, self.shape, rect, widget, enabled, hovered)
        if self.draw_text and self.text and self.text.visible and self.text.text:
            self._draw_text(painter, self.text, rect, widget, enabled, hovered)

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

    def _resolve_style(self, base: Optional[PaintStyle], disabled_style: Optional[PaintStyle], hover_style: Optional[PaintStyle], enabled: bool, hovered: bool) -> PaintStyle:
        base = base or PaintStyle()
        if not enabled and disabled_style:
            return replace(base, **{k:v for k, v in asdict(disabled_style).items() if v is not None})
        if hovered and hover_style:
            return replace(base, **{k:v for k, v in asdict(hover_style).items() if v is not None})
        return base

    def _draw_box(self, painter, shape: BoxShape, rect, widget=None, enabled=True, hovered=False):
        painter.save()
        style = self._resolve_style(shape.style, shape.disabled_style, shape.hover_style, enabled, hovered)
        color = style.brush_color
        if color is None and style.brush_role is not None and widget:
            color = widget.palette().color(style.brush_role)
        if color is not None:
            painter.setBrush(QtGui.QBrush(color))
        else:
            painter.setBrush(QtCore.Qt.NoBrush)
        pen_color = style.pen_color
        if pen_color is None and style.pen_role is not None and widget:
            pen_color = widget.palette().color(style.pen_role)
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

    def _draw_text(self, painter, text: BoxText, rect, widget=None, enabled=True, hovered=False):
        painter.save()
        style = self._resolve_style(text.style, text.disabled_style, text.hover_style, enabled, hovered)
        painter.setFont(text.font)
        color = style.brush_color
        if color is None and style.brush_role is not None and widget:
            color = widget.palette().color(style.brush_role)
        if color is not None:
            painter.setPen(QtGui.QPen(color))
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.black))
        palette = widget.palette() if widget else QtWidgets.QApplication.palette()
        style_widget = widget.style() if widget else QtWidgets.QApplication.style()
        style_widget.drawItemText(painter, rect, int(text.alignment), palette, True, text.text, text.colorRole)
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

class BoxPaintLayoutFlag(Flag):
    Enabled = auto()
    Visible = auto()
    Interactive = auto()
    TransparentForHover = auto()

class BoxPaintLayout(QtWidgets.QBoxLayout):
    """Layout for painting colored boxes that can also contain other layout items."""
    clicked = QtCore.Signal()

    def __init__(self, direction=QtWidgets.QBoxLayout.Direction.TopToBottom):
        """Initialize with direction and either a QColor or a palette role from Qt.ColorRole."""
        super().__init__(direction)
        self._explicit_size_hint = None
        self._explicit_min_size = None
        self._explicit_max_size = None
        self._paint_items = []
        self._mouse_pos = None
        self._flags = BoxPaintLayoutFlag.Enabled | BoxPaintLayoutFlag.Visible

    @QtCore.Property(int)
    def flags(self):
        return int(self._flags)

    @flags.setter
    def flags(self, value):
        self._flags = BoxPaintLayoutFlag(value)
        self.update()
        self.invalidate()

    def has_flag(self, flag):
        return bool(self._flags & flag)

    # --- Custom Size Hint Methods ---
    def setSizeHint(self, size):
        """Set explicit preferred size hint."""
        if isinstance(size, (tuple, list)) and len(size) == 2:
            self._explicit_size_hint = QtCore.QSize(size[0], size[1])
        else:
            self._explicit_size_hint = size

    def setMinimumSize(self, size):
        """Set explicit minimum size."""
        if isinstance(size, (tuple, list)) and len(size) == 2:
            self._explicit_min_size = QtCore.QSize(size[0], size[1])
        else:
            self._explicit_min_size = size

    def setMaximumSize(self, size):
        """Set explicit maximum size."""
        if isinstance(size, (tuple, list)) and len(size) == 2:
            self._explicit_max_size = QtCore.QSize(size[0], size[1])
        else:
            self._explicit_max_size = size

    # Override QBoxLayout's size methods when explicit sizes are set
    def sizeHint(self):
        """Return the preferred size (explicit or calculated)."""
        if self._explicit_size_hint:
            return self._explicit_size_hint
        base_hint = super().sizeHint()
        if not self._paint_items:
            return base_hint
        # If text is present, use its size as a minimum
        text_size = self._paint_items[0].text.sizeHint() if self._paint_items and self._paint_items[0].draw_text else QtCore.QSize(0, 0)
        # Ensure minimum sensible size if layout is empty
        if self.count() == 0:
            base_hint = QtCore.QSize(100, 50)
        # Take the max of base_hint and text_size
        return QtCore.QSize(
            max(base_hint.width(), text_size.width() + 2 * self._paint_items[0].shape.content_margin),
            max(base_hint.height(), text_size.height() + 2 * self._paint_items[0].shape.content_margin)
        )

    def minimumSize(self):
        """Return the minimum size (explicit or calculated)."""
        if self._explicit_min_size:
            return self._explicit_min_size
        base_min = super().minimumSize()
        return base_min

    def maximumSize(self):
        """Return the maximum size (explicit or layout's)."""
        if self._explicit_max_size:
            return self._explicit_max_size
        return super().maximumSize()

    def set_paint_items(self, items):
        """Set the list of BoxPaintItem objects to be painted."""
        self._paint_items = list(items)
        self.update()
        self.invalidate()

    def get_paint_items(self):
        """Get the list of BoxPaintItem objects."""
        return self._paint_items

    @QtCore.Property(QtCore.QPoint)
    def mouse_pos(self):
        return self._mouse_pos
    
    @mouse_pos.setter
    def mouse_pos(self, pos):
        self._mouse_pos = pos
        self.update()
        self.invalidate()

    def paint(self, painter, rect=None):
        layout_geom = self.geometry()
        rect = layout_geom
        if not rect.isValid() or rect.width() <= 0 or rect.height() <= 0:
            return

        # Determine if any child BoxPaintLayout under the mouse is handling hover
        child_hover_handled = False
        if self._mouse_pos is not None:
            for i in range(self.count()):
                item = self.itemAt(i)
                layout = item.layout() if item and isinstance(item, QtWidgets.QLayoutItem) else None
                if layout and isinstance(layout, BoxPaintLayout):
                    child_rect = item.geometry()
                    if child_rect.isValid() and child_rect.contains(self._mouse_pos):
                        # Check if child handles hover
                        for paint_item in layout._paint_items:
                            hover_style = getattr(paint_item.shape, 'hover_style', None) or getattr(paint_item.text, 'hover_style', None)
                            if hover_style and not layout.has_flag(BoxPaintLayoutFlag.TransparentForHover):
                                child_hover_handled = True
                                break
                if child_hover_handled:
                    break

        for idx, item in enumerate(self._paint_items):
            hovered = False
            hover_allowed = self.has_flag(BoxPaintLayoutFlag.Enabled) and self.has_flag(BoxPaintLayoutFlag.Visible)
            hover_transparent = self.has_flag(BoxPaintLayoutFlag.TransparentForHover)
            hover_style = getattr(item.shape, 'hover_style', None) or getattr(item.text, 'hover_style', None)
            # Only show hover if not handled by a child
            if self._mouse_pos is not None and hover_allowed and not hover_transparent and hover_style and not child_hover_handled:
                mapped_pos = QtCore.QPoint(self._mouse_pos.x() + layout_geom.x(), self._mouse_pos.y() + layout_geom.y())
                hovered = item.hit_test(layout_geom, mapped_pos)
            item.paint(painter, layout_geom, widget=painter.device(), enabled=self.has_flag(BoxPaintLayoutFlag.Enabled), hovered=hovered)

        def paint_box_layouts_recursively(layout_item, mouse_pos):
            if not layout_item or not layout_item.geometry().isValid():
                return
            child_rect = layout_item.geometry()
            if child_rect.width() <= 0 or child_rect.height() <= 0:
                return
            layout = layout_item.layout() if isinstance(layout_item, QtWidgets.QLayoutItem) else None
            if layout:
                if isinstance(layout, BoxPaintLayout):
                    if mouse_pos is not None:
                        child_mapped_pos = QtCore.QPoint(mouse_pos.x() - child_rect.x(), mouse_pos.y() - child_rect.y())
                        layout._mouse_pos = child_mapped_pos
                        layout.paint(painter, child_rect)
                        layout._mouse_pos = None
                    else:
                        layout.paint(painter, child_rect)
                else:
                    for j in range(layout.count()):
                        subitem = layout.itemAt(j)
                        paint_box_layouts_recursively(subitem, mouse_pos)

        for i in range(self.count()):
            item = self.itemAt(i)
            paint_box_layouts_recursively(item, self._mouse_pos)

    def hit_test(self, pos, hit_items=None):
        """Recursively check which BoxPaintLayout items contain the point, using painter path if needed.

        Args:
            pos: QPoint or QPointF in widget coordinates
            hit_items: (optional) list to append hits to

        Returns:
            List of BoxPaintLayout items under the point (outermost to innermost)
        """
        if hit_items is None:
            hit_items = []
        rect = self.geometry()
        for item in self._paint_items:
            if item.hit_test(rect, pos):
                hit_items.append(self)
                break
        for i in range(self.count()):
            item = self.itemAt(i)
            if not item or not item.geometry().isValid():
                continue
            rect = item.geometry()
            if rect.width() <= 0 or rect.height() <= 0:
                continue
            # Recurse into any layout, and collect BoxPaintLayout hits
            layout = None
            if isinstance(item, QtWidgets.QLayoutItem):
                layout = item.layout()
            if layout:
                if isinstance(layout, BoxPaintLayout):
                    layout.hit_test(pos, hit_items)
                else:
                    for j in range(layout.count()):
                        subitem = layout.itemAt(j)
                        if not subitem or not subitem.geometry().isValid():
                            continue
                        subrect = subitem.geometry()
                        if subrect.width() <= 0 or subrect.height() <= 0:
                            continue
                        sublayout = subitem.layout() if isinstance(subitem, QtWidgets.QLayoutItem) else None
                        if sublayout and isinstance(sublayout, BoxPaintLayout):
                            sublayout.hit_test(pos, hit_items)
        return hit_items


class BoxLayoutWidget(QtWidgets.QWidget):
    """Widget that uses box layouts for painting and positioning nested items."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        layout = BoxPaintLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setMinimumSize(100, 100)

    def addBox(self, box_layout):
        if not isinstance(box_layout, BoxPaintLayout):
            raise TypeError("Expected BoxPaintLayout")
        self.layout().addLayout(box_layout)
        self.update()

    def addSpacing(self, size):
        self.layout().addSpacing(size)
        self.update()

    def addStretch(self, stretch=1):
        self.layout().addStretch(stretch)
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        try:
            if not painter.begin(self):
                return
            opt = QtWidgets.QStyleOption()
            opt.initFrom(self)
            self.style().drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            self.layout().paint(painter)
        finally:
            painter.end()

    def mousePressEvent(self, event):
        if self.layout().has_flag(BoxPaintLayoutFlag.Interactive) and event.button() == QtCore.Qt.MouseButton.LeftButton:
            hit_items = self.layout().hit_test(event.pos())
            if hit_items:
                self.layout().clicked.emit()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Pass mouse position to main layout for hover
        if self.layout():
            self.layout().mouse_pos = event.pos()
        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        # Clear hover when mouse leaves widget
        if self.layout():
            self.layout().mouse_pos = None
        self.update()
        super().leaveEvent(event)


# --- Example Usage ---
if __name__ == "__main__":
    print("Starting nested box layout example with standard Qt layouts")
    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()

    # Create the main widget
    box_widget = BoxLayoutWidget()

    # Example fonts
    font_bold = QtGui.QFont()
    font_bold.setBold(True)
    font_italic = QtGui.QFont()
    font_italic.setItalic(True)
    font_large = QtGui.QFont()
    font_large.setPointSize(16)

    # 1. Add a top-level box (rectangle, centered bold text)
    top_shape = BoxShape(
        style=PaintStyle(brush_color=QtGui.QColor("dodgerblue")),
        hover_style=PaintStyle(brush_color=QtGui.QColor("lightyellow")),  # Light yellow highlight on hover
        shape_type=ShapeType.Box
    )
    top_text = BoxText(
        text="Main Container",
        alignment=QtCore.Qt.AlignmentFlag.AlignCenter,
        font=font_bold,
        style=PaintStyle()
    )
    top_box = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    top_box.setObjectName("top_box")
    top_box.setSizeHint((400, 500))
    top_box.set_paint_items([BoxPaintItem(shape=top_shape, text=top_text)])

    # 2. Nested box: rounded, left-aligned italic text, with hover style
    nested_shape = BoxShape(
        style=PaintStyle(brush_color=QtGui.QColor("orange")),
        hover_style=PaintStyle(brush_color=QtGui.QColor("#FFD580")),
        shape_type=ShapeType.Box,
        corner_radius=15
    )
    nested_text = BoxText(
        text="Horizontal Box",
        alignment=QtCore.Qt.AlignmentFlag.AlignLeft,
        font=font_italic,
        style=PaintStyle()
    )
    nested_box1 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.LeftToRight)
    nested_box1.setObjectName("nested_box1")
    nested_box1.setSizeHint((200, 100))
    nested_box1.set_paint_items([BoxPaintItem(shape=nested_shape, text=nested_text)])

    # 3. Inner box: rounded, right-aligned large text, with disabled style
    inner_shape1 = BoxShape(
        style=PaintStyle(brush_color=QtGui.QColor("lightgreen")),
        hover_style=PaintStyle(brush_color=QtGui.QColor("#red")),
        disabled_style=PaintStyle(brush_color=QtGui.QColor("#A0A0A0")),
        shape_type=ShapeType.Box,
        corner_radius=10,
        rounded_corners=CornerFlag.TopLeft | CornerFlag.BottomLeft
    )
    inner_text1 = BoxText(
        text="Green Box",
        alignment=QtCore.Qt.AlignmentFlag.AlignRight,
        font=font_large,
        style=PaintStyle()
    )
    inner_box1 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    inner_box1.setObjectName("inner_box1")
    inner_box1.setSizeHint((90, 90))
    inner_box1.set_paint_items([BoxPaintItem(shape=inner_shape1, text=inner_text1)])

    # 4. Inner box: rounded, word-wrapped, centered text, invisible
    inner_shape2 = BoxShape(
        style=PaintStyle(brush_role=QtGui.QPalette.ColorRole.Highlight),
        shape_type=ShapeType.Box,
        corner_radius=10,
        rounded_corners=CornerFlag.TopRight | CornerFlag.BottomRight,
        visible=False
    )
    inner_text2 = BoxText(
        text="Highlight\nBox",
        alignment=QtCore.Qt.AlignmentFlag.AlignCenter,
        wordWrap=True,
        style=PaintStyle(),
        visible=False
    )
    inner_box2 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    inner_box2.setObjectName("inner_box2")
    inner_box2.setSizeHint((90, 90))
    inner_box2.set_paint_items([BoxPaintItem(shape=inner_shape2, text=inner_text2)])

    # 5. Custom path (star), top-aligned text
    star_path = QtGui.QPainterPath()
    star_path.moveTo(50, 0)
    star_path.lineTo(60, 35)
    star_path.lineTo(100, 35)
    star_path.lineTo(70, 60)
    star_path.lineTo(80, 100)
    star_path.lineTo(50, 75)
    star_path.lineTo(20, 100)
    star_path.lineTo(30, 60)
    star_path.lineTo(0, 35)
    star_path.lineTo(40, 35)
    star_path.closeSubpath()
    star_shape = BoxShape(
        style=PaintStyle(brush_color=QtGui.QColor("lightpink")),
        shape_type=ShapeType.Path,
        painter_path=star_path
    )
    star_text = BoxText(
        text="Star Shape",
        alignment=QtCore.Qt.AlignmentFlag.AlignTop,
        style=PaintStyle()
    )
    nested_box2 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    nested_box2.setObjectName("nested_box2")
    nested_box2.setSizeHint((200, 100))
    nested_box2.set_paint_items([BoxPaintItem(shape=star_shape, text=star_text)])

    # 6. Grid layout with painted boxes (various alignments)
    standard_grid = QtWidgets.QGridLayout()
    standard_grid.setContentsMargins(10, 10, 10, 10)
    standard_grid.setSpacing(8)
    grid_box1 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    grid_box1.setObjectName("grid_box1")
    grid_box1.setSizeHint((80, 60))
    grid_box1.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("lightcoral")),
                            hover_style=PaintStyle(brush_color=QtGui.QColor("red")),  # Light blue highlight
                            shape_type=ShapeType.Box, corner_radius=5),
            text=BoxText(text="Grid 1,1", alignment=QtCore.Qt.AlignmentFlag.AlignLeft, style=PaintStyle())
        )
    ])
    grid_box2 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    grid_box2.setObjectName("grid_box2")
    grid_box2.setSizeHint((80, 60))
    grid_box2.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("palegreen")), shape_type=ShapeType.Box),
            text=BoxText(text="Grid 1,2", alignment=QtCore.Qt.AlignmentFlag.AlignRight, style=PaintStyle())
        )
    ])
    grid_box3 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    grid_box3.setObjectName("grid_box3")
    grid_box3.setSizeHint((80, 60))
    grid_box3.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("cornflowerblue")), shape_type=ShapeType.Box, corner_radius=8, rounded_corners=CornerFlag.TopLeft | CornerFlag.BottomRight),
            text=BoxText(text="Grid 2,1", alignment=QtCore.Qt.AlignmentFlag.AlignBottom, style=PaintStyle())
        )
    ])
    grid_box4 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    grid_box4.setObjectName("grid_box4")
    grid_box4.setSizeHint((80, 60))
    grid_box4.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("khaki")), shape_type=ShapeType.Box),
            text=BoxText(text="Grid 2,2", alignment=QtCore.Qt.AlignmentFlag.AlignVCenter, style=PaintStyle())
        )
    ])
    standard_grid.addLayout(grid_box1, 0, 0)
    standard_grid.addLayout(grid_box2, 0, 1)
    standard_grid.addLayout(grid_box3, 1, 0)
    standard_grid.addLayout(grid_box4, 1, 1)

    # 7. Horizontal layout with painted boxes (diamond, different fonts)
    standard_hbox = QtWidgets.QHBoxLayout()
    standard_hbox.setContentsMargins(5, 5, 5, 5)
    standard_hbox.setSpacing(10)
    hbox_item1 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    hbox_item1.setObjectName("hbox_item1")
    hbox_item1.setSizeHint((60, 40))
    hbox_item1.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("plum")), shape_type=ShapeType.Box, corner_radius=5, rounded_corners=CornerFlag.TopLeft | CornerFlag.TopRight),
            text=BoxText(text="HBox 1", alignment=QtCore.Qt.AlignmentFlag.AlignLeft, font=font_bold, style=PaintStyle())
        )
    ])
    hbox_item2 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    hbox_item2.setObjectName("hbox_item2")
    hbox_item2.setSizeHint((60, 40))
    hbox_item2.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("mediumaquamarine")), shape_type=ShapeType.Box),
            text=BoxText(text="HBox 2", alignment=QtCore.Qt.AlignmentFlag.AlignRight, font=font_italic, style=PaintStyle())
        )
    ])
    diamond_path = QtGui.QPainterPath()
    diamond_path.moveTo(25, 0)
    diamond_path.lineTo(50, 20)
    diamond_path.lineTo(25, 40)
    diamond_path.lineTo(0, 20)
    diamond_path.closeSubpath()
    hbox_item3 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    hbox_item3.setObjectName("hbox_item3")
    hbox_item3.setSizeHint((60, 40))
    hbox_item3.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("gold")), shape_type=ShapeType.Path, painter_path=diamond_path),
            text=BoxText(text="Diamond", alignment=QtCore.Qt.AlignmentFlag.AlignCenter, font=font_large, style=PaintStyle())
        )
    ])
    standard_hbox.addLayout(hbox_item1)
    standard_hbox.addLayout(hbox_item2)
    standard_hbox.addLayout(hbox_item3)

    # Add all containers and layouts to the top box
    top_box.addLayout(nested_box1)
    top_box.addSpacing(10)
    top_box.addLayout(nested_box2)
    top_box.addSpacing(15)
    top_box.addLayout(standard_grid)
    top_box.addSpacing(15)
    top_box.addLayout(standard_hbox)

    # Add the top box to the widget
    box_widget.addBox(top_box)

    # Set up the main window
    window.setCentralWidget(box_widget)
    window.setWindowTitle("Painted Layouts Integration")
    window.setGeometry(100, 100, 500, 700)

    window.show()
    sys.exit(app.exec())


