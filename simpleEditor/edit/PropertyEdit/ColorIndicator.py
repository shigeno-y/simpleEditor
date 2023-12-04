import inspect

from pxr import (
    Gf,
)
from PySide2.QtCore import (
    QSignalBlocker,
    Qt,
    Signal,
)
from PySide2.QtGui import (
    QColor,
    # QValidator,      # TEMP: Expression を実装するときに使用する.
    QDoubleValidator,  # TEMP: Expression を実装したら使用しなくなる.
    QImage,
    QIntValidator,  # TEMP: Expression を実装したら使用しなくなる.
    QPainter,
    QPixmap,
)
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
)

from simpleEditor.edit.PropertyEditWidgets import ExpressionFloatLineEdit, SignalBlocker


class ColorIndicator(QLabel):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._resultImage = QImage(10, 10, QImage.Format_RGB32)
        self._color = None
        self._pixMap = None

        self.sync(currentTime)

    def setValue(self, color):
        from pprint import pprint

        print(color)
        pprint(inspect.stack()[1])
        c = QColor(QColor.ExtendedRgb, color[0], color[1], color[2])
        if self._color != c:
            self._color = c
            self._resultImage.fill(self._color)
            self._pixMap = QPixmap.fromImage(self._resultImage)
            self.setPixmap(self._pixMap)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setValue(self._attr.Get(currentTime))
