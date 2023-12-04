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
        import inspect
        from pprint import pprint

        print(color)
        pprint(inspect.stack()[1])
        c = QColor(QColor.ExtendedRgb, color[0], color[1], color[2])
        if self._color != c:
            self._color = c
            self._resultImage.fill(self._color)
            self._pixMap = QPixmap.fromImage(self._resultImage)
            self.setPixmap(self._pixMap)


class ColorPickerWidget(QWidget):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._indicator = ColorIndicator(attr, currentTime, parent)
        self._widgetR = ExpressionFloatLineEdit(self)
        self._widgetG = ExpressionFloatLineEdit(self)
        self._widgetB = ExpressionFloatLineEdit(self)
        self._layout.addWidget(self._indicator)
        self._layout.addWidget(self._widgetR)
        self._layout.addWidget(self._widgetG)
        self._layout.addWidget(self._widgetB)
        self._layout.setMargin(0)
        self.setLayout(self._layout)
        self._widgetR.valueChanged.connect(self._onValueChanged)
        self._widgetG.valueChanged.connect(self._onValueChanged)
        self._widgetB.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onValueChanged(self, _):
        self._attr.Set(self.value())

    def value(self):
        return Gf.Vec3f(
            self._widgetR.value(), self._widgetG.value(), self._widgetB.value()
        )

    def setValue(self, value):
        print(value)
        with SignalBlocker(self._widgetR):
            self._widgetR.setValue(value[0])
        with SignalBlocker(self._widgetG):
            self._widgetG.setValue(value[1])
        with SignalBlocker(self._widgetB):
            self._widgetB.setValue(value[2])
        with SignalBlocker(self._indicator):
            self._indicator.setValue(value)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setValue(self._attr.Get(currentTime))
