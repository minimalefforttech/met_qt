from met_qt._internal.qtcompat import QtWidgets, QtCore
from met_qt.widgets.float_slider import FloatSlider
from met_qt.widgets.range_slider import RangeSlider
from met_qt.core.binding import Bindings
import sys

class SliderExamplesDemo(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Slider Examples")
        layout = QtWidgets.QVBoxLayout(self)

        # First float slider example - with soft range
        float_group1 = QtWidgets.QGroupBox("Float Slider with Soft Range")
        float_layout1 = QtWidgets.QHBoxLayout(float_group1)
        
        float_slider1 = FloatSlider()
        float_slider1.range = (0.0, 100.0)
        float_slider1.soft_range = (20.0, 80.0)
        float_layout1.addWidget(float_slider1)

        spin_value1 = QtWidgets.QDoubleSpinBox()
        spin_value1.setRange(0.0, 100.0)
        spin_value1.setDecimals(3)
        float_layout1.addWidget(QtWidgets.QLabel("Value:"))
        float_layout1.addWidget(spin_value1)

        bindings = Bindings(self)
        group = bindings.bind_group()
        group.add(float_slider1, "value")
        group.add(spin_value1, "value")
        float_slider1.value = 50

        # Second float slider example - basic
        float_group2 = QtWidgets.QGroupBox("Basic Float Slider")
        float_layout2 = QtWidgets.QHBoxLayout(float_group2)
        
        float_slider2 = FloatSlider()
        float_slider2.range = (-10.0, 10.0)
        float_layout2.addWidget(float_slider2)

        spin_value2 = QtWidgets.QDoubleSpinBox()
        spin_value2.setRange(-10.0, 10.0)
        spin_value2.setDecimals(2)
        float_layout2.addWidget(QtWidgets.QLabel("Value:"))
        float_layout2.addWidget(spin_value2)

        group = bindings.bind_group()
        group.add(float_slider2, "value")
        group.add(spin_value2, "value")
        float_slider2.value = 0

        # First range slider example - with soft range
        range_group1 = QtWidgets.QGroupBox("Range Slider with Soft Range")
        range_layout1 = QtWidgets.QHBoxLayout(range_group1)
        
        spin_min1 = QtWidgets.QDoubleSpinBox()
        spin_min1.setRange(0.0, 100.0)
        spin_min1.setDecimals(3)
        range_layout1.addWidget(QtWidgets.QLabel("Min:"))
        range_layout1.addWidget(spin_min1)

        range_slider1 = RangeSlider()
        range_slider1.range = (0.0, 100.0)
        range_slider1.soft_range = (20.0, 80.0)
        range_layout1.addWidget(range_slider1)

        spin_max1 = QtWidgets.QDoubleSpinBox()
        spin_max1.setRange(0.0, 100.0)
        spin_max1.setDecimals(3)
        range_layout1.addWidget(QtWidgets.QLabel("Max:"))
        range_layout1.addWidget(spin_max1)

        group = bindings.bind_group()
        group.add(range_slider1, "min_value")
        group.add(spin_min1, "value")
        group = bindings.bind_group()
        group.add(range_slider1, "max_value")
        group.add(spin_max1, "value")
        range_slider1.min_value = 30
        range_slider1.max_value = 70

        # Second range slider example - percentage
        range_group2 = QtWidgets.QGroupBox("Percentage Range Slider")
        range_layout2 = QtWidgets.QHBoxLayout(range_group2)
        
        spin_min2 = QtWidgets.QDoubleSpinBox()
        spin_min2.setRange(0.0, 100.0)
        spin_min2.setDecimals(1)
        spin_min2.setSuffix("%")
        range_layout2.addWidget(QtWidgets.QLabel("Min:"))
        range_layout2.addWidget(spin_min2)

        range_slider2 = RangeSlider()
        range_slider2.range = (0.0, 100.0)
        range_layout2.addWidget(range_slider2)

        spin_max2 = QtWidgets.QDoubleSpinBox()
        spin_max2.setRange(0.0, 100.0)
        spin_max2.setDecimals(1)
        spin_max2.setSuffix("%")
        range_layout2.addWidget(QtWidgets.QLabel("Max:"))
        range_layout2.addWidget(spin_max2)

        group = bindings.bind_group()
        group.add(range_slider2, "min_value")
        group.add(spin_min2, "value")
        group = bindings.bind_group()
        group.add(range_slider2, "max_value")
        group.add(spin_max2, "value")
        range_slider2.min_value = 25
        range_slider2.max_value = 75

        # Add all groups to main layout
        layout.addWidget(float_group1)
        layout.addWidget(float_group2)
        layout.addWidget(range_group1)
        layout.addWidget(range_group2)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    demo = SliderExamplesDemo()
    demo.show()
    sys.exit(app.exec_())
