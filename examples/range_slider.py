from met_qt._internal.qtcompat import QtWidgets, QtCore, QtGui
from met_qt.widgets.range_slider import RangeSlider
from met_qt.core.binding import Bindings
import sys

class RangeSliderBindingDemo(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RangeSlider Soft Range Binding Demo")
        layout = QtWidgets.QHBoxLayout(self)

        slider = RangeSlider()
        slider.range = (0.0, 100.0)
        slider.soft_range = (20.0, 80.0)
        layout.addWidget(slider)

        # Double spin boxes for min, max
        spin_min = QtWidgets.QDoubleSpinBox()
        spin_min.setRange(0.0, 100.0)
        spin_min.setDecimals(3)
        spin_min.setValue(0.0)
        layout.addWidget(QtWidgets.QLabel("Min:"))
        layout.addWidget(spin_min)

        spin_max = QtWidgets.QDoubleSpinBox()
        spin_max.setRange(0.0, 100.0)
        spin_max.setDecimals(3)
        spin_max.setValue(100.0)
        layout.addWidget(QtWidgets.QLabel("Max:"))
        layout.addWidget(spin_max)

        # Bindings
        bindings = Bindings(self)
        group = bindings.bind_group()
        group.add(slider, "min_value")
        group.add(spin_min, "value")
        group = bindings.bind_group()
        group.add(slider, "max_value")
        group.add(spin_max, "value")
        slider.min_value = 30
        slider.max_value = 70

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    demo = RangeSliderBindingDemo()
    demo.show()
    sys.exit(app.exec_())
