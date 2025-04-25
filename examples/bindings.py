import sys
from met_qt.core.binding import Bindings
from PySide6 import QtWidgets

class BindingExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(BindingExample, self).__init__(parent)
        self.setWindowTitle("Bindings Example")
        self.resize(400, 300)
        
        # Create widgets
        layout = QtWidgets.QVBoxLayout(self)
        
        # One-way binding example
        group1 = QtWidgets.QGroupBox("One-way Binding")
        layout1 = QtWidgets.QHBoxLayout(group1)
        spinbox = QtWidgets.QSpinBox()
        spinbox.setRange(0, 100)
        value_label = QtWidgets.QLabel("0")
        layout1.addWidget(QtWidgets.QLabel("Spin Box:"))
        layout1.addWidget(spinbox)
        layout1.addWidget(QtWidgets.QLabel("Label:"))
        layout1.addWidget(value_label)
        layout.addWidget(group1)
        
        # Two-way binding example
        group2 = QtWidgets.QGroupBox("Two-way Binding")
        layout2 = QtWidgets.QHBoxLayout(group2)
        edit1 = QtWidgets.QLineEdit()
        edit2 = QtWidgets.QLineEdit()
        layout2.addWidget(QtWidgets.QLabel("Edit 1:"))
        layout2.addWidget(edit1)
        layout2.addWidget(QtWidgets.QLabel("Edit 2:"))
        layout2.addWidget(edit2)
        layout.addWidget(group2)
        
        # Expression binding example
        group3 = QtWidgets.QGroupBox("Expression Binding")
        layout3 = QtWidgets.QHBoxLayout(group3)
        first_name = QtWidgets.QLineEdit()
        last_name = QtWidgets.QLineEdit()
        full_name = QtWidgets.QLineEdit()
        full_name.setReadOnly(True)
        layout3.addWidget(QtWidgets.QLabel("First:"))
        layout3.addWidget(first_name)
        layout3.addWidget(QtWidgets.QLabel("Last:"))
        layout3.addWidget(last_name)
        layout3.addWidget(QtWidgets.QLabel("Full:"))
        layout3.addWidget(full_name)
        layout.addWidget(group3)
        
        # Setup bindings
        bindings = Bindings(self)
        
        # One-way binding: spinbox -> label
        bindings.bind(spinbox, "value").to(value_label, "text", lambda x: f"Value: {int(x)}")
        
        # Two-way binding between line edits
        group = bindings.bind_group()
        group.add(edit1, "text")
        group.add(edit2, "text")
        
        # Expression binding: combine first and last names
        with bindings.bind_expression(
                full_name, "text",
                "{first} {last}") as expr:
            expr.bind("first", first_name, "text")
            expr.bind("last", last_name, "text")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = BindingExample()
    widget.show()
    sys.exit(app.exec())
