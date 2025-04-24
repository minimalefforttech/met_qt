import pytest

from met_qt.gui.paint_layout import BoxPaintLayout, BoxShape, BoxText, PaintStyle, ShapeType, BoxPaintItem, CornerFlag, BoxPaintLayoutFlag

from met_qt._internal.qtcompat import QtWidgets, QtCore, QtGui

@pytest.fixture
def widget(qtbot):
    w = QtWidgets.QWidget()
    layout = BoxPaintLayout()
    w.setLayout(layout)
    qtbot.addWidget(w)
    return w, layout

def test_box_paint_layout_add_and_get_items(widget):
    w, layout = widget
    shape = BoxShape(style=PaintStyle(brush_color=QtGui.QColor('red')))
    text = BoxText(text="Hello")
    item = BoxPaintItem(shape=shape, text=text)
    layout.set_paint_items([item])
    assert layout.get_paint_items() == [item]

def test_box_paint_layout_size_hint(widget):
    w, layout = widget
    layout.setSizeHint((123, 45))
    hint = layout.sizeHint()
    assert hint.width() == 123
    assert hint.height() == 45

def test_box_paint_layout_flags(widget):
    w, layout = widget
    layout.flags = int(BoxPaintLayoutFlag.Enabled | BoxPaintLayoutFlag.Visible)
    assert layout.flags == int(BoxPaintLayoutFlag.Enabled | BoxPaintLayoutFlag.Visible)
    layout.flags = int(BoxPaintLayoutFlag.Visible)
    assert layout.flags == int(BoxPaintLayoutFlag.Visible)

def test_box_paint_item_hit_test(widget):
    w, layout = widget
    shape = BoxShape(style=PaintStyle(brush_color=QtGui.QColor('red')))
    text = BoxText(text="Hello")
    item = BoxPaintItem(shape=shape, text=text)
    layout.set_paint_items([item])
    w.resize(100, 100)
    rect = QtCore.QRect(0, 0, 100, 100)
    pos_inside = QtCore.QPoint(10, 10)
    pos_outside = QtCore.QPoint(200, 200)
    assert item.hit_test(rect, pos_inside)
    assert not item.hit_test(rect, pos_outside)

def test_box_paint_layout_paint_runs(widget, qtbot):
    w, layout = widget
    shape = BoxShape(style=PaintStyle(brush_color=QtGui.QColor('red')))
    text = BoxText(text="Hello")
    item = BoxPaintItem(shape=shape, text=text)
    layout.set_paint_items([item])
    w.resize(100, 100)
    pixmap = QtGui.QPixmap(100, 100)
    pixmap.fill(QtCore.Qt.GlobalColor.white)
    painter = QtGui.QPainter(pixmap)
    layout.paint(painter, 0)
    painter.end()

def test_box_paint_layout_render_runs(widget, qtbot):
    w, layout = widget
    shape = BoxShape(style=PaintStyle(brush_color=QtGui.QColor('red')))
    text = BoxText(text="Hello")
    item = BoxPaintItem(shape=shape, text=text)
    layout.set_paint_items([item])
    w.resize(100, 100)
    pixmap = QtGui.QPixmap(100, 100)
    pixmap.fill(QtCore.Qt.GlobalColor.white)
    painter = QtGui.QPainter(pixmap)
    BoxPaintLayout.render(layout, painter)
    painter.end()
