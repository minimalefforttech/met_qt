# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
from met_qt._internal.qtcompat import QtWidgets, QtCore, QtGui
from typing import Optional
from met_qt._internal.widgets.abstract_slider import AbstractSoftSlider as _AbstractSoftSlider
from met_qt.core.meta import QProperty
import sys


class FloatSlider(_AbstractSoftSlider):
    """
    A slider widget supporting floating-point values, with hard (min/max), soft, and interactive ranges.
    - Hard range: absolute min/max (cannot be exceeded)
    - Soft range: user-adjustable subrange within hard range
    - Interactive range: intersection of soft and hard range (not stored)
    """
    value_changed = QtCore.Signal(float)
    slider_moved = QtCore.Signal(float)
    slider_pressed = QtCore.Signal()
    slider_released = QtCore.Signal()

    def __init__(self, orientation: QtCore.Qt.Orientation = QtCore.Qt.Horizontal, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(orientation, parent)
        self._value: float = 0.0
        self._slider_down: bool = False
        self.range_changed.connect(self._on_range_changed)

    def _on_range_changed(self, min_, max_):
        # Clamp value to new range
        clamped = self._bound(self._value)
        if clamped != self._value:
            self.value = clamped

    @QtCore.Property(float, notify=value_changed)
    def value(self) -> float:
        """Return the current value."""
        return self._value

    @value.setter
    def value(self, value: float):
        value = self._bound(float(value))
        changed = False
        if self._soft_range is not None and value < self._soft_range[0]:
            self._soft_range = (value, self._soft_range[1])
            changed = True
        if self._soft_range is not None and value > self._soft_range[1]:
            self._soft_range = (self._soft_range[0], value)
            changed = True
        if changed:
            self.soft_range_changed.emit(self._soft_range[0] if self._soft_range is not None else self._range[0],
                                        self._soft_range[1] if self._soft_range is not None else self._range[1])
        if self._value != value:
            self._value = value
            self.value_changed.emit(self._value)
            self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        """
        Paint the slider using QStylePainter and QStyleOptionSlider for native look and feel.
        """
        visual_range = self._visual_range()
        
        opt = QtWidgets.QStyleOptionSlider()
        opt.initFrom(self)
        opt.orientation = self._orientation
        # Allow for 4dp accuracy
        mult = 10**self._decimals
        opt.minimum = int(visual_range[0]*mult)
        opt.maximum = int(visual_range[1]*mult)
        opt.sliderPosition = int(self._value*mult)
        opt.sliderValue = int(self._value*mult)
        opt.singleStep = int(self.single_step*mult)
        opt.pageStep = int(self.page_step*mult)
        opt.upsideDown = False
        opt.state |= QtWidgets.QStyle.State_HasFocus if self.hasFocus() else QtWidgets.QStyle.State_None
        if self._slider_down:
            opt.state |= QtWidgets.QStyle.State_Sunken
        else:
            opt.state &= ~QtWidgets.QStyle.State_Sunken

        painter = QtWidgets.QStylePainter(self)
        painter.drawComplexControl(QtWidgets.QStyle.CC_Slider, opt)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            groove_rect = self._groove_rect()
            pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
            if self._orientation == QtCore.Qt.Horizontal:
                if pos.x() < groove_rect.left():
                    pos = QtCore.QPoint(groove_rect.left(), pos.y())
                elif pos.x() > groove_rect.right():
                    pos = QtCore.QPoint(groove_rect.right(), pos.y())
            else:
                if pos.y() < groove_rect.top():
                    pos = QtCore.QPoint(pos.x(), groove_rect.top())
                elif pos.y() > groove_rect.bottom():
                    pos = QtCore.QPoint(pos.x(), groove_rect.bottom())
            val = self._pos_to_value(
                pos.x() if self._orientation == QtCore.Qt.Horizontal else pos.y(),
                groove_rect)
            self._slider_down = True
            self.value = val
            self.slider_moved.emit(self._value)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._slider_down:
            groove_rect = self._groove_rect()
            pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
            if self._orientation == QtCore.Qt.Horizontal:
                if pos.x() < groove_rect.left():
                    pos = QtCore.QPoint(groove_rect.left(), pos.y())
                elif pos.x() > groove_rect.right():
                    pos = QtCore.QPoint(groove_rect.right(), pos.y())
            else:
                if pos.y() < groove_rect.top():
                    pos = QtCore.QPoint(pos.x(), groove_rect.top())
                elif pos.y() > groove_rect.bottom():
                    pos = QtCore.QPoint(pos.x(), groove_rect.bottom())
            val = self._pos_to_value(
                pos.x() if self._orientation == QtCore.Qt.Horizontal else pos.y(),
                groove_rect)
            self.value = val
            self.slider_moved.emit(self._value)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if self._slider_down and event.button() == QtCore.Qt.LeftButton:
            self._slider_down = False
            self.slider_released.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        val = self._value
        if key in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Down):
            val -= self.single_step
        elif key in (QtCore.Qt.Key_Right, QtCore.Qt.Key_Up):
            val += self.single_step
        elif key == QtCore.Qt.Key_PageUp:
            val += self.page_step
        elif key == QtCore.Qt.Key_PageDown:
            val -= self.page_step
        elif key == QtCore.Qt.Key_Home:
            val = self._visual_range()[0]
        elif key == QtCore.Qt.Key_End:
            val = self._visual_range()[1]
        else:
            super().keyPressEvent(event)
            return
        self.value = val
        self.slider_moved.emit(self._value)
        event.accept()
