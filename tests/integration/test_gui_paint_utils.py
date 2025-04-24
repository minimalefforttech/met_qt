import pytest
from met_qt.gui import paint_utils
from met_qt._internal.qtcompat import QtWidgets, QtCore, QtGui

@pytest.fixture
def painter_and_pixmap(qtbot):
    widget = QtWidgets.QWidget()
    qtbot.addWidget(widget)
    pixmap = QtGui.QPixmap(100, 100)
    pixmap.fill(QtCore.Qt.white)
    painter = QtGui.QPainter(pixmap)
    yield painter, pixmap
    painter.end()

def test_draw_text(painter_and_pixmap):
    painter, _ = painter_and_pixmap
    rect = paint_utils.draw_text(painter, QtCore.QRect(10, 10, 80, 20), 0, "Hello")
    assert rect.width() > 0 and rect.height() > 0

def test_draw_partially_rounded_rect(painter_and_pixmap):
    painter, _ = painter_and_pixmap
    rect = paint_utils.draw_partially_rounded_rect(painter, QtCore.QRect(10, 10, 80, 80), 10, 10, 10, 10)
    assert rect.width() > 0 and rect.height() > 0

def test_draw_path(painter_and_pixmap):
    painter, _ = painter_and_pixmap
    path = QtGui.QPainterPath()
    path.addRect(20, 20, 40, 40)
    rect = paint_utils.draw_path(painter, path)
    assert rect.width() > 0 and rect.height() > 0

def test_anchor(qtbot):
    rect = paint_utils.anchor((50, 50), left=10, top=10)
    assert rect.width() > 0 and rect.height() > 0

def test_to_global_and_from_global(painter_and_pixmap):
    painter, _ = painter_and_pixmap
    point = QtCore.QPoint(5, 5)
    global_point = paint_utils.to_global(painter, point)
    widget_point = paint_utils.from_global(painter, global_point)
    assert isinstance(global_point, QtCore.QPoint)
    assert isinstance(widget_point, QtCore.QPoint)

def test_draw_item_text(painter_and_pixmap):
    painter, _ = painter_and_pixmap
    palette = QtGui.QPalette()
    rect = paint_utils.draw_item_text(
        painter,
        QtCore.QRect(10, 10, 80, 20),
        QtCore.Qt.AlignLeft,
        palette,
        True,
        "Test Text"
    )
    assert rect.width() >= 0 and rect.height() >= 0

def test_draw_primitive(painter_and_pixmap):
    painter, _ = painter_and_pixmap
    style = QtWidgets.QApplication.style()
    option = QtWidgets.QStyleOption()
    option.rect = QtCore.QRect(10, 10, 20, 20)
    rect = paint_utils.draw_primitive(
        painter,
        QtWidgets.QStyle.PE_Frame,
        option,
        None,
        style
    )
    assert rect.width() > 0 and rect.height() > 0

def test_draw_control(painter_and_pixmap):
    painter, _ = painter_and_pixmap
    style = QtWidgets.QApplication.style()
    option = QtWidgets.QStyleOption()
    option.rect = QtCore.QRect(10, 10, 20, 20)
    rect = paint_utils.draw_control(
        painter,
        QtWidgets.QStyle.CE_PushButton,
        option,
        None,
        style
    )
    assert rect.width() > 0 and rect.height() > 0
