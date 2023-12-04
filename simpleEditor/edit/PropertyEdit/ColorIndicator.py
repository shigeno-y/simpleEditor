from PySide2.QtCore import (
    Qt,
    QSignalBlocker,
    Signal,
)
from PySide2.QtGui import (
    # QValidator,      # TEMP: Expression を実装するときに使用する.
    QDoubleValidator,  # TEMP: Expression を実装したら使用しなくなる.
    QIntValidator,  # TEMP: Expression を実装したら使用しなくなる.
    QImage,
    QPainter,
    QColor,
    QPixmap,
)
from PySide2.QtWidgets import (
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QWidget,
)

from pxr import (
    Gf,
)


class colorIndicator(QLabel):
    def __init__(self, parent=None, color=Gf.Vec3f(1.0, 1.0, 1.0), *args, **kwargs):
        super(colorIndicator, self).__init__(parent, *args, **kwargs)
        self.resultImage = QImage(10, 10, QImage.Format_RGB32)
        self.painter = QPainter(self.resultImage)
        color = QColor(QColor.ExtendedRgb, color[0], color[1], color[2])
        self.painter.begin(self.resultImage)
        self.painter.setBrush(color)
        self.painter.setPen(color)
        self.painter.drawRect(0, 0, 10, 10)
        self.painter.end()
        pixmap = QPixmap.fromImage(self.resultImage)
        self.setPixmap(pixmap)
