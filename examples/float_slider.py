from met_qt._internal.qtcompat import QtWidgets, QtCore
from met_qt.widgets.float_slider import FloatSlider
from met_qt.core.binding import Bindings
import sys

class FloatSliderBindingDemo(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FloatSlider Soft Range Binding Demo")
        layout = QtWidgets.QHBoxLayout(self)

        slider = FloatSlider()
        slider.range = (0.0, 100.0)
        # A soft range allows the slider to be within 20-80 but if value is set
        # outside of that range, it will grow up to the range.
        slider.soft_range = (20.0, 80.0)
        layout.addWidget(slider)

        # Double spin boxes for value, soft min, soft max
        spin_value = QtWidgets.QDoubleSpinBox()
        spin_value.setRange(0.0, 100.0)
        spin_value.setDecimals(3)
        layout.addWidget(QtWidgets.QLabel("Value:"))
        layout.addWidget(spin_value)

        # Bindings
        bindings = Bindings(self)
        group = bindings.bind_group()
        group.add(slider, "value")
        group.add(spin_value, "value")
        slider.value = 50

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    demo = FloatSliderBindingDemo()
    demo.show()
    sys.exit(app.exec_())
