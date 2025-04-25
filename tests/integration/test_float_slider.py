import pytest
from met_qt.widgets.float_slider import FloatSlider
from met_qt._internal.qtcompat import QtWidgets, QtCore

@pytest.fixture
def app(qtbot):
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

def test_float_slider_basic(app, qtbot):
    slider = FloatSlider()
    slider.range = (0.0, 1.0)
    slider.single_step = 0.25
    
    # Test step size clamping
    slider.value = 0.3  # Should clamp to 0.25
    assert slider.value == 0.25
    slider.value = 0.7  # Should clamp to 0.75
    assert slider.value == 0.75
    
    # Test min/max clamping
    slider.value = -0.5  # Should clamp to min
    assert slider.value == 0.0
    slider.value = 1.5  # Should clamp to max
    assert slider.value == 1.0

def test_float_slider_click(app, qtbot):
    slider = FloatSlider()
    slider.range = (0.0, 1.0)
    slider.single_step = 0.25
    
    # Show widget and click in center
    slider.show()
    qtbot.addWidget(slider)
    
    # Get center position
    center = slider.rect().center()
    qtbot.mouseClick(slider, QtCore.Qt.LeftButton, pos=center)
    
    # Value should be approximately 0.5 (may have small float precision differences)
    assert abs(slider.value - 0.5) < 0.001
