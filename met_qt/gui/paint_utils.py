# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
"""
This file contains general utilities for painting, predominantly around anchors.
The concept is that these methods can be used to draw and return the rect which was used.
anchor() can be used to snap components together
"""
from typing import Union, Optional
from met_qt._internal.qtcompat import QtWidgets, QtCore, QtGui


def to_global(painter: QtGui.QPainter, point_or_rect: Union[QtCore.QRect, QtCore.QPoint]) -> Union[QtCore.QRect, QtCore.QPoint]:
    """
    Map a QRect or QPoint from widget coordinates to global (transformed) coordinates using the painter's transform.
    Args:
        painter: QPainter instance.
        point_or_rect: QRect or QPoint to map.
    Returns:
        QRect or QPoint in global coordinates.
    """
    t = painter.transform()
    if isinstance(point_or_rect, (QtCore.QRect, QtCore.QRectF)):
        return t.mapRect(point_or_rect)
    elif isinstance(point_or_rect, (QtCore.QPoint, QtCore.QPointF)):
        return t.map(point_or_rect)
    else:
        raise ValueError("to_global expects a QRect or QPoint")

def from_global(painter: QtGui.QPainter, point_or_rect: Union[QtCore.QRect, QtCore.QPoint]) -> Union[QtCore.QRect, QtCore.QPoint]:
    """
    Map a QRect or QPoint from global (transformed) coordinates to widget coordinates using the painter's transform.
    Args:
        painter: QPainter instance.
        point_or_rect: QRect or QPoint to map.
    Returns:
        QRect or QPoint in widget coordinates.
    """
    inv, invertible = painter.transform().inverted()
    if not invertible:
        raise ValueError("Painter transform is not invertible")
    if isinstance(point_or_rect, QtCore.QRect):
        return inv.mapRect(point_or_rect)
    elif isinstance(point_or_rect, QtCore.QPoint):
        return inv.map(point_or_rect)
    else:
        raise ValueError("from_global expects a QRect or QPoint")

def draw_text(painter: QtGui.QPainter, *args, **kwargs) -> QtCore.QRect:
    """
    Draw text using the painter and return the bounding rect of the text as drawn.
    Accepts either a QRect and flags/text, or x/y/text, matching QPainter.drawText signatures.
    Returns:
        QRect: The bounding rect of the text as drawn.
    """
    if len(args) > 0 and isinstance(args[0], QtCore.QRect):
        rect = args[0]
        text = args[2] if len(args) > 2 else kwargs.get('text', '')
        flags = args[1] if len(args) > 1 else kwargs.get('flags', 0)
        font_metrics = painter.fontMetrics()
        used_rect = font_metrics.boundingRect(rect, flags, text)
    elif len(args) >= 2 and all(isinstance(a, int) for a in args[:2]):
        font_metrics = painter.fontMetrics()
        text = args[2] if len(args) > 2 else ''
        used_rect = font_metrics.boundingRect(args[0], args[1], 10000, 10000, 0, text)
        rect = used_rect
    else:
        rect = QtCore.QRect(0, 0, 0, 0)
        used_rect = rect
    painter.drawText(*args, **kwargs)
    return used_rect

def draw_partially_rounded_rect(
    painter: QtGui.QPainter,
    rect: QtCore.QRect,
    top_left: int,
    top_right: int,
    bottom_right: int,
    bottom_left: int
) -> QtCore.QRect:
    """
    Draw a rectangle with selectively rounded corners using the painter and return the rect used.
    Args:
        painter: QPainter instance.
        rect: QRect to draw.
        top_left, top_right, bottom_right, bottom_left: Radii for each corner.
    Returns:
        QRect: The rect drawn.
    """
    path = QtGui.QPainterPath()
    r = rect
    path.moveTo(r.left() + top_left, r.top())
    path.lineTo(r.right() - top_right, r.top())
    if top_right:
        path.quadTo(r.right(), r.top(), r.right(), r.top() + top_right)
    path.lineTo(r.right(), r.bottom() - bottom_right)
    if bottom_right:
        path.quadTo(r.right(), r.bottom(), r.right() - bottom_right, r.bottom())
    path.lineTo(r.left() + bottom_left, r.bottom())
    if bottom_left:
        path.quadTo(r.left(), r.bottom(), r.left(), r.bottom() - bottom_left)
    path.lineTo(r.left(), r.top() + top_left)
    if top_left:
        path.quadTo(r.left(), r.top(), r.left() + top_left, r.top())
    painter.drawPath(path)
    return rect

def draw_path(painter: QtGui.QPainter, path: QtGui.QPainterPath) -> QtCore.QRect:
    """
    Draw a QPainterPath using the painter and return its bounding rect.
    Args:
        painter: QPainter instance.
        path: QPainterPath to draw.
    Returns:
        QRect: The bounding rect of the path.
    """
    painter.drawPath(path)
    rect = path.boundingRect().toRect()
    return rect

def draw_item_text(
    painter: QtGui.QPainter,
    rect: QtCore.QRect,
    flags: int,
    palette: QtGui.QPalette,
    enabled: bool,
    text: str,
    textRole: int = QtGui.QPalette.WindowText,
    font: Optional[QtGui.QFont] = None,
    style: Optional[QtWidgets.QStyle] = None
) -> QtCore.QRect:
    """
    Draw item text using the style and painter, and return the actual text rect as computed by the style.
    Args:
        painter: QPainter instance.
        rect: QRect to draw in.
        flags: Alignment flags.
        palette: QPalette for text.
        enabled: Whether the item is enabled.
        text: The text to draw.
        textRole: QPalette role for the text.
        font: Optional QFont.
        style: Optional QStyle.
    Returns:
        QRect: The actual text rect as computed by the style.
    """
    style = style or QtWidgets.QApplication.style()
    option = QtWidgets.QStyleOptionViewItem()
    option.rect = rect
    option.displayAlignment = flags
    option.palette = palette
    option.state = QtWidgets.QStyle.State_Enabled if enabled else QtWidgets.QStyle.State_None
    option.text = text
    if font is not None:
        option.font = font
    text_rect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, option)
    style.drawItemText(painter, rect, flags, palette, enabled, text, textRole)
    return text_rect

def draw_primitive(
    painter: QtGui.QPainter,
    element: int,
    option: QtWidgets.QStyleOption,
    widget: Optional[QtWidgets.QWidget] = None,
    style: Optional[QtWidgets.QStyle] = None
) -> QtCore.QRect:
    """
    Draw a primitive element using the style and painter, and return the option's rect.
    Args:
        painter: QPainter instance.
        element: QStyle.PrimitiveElement.
        option: QStyleOption.
        widget: Optional QWidget.
        style: Optional QStyle.
    Returns:
        QRect: The rect from the option.
    """
    style = style or QtWidgets.QApplication.style()
    style.drawPrimitive(element, option, painter, widget)
    rect = option.rect
    return rect

def draw_control(
    painter: QtGui.QPainter,
    element: int,
    option: QtWidgets.QStyleOption,
    widget: Optional[QtWidgets.QWidget] = None,
    style: Optional[QtWidgets.QStyle] = None
) -> QtCore.QRect:
    """
    Draw a control element using the style and painter, and return the option's rect.
    Args:
        painter: QPainter instance.
        element: QStyle.ControlElement.
        option: QStyleOption.
        widget: Optional QWidget.
        style: Optional QStyle.
    Returns:
        QRect: The rect from the option.
    """
    style = style or QtWidgets.QApplication.style()
    style.drawControl(element, option, painter, widget)
    rect = option.rect
    return rect

def draw_complex_control(
    painter: QtGui.QPainter,
    element: int,
    option: QtWidgets.QStyleOptionComplex,
    widget: Optional[QtWidgets.QWidget] = None,
    style: Optional[QtWidgets.QStyle] = None,
    subcontrol: Optional[int] = None
) -> QtCore.QRect:
    """
    Draw a complex control element using the style and painter, and return the subcontrol rect if specified, otherwise the option's rect.
    Args:
        painter: QPainter instance.
        element: QStyle.ComplexControl.
        option: QStyleOptionComplex.
        widget: Optional QWidget.
        style: Optional QStyle.
        subcontrol: Optional QStyle.SubControl to get the rect for.
    Returns:
        QRect: The subcontrol rect if specified, else the rect from the option.
    """
    style = style or QtWidgets.QApplication.style()
    style.drawComplexControl(element, option, painter, widget)
    if subcontrol is not None:
        return style.subControlRect(element, option, subcontrol, widget)
    rect = option.rect
    return rect

def anchor(
    rect: Union[QtCore.QRect, QtCore.QSize, tuple],
    left: Optional[int] = None,
    right: Optional[int] = None,
    top: Optional[int] = None,
    bottom: Optional[int] = None,
    vcenter: Optional[int] = None,
    hcenter: Optional[int] = None
) -> QtCore.QRect:
    """
    Anchor and optionally stretch a rect based on left, right, top, bottom, vcenter, hcenter.
    Args:
        rect: QRect, QSize, or (w, h) tuple. If size/tuple, origin is (0,0).
        left, right, top, bottom: Optional anchor positions.
        vcenter: Optional vertical center position.
        hcenter: Optional horizontal center position.
    Returns:
        QRect: The anchored and/or stretched rect.
    """
    if isinstance(rect, QtCore.QRect):
        r = QtCore.QRect(rect)
    elif isinstance(rect, QtCore.QSize):
        r = QtCore.QRect(0, 0, rect.width(), rect.height())
    elif isinstance(rect, tuple) and len(rect) == 2:
        r = QtCore.QRect(0, 0, rect[0], rect[1])
    else:
        raise ValueError("rect must be QRect, QSize, or (w, h) tuple")
    if left is not None:
        r.moveLeft(left)
    if right is not None:
        if left is not None:
            r.setWidth(right - left)
        else:
            r.moveRight(right)
    if top is not None:
        r.moveTop(top)
    if bottom is not None:
        if top is not None:
            r.setHeight(bottom - top)
        else:
            r.moveBottom(bottom)
    if vcenter is not None:
        r.moveCenter(QtCore.QPoint(r.center().x(), vcenter))
    if hcenter is not None:
        r.moveCenter(QtCore.QPoint(hcenter, r.center().y()))
    return r