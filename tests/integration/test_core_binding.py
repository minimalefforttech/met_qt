import pytest
from met_qt._internal.qtcompat import QtWidgets
from met_qt.core.binding import Bindings

@pytest.fixture
def bindings_widget(qtbot):
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(widget)
    spinbox = QtWidgets.QSpinBox()
    spinbox.setRange(0, 100)
    value_label = QtWidgets.QLabel("0")
    layout.addWidget(spinbox)
    layout.addWidget(value_label)
    edit1 = QtWidgets.QLineEdit()
    edit2 = QtWidgets.QLineEdit()
    layout.addWidget(edit1)
    layout.addWidget(edit2)
    first_name = QtWidgets.QLineEdit()
    last_name = QtWidgets.QLineEdit()
    full_name = QtWidgets.QLineEdit()
    full_name.setReadOnly(True)
    layout.addWidget(first_name)
    layout.addWidget(last_name)
    layout.addWidget(full_name)
    widget.show()
    qtbot.addWidget(widget)
    return {
        'widget': widget,
        'spinbox': spinbox,
        'value_label': value_label,
        'edit1': edit1,
        'edit2': edit2,
        'first_name': first_name,
        'last_name': last_name,
        'full_name': full_name,
        'bindings': Bindings(widget)
    }

def test_one_way_binding(qtbot, bindings_widget):
    spinbox = bindings_widget['spinbox']
    value_label = bindings_widget['value_label']
    bindings = bindings_widget['bindings']
    # Create a helper to track signal emissions
    signal_count = 0
    def on_value_changed(value):
        nonlocal signal_count
        signal_count += 1
        print(f"Value changed to: {value}")
    
    binding = bindings.bind(spinbox, "value")
    binding.to(value_label, "text", lambda x: str(x))
    spinbox.valueChanged.connect(on_value_changed)
    spinbox.setValue(42)
    # Update binding after value change
    binding.update_targets()
    qtbot.wait(100)  # Give time for signals to propagate
    print(f"Spinbox value: {spinbox.value()}")
    print(f"Label text: {value_label.text()}")
    assert value_label.text() == "42", "Label text was not updated"

def test_two_way_binding(qtbot, bindings_widget):
    edit1 = bindings_widget['edit1']
    edit2 = bindings_widget['edit2']
    bindings = bindings_widget['bindings']
    group = bindings.bind_group()
    group.add(edit1, "text")
    group.add(edit2, "text")
    edit1.setText("foo")
    qtbot.waitUntil(lambda: edit2.text() == "foo")
    edit2.setText("bar")
    qtbot.waitUntil(lambda: edit1.text() == "bar")

def test_expression_binding(qtbot, bindings_widget):
    first_name = bindings_widget['first_name']
    last_name = bindings_widget['last_name']
    full_name = bindings_widget['full_name']
    bindings = bindings_widget['bindings']
    with bindings.bind_expression(full_name, "text", "{first} {last}") as expr:
        expr.bind("first", first_name, "text")
        expr.bind("last", last_name, "text")
    first_name.setText("Ada")
    last_name.setText("Lovelace")
    qtbot.waitUntil(lambda: full_name.text() == "Ada Lovelace")

def test_math_expression_binding(qtbot, bindings_widget):
    # Add two QLineEdit widgets for numbers and a QLabel for the result
    widget = bindings_widget['widget']
    num1 = QtWidgets.QLineEdit()
    num2 = QtWidgets.QLineEdit()
    result = QtWidgets.QSlider()
    widget.layout().addWidget(num1)
    widget.layout().addWidget(num2)
    widget.layout().addWidget(result)
    bindings = bindings_widget['bindings']
    # Expression: sum of two floats
    with bindings.bind_expression(result, "value", "a+b") as expr:
        expr.bind("a", num1, "text")
        expr.bind("b", num2, "text")
    num1.setText("2")
    num2.setText("3")
    qtbot.waitUntil(lambda: result.value() == 5, timeout=20)
    num1.setText("10")
    num2.setText("5")
    qtbot.waitUntil(lambda: result.value() == 15, timeout=20)
