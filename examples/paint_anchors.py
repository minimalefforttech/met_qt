import sys
import os
met_qt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python'))
if met_qt_path not in sys.path:
    sys.path.append(met_qt_path)

from PySide6 import QtWidgets, QtCore, QtGui
from met_qt.gui import paint_utils



class PainterExampleWidget(QtWidgets.QWidget):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        # # Apply a transform for testing
        # transform = QtGui.QTransform()
        # transform.translate(self.width() // 2, self.height() // 2)
        # transform.rotate(15)
        # transform.scale(1.2, 0.8)
        # transform.translate(-self.width() // 2, -self.height() // 2)
        # painter.setTransform(transform)

        event_rect = event.rect()
        spacing = 10
        # Top row: two left, two right, two center (center squish)
        # Left
        text_rect = paint_utils.draw_text(painter, paint_utils.anchor((120, 30), left=event_rect.left()+spacing, top=event_rect.top()+spacing), QtCore.Qt.AlignLeft, "Hello Anchor")
        rect_rect = paint_utils.anchor((80, 40), left=text_rect.right()+spacing, top=event_rect.top()+spacing)
        painter.drawRect(rect_rect)
        # Right
        option_btn_right = QtWidgets.QStyleOptionButton()
        option_btn_right.rect = paint_utils.anchor((80, 40), right=event_rect.right()-spacing, top=event_rect.top()+spacing)
        option_btn_right.text = "Right Btn"
        right_btn_rect = paint_utils.draw_control(painter, QtWidgets.QStyle.CE_PushButton, option_btn_right)
        option_btn = QtWidgets.QStyleOptionButton()
        option_btn.rect = paint_utils.anchor((80, 40), right=option_btn_right.rect.left()-spacing, top=event_rect.top()+spacing)
        option_btn.text = "Btn"
        control_rect = paint_utils.draw_control(painter, QtWidgets.QStyle.CE_PushButton, option_btn)
        # Center (squish between left and right)
        center_left = rect_rect.right() + spacing
        center_right = option_btn.rect.left() - spacing
        center_height = 40
        rounded_rect = paint_utils.draw_partially_rounded_rect(
            painter,
            paint_utils.anchor((0, center_height),
                    left=center_left, right=(center_left+center_right)//2-spacing//2,
                    top=event_rect.top()+spacing), 0, 0, 10, 0)
        ellipse_rect = paint_utils.anchor((0, center_height), left=(center_left+center_right)//2+spacing//2, right=center_right, top=event_rect.top()+spacing)
        painter.drawEllipse(ellipse_rect)
        # Bottom row, left-aligned
        pixmap = QtGui.QPixmap(40, 40)
        pixmap.fill(QtGui.QColor('blue'))
        pixmap_rect = paint_utils.anchor((40, 40), left=event_rect.left()+spacing, bottom=event_rect.bottom()-spacing-40)
        painter.drawPixmap(pixmap_rect, pixmap)
        image = QtGui.QImage(40, 40, QtGui.QImage.Format_ARGB32)
        image.fill(QtGui.QColor('green'))
        image_rect = paint_utils.anchor((40, 40), left=pixmap_rect.right()+spacing, bottom=event_rect.bottom()-spacing-40)
        painter.drawImage(image_rect, image)
        # Centered horizontally at the bottom
        center_x = event_rect.left() + (event_rect.width() - 100) // 2
        itemtext_rect = paint_utils.draw_item_text(painter, paint_utils.anchor((100, 30), left=center_x, bottom=event_rect.bottom()-spacing), QtCore.Qt.AlignCenter, self.palette(), True, "Centered Text")
        # Path between bottom left and bottom right
        path = QtGui.QPainterPath()
        path.moveTo(pixmap_rect.left(), pixmap_rect.bottom()-10)
        path.cubicTo(pixmap_rect.left()+40, pixmap_rect.bottom()-60, image_rect.right()+40, itemtext_rect.top()-20, event_rect.right()-spacing, itemtext_rect.bottom()-10)
        path_rect = paint_utils.draw_path(painter, path)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = PainterExampleWidget()
    w.resize(650, 120)
    w.setWindowTitle("Painter Example")
    w.show()
    sys.exit(app.exec())