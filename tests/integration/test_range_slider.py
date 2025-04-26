import pytest
from met_qt.widgets.range_slider import RangeSlider
from met_qt._internal.qtcompat import QtWidgets

@pytest.fixture
def app(qtbot):
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

def test_range_slider_basic(app, qtbot):
    slider = RangeSlider()
    slider.range = (0.0, 10.0)
    slider.soft_range = (2.0, 8.0)
    slider.min_value = 3.0
    slider.max_value = 7.0
    assert slider.min_value == 3.0
    assert slider.max_value == 7.0
    slider.min_value = 11.0  # Should swap and clamp
    assert slider.min_value == 7.0
    assert slider.max_value == 10.0
    slider.max_value = -2.0  # Should swap and clamp
    assert slider.max_value == 7.0
    assert slider.min_value == 0.0
