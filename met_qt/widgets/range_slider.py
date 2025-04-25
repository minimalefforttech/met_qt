# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
from met_qt._internal.qtcompat import QtWidgets, QtCore, QtGui
from typing import Optional
from met_qt._internal.widgets.abstract_slider import AbstractSoftSlider as _AbstractSoftSlider

class RangeSlider(_AbstractSoftSlider):
    """
    A slider widget supporting floating-point range selection with two handles (min/max)
    Dragging a handle past the other switches which handle is being dragged.
    """
    min_value_changed = QtCore.Signal(float)
    max_value_changed = QtCore.Signal(float)
    slider_moved = QtCore.Signal(float, float)
    slider_pressed = QtCore.Signal()
    slider_released = QtCore.Signal()

    def __init__(self, orientation: QtCore.Qt.Orientation = QtCore.Qt.Horizontal, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(orientation, parent)
        self._min_value: float = self._range[0]
        self._max_value: float = self._range[1]
        self._active_handle: Optional[str] = None  # 'min' or 'max'
        self._slider_down: bool = False
        self.range_changed.connect(self._on_range_changed)

    def _on_range_changed(self, min_: float, max_: float):
        self._min_value = min_
        self._max_value = max_
        self.min_value_changed.emit(self._min_value)
        self.max_value_changed.emit(self._max_value)
        self.slider_moved.emit(self._min_value, self._max_value)
        self.update()

    @QtCore.Property(float, notify=min_value_changed)
    def min_value(self) -> float:
        return self._min_value

    @min_value.setter
    def min_value(self, value: float):
        value = float(value)
        value = min(max(value, self._range[0]), self._range[1])
        if self.single_step > 0:
            value = round(value / self.single_step) * self.single_step
        # Handle swapping if past max
        if value > self._max_value:
            old_min = self._min_value
            self._min_value, self._max_value = self._max_value, value
            self._active_handle = 'max' if self._active_handle == 'min' else 'min'
            self.max_value_changed.emit(self._max_value)
        else:
            old_min = self._min_value
            self._min_value = value
        if old_min != self._min_value:
            self.min_value_changed.emit(self._min_value)
            self.slider_moved.emit(self._min_value, self._max_value)
            self.update()

    @QtCore.Property(float, notify=max_value_changed)
    def max_value(self) -> float:
        return self._max_value

    @max_value.setter
    def max_value(self, value: float):
        value = float(value)
        value = min(max(value, self._range[0]), self._range[1])
        if self.single_step > 0:
            value = round(value / self.single_step) * self.single_step
        # Handle swapping if before min
        if value < self._min_value:
            old_max = self._max_value
            self._min_value, self._max_value = value, self._min_value
            self._active_handle = 'min' if self._active_handle == 'max' else 'max'
            self.min_value_changed.emit(self._min_value)
        else:
            old_max = self._max_value
            self._max_value = value
        if old_max != self._max_value:
            self.max_value_changed.emit(self._max_value)
            self.slider_moved.emit(self._min_value, self._max_value)
            self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        visual_range = self._visual_range()
        mult = 10 ** self._decimals
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        groove_rect = self._groove_rect()
        min_center = self._value_to_pos(self._min_value, groove_rect)
        max_center = self._value_to_pos(self._max_value, groove_rect)

        groove_color = self.palette().color(QtGui.QPalette.Button)
        groove_color2 = groove_color.lighter(120)
        groove_gradient = QtGui.QLinearGradient(
            groove_rect.center().x(), groove_rect.top(),
            groove_rect.center().x(), groove_rect.bottom()
        )
        groove_gradient.setColorAt(0, groove_color)
        groove_gradient.setColorAt(1, groove_color2)
        painter.save()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(groove_gradient)
        painter.drawRoundedRect(groove_rect, 3, 3)
        painter.restore()

        if self.isEnabled():
            highlight_color = self.palette().color(QtGui.QPalette.Highlight)
        else:
            highlight_color = self.palette().color(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight)
        painter.save()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(highlight_color))
        if self._orientation == QtCore.Qt.Horizontal:
            y = groove_rect.top()
            h = groove_rect.height()
            left = min(min_center, max_center)
            right = max(min_center, max_center)
            highlight_rect = QtCore.QRect(left, y, right - left, h)
        else:
            x = groove_rect.left()
            w = groove_rect.width()
            top = min(min_center, max_center)
            bottom = max(min_center, max_center)
            highlight_rect = QtCore.QRect(x, top, w, bottom - top)
        painter.drawRoundedRect(highlight_rect, 3, 3)
        painter.restore()

        style = self.style()
        opt = QtWidgets.QStyleOptionSlider()
        opt.initFrom(self)
        opt.orientation = self._orientation
        opt.minimum = int(visual_range[0] * mult)
        opt.maximum = int(visual_range[1] * mult)
        opt.subControls = QtWidgets.QStyle.SC_SliderHandle

        opt.sliderPosition = int(self._min_value * mult)
        opt.sliderValue = int(self._min_value * mult)
        opt.state = QtWidgets.QStyle.State_Enabled if self.isEnabled() else QtWidgets.QStyle.State_None
        if self._active_handle == 'min' and self._slider_down:
            opt.state |= QtWidgets.QStyle.State_Sunken
        style.drawComplexControl(QtWidgets.QStyle.CC_Slider, opt, painter, self)

        opt.sliderPosition = int(self._max_value * mult)
        opt.sliderValue = int(self._max_value * mult)
        opt.state = QtWidgets.QStyle.State_Enabled if self.isEnabled() else QtWidgets.QStyle.State_None
        if self._active_handle == 'max' and self._slider_down:
            opt.state |= QtWidgets.QStyle.State_Sunken
        style.drawComplexControl(QtWidgets.QStyle.CC_Slider, opt, painter, self)

    def _pick_handle(self, pos):
        # Decide which handle is closer to the mouse position
        groove_rect = self._groove_rect()
        if self._orientation == QtCore.Qt.Horizontal:
            min_pos = self._value_to_pos(self._min_value, groove_rect)
            max_pos = self._value_to_pos(self._max_value, groove_rect)
            if abs(pos.x() - min_pos) < abs(pos.x() - max_pos):
                return 'min'
            else:
                return 'max'
        else:
            min_pos = self._value_to_pos(self._min_value, groove_rect)
            max_pos = self._value_to_pos(self._max_value, groove_rect)
            if abs(pos.y() - min_pos) < abs(pos.y() - max_pos):
                return 'min'
            else:
                return 'max'

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            groove_rect = self._groove_rect()
            pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
            self._active_handle = self._pick_handle(pos)
            self._slider_down = True
            val = self._pos_to_value(pos.x() if self._orientation == QtCore.Qt.Horizontal else pos.y(), groove_rect)
            if self._active_handle == 'min':
                self.min_value = val
            else:
                self.max_value = val
            self.slider_moved.emit(self._min_value, self._max_value)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._slider_down and self._active_handle:
            groove_rect = self._groove_rect()
            pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
            val = self._pos_to_value(pos.x() if self._orientation == QtCore.Qt.Horizontal else pos.y(), groove_rect)
            if self._active_handle == 'min':
                self.min_value = val
            else:
                self.max_value = val
            self.slider_moved.emit(self._min_value, self._max_value)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if self._slider_down and event.button() == QtCore.Qt.LeftButton:
            self._slider_down = False
            self._active_handle = None
            self.slider_released.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        if self._active_handle == 'min':
            val = self._min_value
        else:
            val = self._max_value
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
        if self._active_handle == 'min':
            self.min_value = val
        else:
            self.max_value = val
        self.slider_moved.emit(self._min_value, self._max_value)
        event.accept()
