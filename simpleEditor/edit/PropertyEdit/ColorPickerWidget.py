from PySide2.QtCore import (
    Qt,
    QSignalBlocker,
    Signal,
)
from PySide2.QtGui import (
    # QValidator,      # TEMP: Expression を実装するときに使用する.
    QDoubleValidator,  # TEMP: Expression を実装したら使用しなくなる.
    QIntValidator,  # TEMP: Expression を実装したら使用しなくなる.
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

from simpleEditor.edit.PropertyEditWidgets import SignalBlocker, ExpressionFloatLineEdit




class ColorPickerWidget(QWidget):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._widgetX = ExpressionFloatLineEdit(self)
        self._widgetY = ExpressionFloatLineEdit(self)
        self._widgetZ = ExpressionFloatLineEdit(self)
        self._layout.addWidget(self._widgetX)
        self._layout.addWidget(self._widgetY)
        self._layout.addWidget(self._widgetZ)
        self._layout.setMargin(0)
        self.setLayout(self._layout)
        self._widgetX.valueChanged.connect(self._onValueChanged)
        self._widgetY.valueChanged.connect(self._onValueChanged)
        self._widgetZ.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onValueChanged(self, _):
        self._attr.Set(self.value())

    def value(self):
        return Gf.Vec3f(
            self._widgetX.value(), self._widgetY.value(), self._widgetZ.value()
        )

    def setValue(self, value):
        with SignalBlocker(self._widgetX):
            self._widgetX.setValue(value[0])
        with SignalBlocker(self._widgetY):
            self._widgetY.setValue(value[1])
        with SignalBlocker(self._widgetZ):
            self._widgetZ.setValue(value[2])

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setValue(self._attr.Get(currentTime))
