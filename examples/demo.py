from PySide6 import QtWidgets, QtCore, QtGui
from met_qt.gui import paint_utils
from met_qt.core.binding import Bindings
from met_qt.core.model_data_mapper import ModelDataMapper
from met_qt.widgets.float_slider import FloatSlider
from met_qt.widgets.range_slider import RangeSlider

reference_date = QtCore.QDate(2025, 4, 7)

PEOPLE = [
    "Alice Tinker",
    "Bob Morgan",
    "Charlie Park",
    "David Chen",
    "Emma Williams",
    "Sophia Rodriguez",
    "Michael Johnson",
    "Olivia Smith",
    "Liam Brown",
    "Noah Davis",
    "Ava Wilson",
    "Isabella Martinez",
]

SAMPLE_TICKET_DATA = [
    {
        "id": "PIPE-101",
        "summary": "Fix pipeline issue",
        "assignee": "Alice Tinker",
        "comments": 2,
        "updated": reference_date.addDays(-3).toString("yyyy-MM-dd"),  
        "reporter": "Emma Williams",
        "priority": 4.5
    },
    {
        "id": "IT-202",
        "summary": "Resolve network problem",
        "assignee": "Bob Morgan",
        "comments": 0,
        "updated": reference_date.addDays(-8).toString("yyyy-MM-dd"),  
        "reporter": "David Chen",
        "priority": 3.0
    },
    {
        "id": "CREHELP-303",
        "summary": "Creature animation bug",
        "assignee": "Charlie Park",
        "comments": 14,
        "updated": reference_date.addDays(-1).toString("yyyy-MM-dd"),  
        "reporter": "Sophia Rodriguez",
        "priority": 5.0
    },
    {
        "id": "PIPE-104",
        "summary": "Optimize data flow",
        "assignee": "Alice Tinker",
        "comments": 0,
        "updated": reference_date.addDays(-12).toString("yyyy-MM-dd"),  
        "reporter": "Michael Johnson",
        "priority": 2.5
    },
    {
        "id": "IT-205",
        "summary": "Install new software",
        "assignee": "Bob Morgan",
        "comments": 0,
        "updated": reference_date.addDays(-6).toString("yyyy-MM-dd"),  
        "reporter": "Olivia Smith",
        "priority": 1.5
    }
]

class TicketItemDelegate(QtWidgets.QStyledItemDelegate):
    @staticmethod
    def priority_color(val):
        v = max(0.0, min(5.0, float(val))) / 5.0
        if v < 0.5:
            # Blue to orange transition
            r = int(30 + (255-30)*v*2)
            g = int(144 + (165-144)*v*2)
            b = int(255 - (255-0)*v*2)
        else:
            # Orange to red transition
            r = 255
            g = int(165 - (165-0)*(v-0.5)*2)
            b = 0
        return QtGui.QColor(r, g, b)
    
    def sizeHint(self, option, index):
        # Ideally you would get this from the actual data
        return QtCore.QSize(option.rect.width(), 60)

    def paint(self, painter, option, index):
        painter.save()
        ticket = index.data(QtCore.Qt.DisplayRole)
        data = index.data(QtCore.Qt.UserRole)
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        rect = option.rect
        left_margin = 10
        spacing = 8
        circle_size = 30
        circle_rect = paint_utils.anchor((circle_size, circle_size),
            left=rect.left()+left_margin,
            top=rect.top() + (rect.height()-circle_size)//2)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        name_hash = sum(ord(c) for c in data["reporter"])
        hue = (name_hash % 360) / 360.0
        color = QtGui.QColor.fromHslF(hue, 0.7, 0.5)
        painter.setBrush(QtGui.QBrush(color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(circle_rect)
        initials = "".join(name[0].upper() for name in data["reporter"].split() if name)
        painter.setPen(QtCore.Qt.white)
        paint_utils.draw_text(painter, circle_rect, QtCore.Qt.AlignCenter, initials)

        text_left = circle_rect.right() + spacing
        text_width = rect.width() - text_left - 10
        id_rect = paint_utils.anchor((text_width-100, 20), left=text_left, top=rect.top()+2)
        painter.setPen(option.palette.text().color())
        id_rect = paint_utils.draw_text(painter, id_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop, ticket)

        priority_size = id_rect.height() - 5
        priority_rect = paint_utils.anchor((priority_size, priority_size),
            left=id_rect.right()+spacing,
            vcenter=id_rect.center().y())
        painter.setBrush(self.priority_color(data['priority']))
        painter.setPen(QtCore.Qt.NoPen)
        paint_utils.draw_partially_rounded_rect(
            painter, priority_rect, 4, 8, 8, 4
        )
        painter.setPen(QtCore.Qt.white)

        summary_rect = paint_utils.anchor((text_width-100, 20), left=text_left, top=id_rect.bottom()-2)
        paint_utils.draw_text(painter, summary_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop, data["summary"])

        assignee_rect = paint_utils.anchor((140, 20), right=rect.right()-10, top=rect.top()+2)
        paint_utils.draw_text(painter, assignee_rect, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop, data["assignee"])

        comments_text = f"{data['comments']} 🗩"
        comments_rect = paint_utils.anchor((140, 20), right=rect.right()-10, top=assignee_rect.bottom()-2)
        paint_utils.draw_text(painter, comments_rect, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop, comments_text)

        updated_date = QtCore.QDate.fromString(data["updated"], "yyyy-MM-dd")
        current_date = QtCore.QDate.currentDate()
        days_diff = updated_date.daysTo(current_date)
        days_text = f"{days_diff} days ago"
        days_rect = paint_utils.anchor((140, 20), right=rect.right()-10, top=comments_rect.bottom()-2)
        paint_utils.draw_text(painter, days_rect, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop, days_text)
        painter.restore()

class TicketListWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ticket List View")

        self.setMinimumSize(700, 400)

        layout = QtWidgets.QVBoxLayout(self)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        layout.addWidget(splitter)
        # ListView
        self.list_view = QtWidgets.QListView()
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setItemDelegate(TicketItemDelegate(self))
        splitter.addWidget(self.list_view)
        # Model
        self.model = QtGui.QStandardItemModel()
        for ticket in SAMPLE_TICKET_DATA:
            item = QtGui.QStandardItem(ticket["id"])
            item.setData(ticket, QtCore.Qt.UserRole)
            self.model.appendRow(item)
        self.list_view.setModel(self.model)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # Form Layout
        form_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QFormLayout(form_widget)
        self.edit_summary = QtWidgets.QLineEdit()
        self.label_updated = QtWidgets.QLabel()
        self.combo_reporter = QtWidgets.QComboBox()
        self.combo_reporter.addItems(PEOPLE)
        self.combo_assignee = QtWidgets.QComboBox()
        self.combo_assignee.addItems(PEOPLE)
        self.float_priority = FloatSlider()
        self.float_priority.range = (0.0, 5.0)
        form_layout.addRow("Summary", self.edit_summary)
        form_layout.addRow("Updated", self.label_updated)
        form_layout.addRow("Reporter", self.combo_reporter)
        form_layout.addRow("Assignee", self.combo_assignee)
        form_layout.addRow("Priority", self.float_priority)
        splitter.addWidget(form_widget)
        splitter.setStretchFactor(1, 2)
        # Model Mapper
        self.mapper = ModelDataMapper(self)
        self.mapper.set_model(self.model)
        self.mapper.add_mapping(self.edit_summary, "text", role=QtCore.Qt.UserRole,
            from_model=lambda d: d.get("summary", ""),
            from_property=lambda v, d: {**d, "summary": v},
            signal=self.edit_summary.textChanged)
        self.mapper.add_mapping(self.label_updated, "text", role=QtCore.Qt.UserRole,
            from_model=lambda d: self._format_updated(d.get("updated")),
            from_property=None)
        self.mapper.add_mapping(self.combo_reporter, "currentText", role=QtCore.Qt.UserRole,
            from_model=lambda d: d.get("reporter", PEOPLE[0]),
            from_property=lambda v, d: {**d, "reporter": v})
        self.mapper.add_mapping(self.combo_assignee, "currentText", role=QtCore.Qt.UserRole,
            from_model=lambda d: d.get("assignee", PEOPLE[0]),
            from_property=lambda v, d: {**d, "assignee": v})
        self.mapper.add_mapping(self.float_priority, "value", role=QtCore.Qt.UserRole,
            from_model=lambda d: d.get("priority", 1.0),
            from_property=lambda v, d: {**d, "priority": v})
        self.list_view.selectionModel().currentChanged.connect(self._on_selection_changed)
        self.mapper.set_current_index(0)
        self.list_view.setCurrentIndex(self.model.index(0, 0))

        # First range slider example - with soft range
        slider_group = QtWidgets.QGroupBox("Sliders")
        slider_layout = QtWidgets.QVBoxLayout(slider_group)
        
        float_layout = QtWidgets.QHBoxLayout()
        slider_layout.addLayout(float_layout)
        
        float_slider = FloatSlider()
        float_slider.range = (-10.0, 10.0)
        float_layout.addWidget(float_slider)
        float_layout.setStretchFactor(float_slider, 1)

        spin_value = QtWidgets.QDoubleSpinBox()
        spin_value.setRange(-10.0, 10.0)
        spin_value.setDecimals(2)
        float_layout.addWidget(spin_value)

        range_layout = QtWidgets.QHBoxLayout()
        slider_layout.addLayout(range_layout)
        
        spin_min = QtWidgets.QDoubleSpinBox()
        spin_min.setRange(0.0, 100.0)
        spin_min.setDecimals(2)
        range_layout.addWidget(spin_min)

        range_slider = RangeSlider()
        range_slider.range = (0.0, 100.0)
        range_slider.soft_range = (20.0, 80.0)
        range_layout.addWidget(range_slider)
        range_layout.setStretchFactor(range_slider, 1)

        spin_max = QtWidgets.QDoubleSpinBox()
        spin_max.setRange(0.0, 100.0)
        spin_max.setDecimals(2)
        range_layout.addWidget(spin_max)

        bindings = Bindings(self)
        with bindings.bind_group() as group:
            group.add(float_slider, "value")
            group.add(spin_value, "value")

        with bindings.bind_group() as group:
            group.add(range_slider, "min_value")
            group.add(spin_min, "value")

        with bindings.bind_group() as group:
            group.add(range_slider, "max_value")
            group.add(spin_max, "value")
            range_slider.min_value = 30
            range_slider.max_value = 70

        # Add all groups to main layout
        layout.addWidget(slider_group)
        layout.setStretchFactor(splitter, 1)

    def _on_selection_changed(self, current, previous):
        self.mapper.set_current_index(current.row())

    def _format_updated(self, date_str):
        if not date_str:
            return ""
        updated_date = QtCore.QDate.fromString(date_str, "yyyy-MM-dd")
        current_date = QtCore.QDate.currentDate()
        days_diff = updated_date.daysTo(current_date)
        if days_diff == 0:
            return "Today"
        elif days_diff == 1:
            return "Yesterday"
        else:
            return f"{days_diff} days ago"

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widget = TicketListWidget()
    widget.show()
    sys.exit(app.exec())