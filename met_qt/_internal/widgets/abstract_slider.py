# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
from met_qt._internal.qtcompat import QtWidgets, QtCore, QtGui
from typing import Optional
from met_qt.core.meta import QProperty
import sys


class AbstractSoftSlider(QtWidgets.QWidget):
    """
    Base class for custom sliders with a soft range
    """
    range_changed = QtCore.Signal(float, float)
    soft_range_changed = QtCore.Signal(float, float)

    orientation, orientation_changed = QProperty("orientation", QtCore.Qt.Orientation, default=QtCore.Qt.Horizontal, signal=True)
    tracking, tracking_changed = QProperty("tracking", bool, default=True, signal=True)
    single_step = QProperty("single_step", float, default=0.01)
    page_step = QProperty("page_step", float, default=0.1)

    def __init__(self, orientation: QtCore.Qt.Orientation = QtCore.Qt.Horizontal, parent: Optional[QtWidgets.QWidget] = None):
        """Initialize the FloatSlider widget."""
        super().__init__(parent)
        # Store ranges as tuples
        self._range: tuple[float, float] = (0.0, 1.0)
        self._soft_range: Optional[tuple[float, float]] = None
        self.orientation = orientation
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMinimumSize(40, 20)
        self._decimals = 4  # Number of decimal places for float values


    @QtCore.Property('QVariant', notify=range_changed)
    def range(self) -> tuple[float, float]:
        """Return the hard (min, max) range as a tuple."""
        return self._range
    
    @range.setter
    def range(self, rng: tuple[Optional[float], Optional[float]]):
        # Replace None with float limits
        min_ = float(rng[0]) if rng[0] is not None else -sys.float_info.max
        max_ = float(rng[1]) if rng[1] is not None else sys.float_info.max
        
        if min_ > max_:
            min_, max_ = max_, min_
        old_range = self._range
        self._range = (min_, max_)
        # Clamp soft range
        if self._soft_range is not None:
            smin, smax = self._soft_range
            smin = max(min_, min(smin, max_))
            smax = min(max_, max(smax, min_))
            if smin > smax:
                smin, smax = smax, smin
            self._soft_range = (smin, smax)
        if old_range != self._range:
            self.range_changed.emit(*self._range)
            self.update()

    @QtCore.Property('QVariant', notify=soft_range_changed)
    def soft_range(self) -> Optional[tuple[float, float]]:
        """Return the soft (min, max) range as a tuple, or None if unset."""
        return self._soft_range

    @soft_range.setter
    def soft_range(self, rng: Optional[tuple[float, float]]):
        if rng is None:
            self._soft_range = None
            self.soft_range_changed.emit(*self._range)
            self.update()
            return
        min_, max_ = float(rng[0]), float(rng[1])
        rmin, rmax = self._range
        min_ = max(rmin, min_)
        max_ = min(rmax, max_)
        if min_ > max_:
            min_, max_ = max_, min_
        old_soft = self._soft_range
        self._soft_range = (min_, max_)
        if old_soft != self._soft_range:
            self.soft_range_changed.emit(*self._soft_range)
            self.update()

    def _bound(self, value: float) -> float:
        """Clamp value to the hard range."""
        value = min(max(value, self._range[0]), self._range[1])
        # round to step size
        if self.single_step > 0:
            value = round(value / self.single_step) * self.single_step
        return value

    def sizeHint(self) -> QtCore.QSize:
        """Return the recommended size for the widget."""
        if self._orientation == QtCore.Qt.Horizontal:
            return QtCore.QSize(160, 24)
        else:
            return QtCore.QSize(24, 160)

    def minimumSizeHint(self) -> QtCore.QSize:
        """Return the minimum recommended size for the widget."""
        return self.sizeHint()

    def _visual_range(self) -> tuple[float, float]:
        soft_min = self._soft_range[0] if self._soft_range is not None else self._range[0]
        soft_max = self._soft_range[1] if self._soft_range is not None else self._range[1]
        return (
            max(self._range[0], soft_min),
            min(self._range[1], soft_max)
        )

    def _value_to_pos(self, value: float, groove_rect: QtCore.QRect) -> int:
        """Map a value in [min, max] to a pixel position along the groove."""
        vmin, vmax = self._visual_range()
        if self._orientation == QtCore.Qt.Horizontal:
            x0, x1 = groove_rect.left(), groove_rect.right()
            return int(x0 + (x1 - x0) * (value - vmin) / (vmax - vmin) if vmax > vmin else x0)
        else:
            y0, y1 = groove_rect.bottom(), groove_rect.top()
            return int(y0 + (y1 - y0) * (value - vmin) / (vmax - vmin) if vmax > vmin else y0)

    def _pos_to_value(self, pos: int, groove_rect: QtCore.QRect) -> float:
        """Map a pixel position along the groove to a value in [min, max]."""
        vmin, vmax = self._visual_range()
        pos = float(pos)
        if self._orientation == QtCore.Qt.Horizontal:
            x0, x1 = float(groove_rect.left()), float(groove_rect.right())
            if x1 == x0:
                return vmin
            ratio = (pos - x0) / (x1 - x0)
        else:
            y0, y1 = float(groove_rect.bottom()), float(groove_rect.top())
            if y1 == y0:
                return vmin
            ratio = (pos - y0) / (y1 - y0)
        return vmin + (vmax - vmin) * ratio

    def _groove_rect(self) -> QtCore.QRect:
        rect = self.rect()
        groove_thickness = 6
        handle_radius = 8
        if self._orientation == QtCore.Qt.Horizontal:
            return QtCore.QRect(
                rect.left() + handle_radius, rect.center().y() - groove_thickness // 2,
                rect.width() - 2 * handle_radius, groove_thickness)
        else:
            return QtCore.QRect(
                rect.center().x() - groove_thickness // 2, rect.top() + handle_radius,
                groove_thickness, rect.height() - 2 * handle_radius)