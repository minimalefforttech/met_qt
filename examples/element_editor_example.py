from met_qt._internal.qtcompat import QtCore, QtGui, QtWidgets
from met_qt.core.model_data_mapper import ModelDataMapper

FORMATS = ["usd", "fbx", "alembic", "obj", "ma", "mb"]
HEADERS = ["Element Name", "Quantity", "Format"]
BASE_ELEMENTS = [
    ["chrHuman01", 3, "usd"],
    ["chrOrc01", 2, "fbx"],
    ["amlCheetah02", 1, "alembic"],
    ["prpSword01", 5, "usd"],
    ["envForest01", 1, "alembic"],
]

def create_model():
    DATA = []
    for i in range(20):
        for elem in BASE_ELEMENTS:
            new_elem = elem.copy()
            new_elem[0] = f"{new_elem[0]}_{i+1:02d}"
            DATA.append(new_elem)
    model = QtGui.QStandardItemModel()
    model.setHorizontalHeaderLabels(HEADERS)
    for data_row in DATA:
        item = QtGui.QStandardItem(str(data_row[0]))
        item.setData({
            "quantity": data_row[1],
            "format": data_row[2],
        }, QtCore.Qt.UserRole)
        model.appendRow(item)
    return model

class ElementEditorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        # ListView
        self.list_view = QtWidgets.QListView()
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.model = create_model()
        self.list_view.setModel(self.model)
        layout.addWidget(self.list_view, 1)
        # Form
        form_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QFormLayout(form_widget)
        self.label_name = QtWidgets.QLabel()
        self.spin_quantity = QtWidgets.QSpinBox()
        self.spin_quantity.setRange(0, 999)
        self.combo_format = QtWidgets.QComboBox()
        self.combo_format.addItems(FORMATS)
        form_layout.addRow("Element Name", self.label_name)
        form_layout.addRow("Quantity", self.spin_quantity)
        form_layout.addRow("Format", self.combo_format)
        layout.addWidget(form_widget, 2)
        # Mapper
        self.mapper = ModelDataMapper(self)
        self.mapper.set_model(self.model)
        self.mapper.add_mapping(self.label_name, "text", role=QtCore.Qt.DisplayRole)
        self.mapper.add_mapping(
            self.spin_quantity, "value", role=QtCore.Qt.UserRole,
            fn_set=lambda w, d: w.setValue(d.get("quantity", 0)),
            fn_extract=lambda w, d: {**d, "quantity": w.value()},
            signal=self.spin_quantity.valueChanged
        )
        self.mapper.add_mapping(
            self.combo_format, "currentText", role=QtCore.Qt.UserRole,
            fn_set=lambda w, d: w.setCurrentText(d.get("format", FORMATS[0])),
            fn_extract=lambda w, d: {**d, "format": w.currentText()},
            signal=self.combo_format.currentTextChanged
        )
        self.list_view.selectionModel().currentChanged.connect(self._on_selection_changed)
        self.mapper.set_current_index(0)
        self.list_view.setCurrentIndex(self.model.index(0, 0))

    def _on_selection_changed(self, current, previous):
        self.mapper.set_current_index(current.row())

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = ElementEditorWidget()
    w.setWindowTitle("Element Editor Example")
    w.resize(600, 400)
    w.show()
    sys.exit(app.exec())
