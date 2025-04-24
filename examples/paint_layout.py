import sys
import os
met_qt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python'))
if met_qt_path not in sys.path:
    sys.path.append(met_qt_path)

from met_qt.gui.paint_layout import BoxPaintLayout, BoxShape, BoxText, PaintStyle, ShapeType, BoxPaintItem, CornerFlag
from PySide6 import QtWidgets, QtCore, QtGui


class BoxLayoutWidget(QtWidgets.QWidget):
    """Widget that uses box layouts for painting and positioning nested items."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        layout = BoxPaintLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setMinimumSize(100, 100)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        try:
            if not painter.begin(self):
                return
            opt = QtWidgets.QStyleOption()
            opt.initFrom(self)
            self.style().drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            BoxPaintLayout.render(self.layout(), painter, self.mapFromGlobal(QtGui.QCursor.pos()))
        finally:
            painter.end()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            hit_items = BoxPaintLayout.hit_test(self.layout(), event.pos())
            if hit_items:
                self.layout().clicked.emit()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)


# --- Example Usage ---
if __name__ == "__main__":
    print("Starting nested box layout example with standard Qt layouts")
    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()

    # Create the main widget
    box_widget = BoxLayoutWidget()
    palette = box_widget.palette()
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor("black"))
    box_widget.setPalette(palette)

    # Example fonts
    font_bold = QtGui.QFont()
    font_bold.setBold(True)
    font_italic = QtGui.QFont()
    font_italic.setItalic(True)
    font_large = QtGui.QFont()
    font_large.setPointSize(16)

    # 1. Add a top-level box (rectangle, centered bold text)
    top_shape = BoxShape(
        style=PaintStyle(brush_color=QtGui.QColor("dodgerblue")),
        hover_style=PaintStyle(brush_color=QtGui.QColor("lightyellow")),  # Light yellow highlight on hover
        shape_type=ShapeType.Box
    )
    top_text = BoxText(
        text="Main Container",
        alignment=QtCore.Qt.AlignmentFlag.AlignCenter,
        font=font_bold,
        style=PaintStyle()
    )
    top_box = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    top_box.setObjectName("top_box")
    top_box.setSizeHint((400, 500))
    top_box.set_paint_items([BoxPaintItem(shape=top_shape, text=top_text)])

    # 2. Nested box: rounded, left-aligned italic text, with hover style
    nested_shape = BoxShape(
        style=PaintStyle(brush_color=QtGui.QColor("orange")),
        hover_style=PaintStyle(brush_color=QtGui.QColor("#FFD580")),
        shape_type=ShapeType.Box,
        corner_radius=15
    )
    nested_text = BoxText(
        text="Horizontal Box",
        alignment=QtCore.Qt.AlignmentFlag.AlignLeft,
        font=font_italic,
    )
    nested_box1 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.LeftToRight)
    nested_box1.setObjectName("nested_box1")
    nested_box1.setSizeHint((200, 100))
    nested_box1.set_paint_items([BoxPaintItem(shape=nested_shape, text=nested_text)])

    # 3. Inner box: rounded, right-aligned large text, with disabled style
    inner_shape1 = BoxShape(
        style=PaintStyle(brush_color=QtGui.QColor("lightgreen")),
        hover_style=PaintStyle(brush_color=QtGui.QColor("#red")),
        disabled_style=PaintStyle(brush_color=QtGui.QColor("#A0A0A0")),
        shape_type=ShapeType.Box,
        corner_radius=10,
        rounded_corners=CornerFlag.TopLeft | CornerFlag.BottomLeft
    )
    inner_text1 = BoxText(
        text="Green Box",
        alignment=QtCore.Qt.AlignmentFlag.AlignRight,
        font=font_large,
    )
    inner_box1 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    inner_box1.setObjectName("inner_box1")
    inner_box1.setSizeHint((90, 90))
    inner_box1.set_paint_items([BoxPaintItem(shape=inner_shape1, text=inner_text1)])

    # 4. Inner box: rounded, word-wrapped, centered text, invisible
    inner_shape2 = BoxShape(
        style=PaintStyle(brush_role=QtGui.QPalette.ColorRole.Highlight),
        shape_type=ShapeType.Box,
        corner_radius=10,
        rounded_corners=CornerFlag.TopRight | CornerFlag.BottomRight,
        visible=False
    )
    inner_text2 = BoxText(
        text="Highlight\nBox",
        alignment=QtCore.Qt.AlignmentFlag.AlignCenter,
        wordWrap=True,
        style=PaintStyle(),
        visible=False
    )
    inner_box2 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    inner_box2.setObjectName("inner_box2")
    inner_box2.setSizeHint((90, 90))
    inner_box2.set_paint_items([BoxPaintItem(shape=inner_shape2, text=inner_text2)])

    # 5. Custom path (star), top-aligned text
    star_path = QtGui.QPainterPath()
    star_path.moveTo(50, 0)
    star_path.lineTo(60, 35)
    star_path.lineTo(100, 35)
    star_path.lineTo(70, 60)
    star_path.lineTo(80, 100)
    star_path.lineTo(50, 75)
    star_path.lineTo(20, 100)
    star_path.lineTo(30, 60)
    star_path.lineTo(0, 35)
    star_path.lineTo(40, 35)
    star_path.closeSubpath()
    star_shape = BoxShape(
        style=PaintStyle(brush_color=QtGui.QColor("lightpink")),
        shape_type=ShapeType.Path,
        painter_path=star_path
    )
    star_text = BoxText(
        text="Star Shape",
        alignment=QtCore.Qt.AlignmentFlag.AlignTop,
    )
    nested_box2 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    nested_box2.setObjectName("nested_box2")
    nested_box2.setSizeHint((200, 100))
    nested_box2.set_paint_items([BoxPaintItem(shape=star_shape, text=star_text)])

    # 6. Grid layout with painted boxes (various alignments)
    standard_grid = QtWidgets.QGridLayout()
    standard_grid.setContentsMargins(10, 10, 10, 10)
    standard_grid.setSpacing(8)
    grid_box1 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    grid_box1.setObjectName("grid_box1")
    grid_box1.setSizeHint((80, 60))
    grid_box1.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("lightcoral")),
                            hover_style=PaintStyle(brush_color=QtGui.QColor("red")),  # Light blue highlight
                            shape_type=ShapeType.Box, corner_radius=5),
            text="Grid 1,1"
        )
    ])
    grid_box2 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    grid_box2.setObjectName("grid_box2")
    grid_box2.setSizeHint((80, 60))
    grid_box2.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("palegreen")), shape_type=ShapeType.Box),
            text="Grid 1,2"
        )
    ])
    grid_box3 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    grid_box3.setObjectName("grid_box3")
    grid_box3.setSizeHint((80, 60))
    grid_box3.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("cornflowerblue")), shape_type=ShapeType.Box, corner_radius=8, rounded_corners=CornerFlag.TopLeft | CornerFlag.BottomRight),
            text="Grid 2,1"
        )
    ])
    grid_box4 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    grid_box4.setObjectName("grid_box4")
    grid_box4.setSizeHint((80, 60))
    grid_box4.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("khaki")), shape_type=ShapeType.Box),
            text="Grid 2,2"
        )
    ])
    standard_grid.addLayout(grid_box1, 0, 0)
    standard_grid.addLayout(grid_box2, 0, 1)
    standard_grid.addLayout(grid_box3, 1, 0)
    standard_grid.addLayout(grid_box4, 1, 1)

    # 7. Horizontal layout with painted boxes (diamond, different fonts)
    standard_hbox = QtWidgets.QHBoxLayout()
    standard_hbox.setContentsMargins(5, 5, 5, 5)
    standard_hbox.setSpacing(10)
    hbox_item1 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    hbox_item1.setObjectName("hbox_item1")
    hbox_item1.setSizeHint((60, 40))
    hbox_item1.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("plum")), shape_type=ShapeType.Box, corner_radius=5, rounded_corners=CornerFlag.TopLeft | CornerFlag.TopRight),
            text=BoxText(text="HBox 1", alignment=QtCore.Qt.AlignmentFlag.AlignLeft, font=font_bold, style=PaintStyle())
        )
    ])
    hbox_item2 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    hbox_item2.setObjectName("hbox_item2")
    hbox_item2.setSizeHint((60, 40))
    hbox_item2.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("mediumaquamarine")), shape_type=ShapeType.Box),
            text=BoxText(text="HBox 2", alignment=QtCore.Qt.AlignmentFlag.AlignRight, font=font_italic, style=PaintStyle())
        )
    ])
    diamond_path = QtGui.QPainterPath()
    diamond_path.moveTo(25, 0)
    diamond_path.lineTo(50, 20)
    diamond_path.lineTo(25, 40)
    diamond_path.lineTo(0, 20)
    diamond_path.closeSubpath()
    hbox_item3 = BoxPaintLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
    hbox_item3.setObjectName("hbox_item3")
    hbox_item3.setSizeHint((60, 40))
    hbox_item3.set_paint_items([
        BoxPaintItem(
            shape=BoxShape(style=PaintStyle(brush_color=QtGui.QColor("gold")), shape_type=ShapeType.Path, painter_path=diamond_path),
            text=BoxText(text="Diamond", alignment=QtCore.Qt.AlignmentFlag.AlignCenter, font=font_large, style=PaintStyle())
        )
    ])
    standard_hbox.addLayout(hbox_item1)
    standard_hbox.addLayout(hbox_item2)
    standard_hbox.addLayout(hbox_item3)

    # Add all containers and layouts to the top box
    top_box.addLayout(nested_box1)
    top_box.addSpacing(10)
    top_box.addLayout(nested_box2)
    top_box.addSpacing(15)
    top_box.addLayout(standard_grid)
    top_box.addSpacing(15)
    top_box.addLayout(standard_hbox)

    # Add the top box to the widget
    box_widget.layout().addLayout(top_box)

    # Set up the main window
    window.setCentralWidget(box_widget)
    window.setWindowTitle("Painted Layouts Integration")
    window.setGeometry(100, 100, 500, 700)

    window.show()
    sys.exit(app.exec())


