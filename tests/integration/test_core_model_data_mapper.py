import pytest
from met_qt._internal.qtcompat import QtCore, QtGui, QtWidgets
from met_qt.core.model_data_mapper import ModelDataMapper

class DummyWidget(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(int)
    def __init__(self):
        super().__init__()
        self._value = 0
    def setValue(self, v):
        self._value = v
        self.valueChanged.emit(v)
    def value(self):
        return self._value

def create_simple_model():
    model = QtGui.QStandardItemModel()
    item = QtGui.QStandardItem("Test")
    item.setData({"quantity": 42, "format": "usd"}, QtCore.Qt.UserRole)
    model.appendRow(item)
    return model

def test_model_data_mapper_basic(qtbot):
    model = create_simple_model()
    widget = DummyWidget()
    mapper = ModelDataMapper()
    mapper.set_model(model)
    mapper.add_mapping(
        widget, "value", role=QtCore.Qt.UserRole,
        from_model=lambda d: d.get("quantity", 0),
        from_property=lambda v, d: {**d, "quantity": v},
        signal=widget.valueChanged
    )
    mapper.set_current_index(0)
    # Model to widget
    assert widget.value() == 42
    # Widget to model
    widget.setValue(99)
    assert model.item(0).data(QtCore.Qt.UserRole)["quantity"] == 99

def test_model_data_mapper_refresh(qtbot):
    model = create_simple_model()
    widget = DummyWidget()
    mapper = ModelDataMapper()
    mapper.set_model(model)
    mapper.add_mapping(
        widget, "value", role=QtCore.Qt.UserRole,
        from_model=lambda d: d.get("quantity", 0),
        from_property=lambda v, d: {**d, "quantity": v},
        signal=widget.valueChanged
    )
    mapper.set_current_index(0)
    model.item(0).setData({"quantity": 123, "format": "usd"}, QtCore.Qt.UserRole)
    mapper.refresh()
    assert widget.value() == 123
