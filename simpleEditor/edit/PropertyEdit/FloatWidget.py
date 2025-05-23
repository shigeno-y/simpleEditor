# SPDX-License-Identifier: Apache-2.0


from pxr import (
    Gf,
    Sdf,
)
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QWidget,
)

from .ExpressionFloatLineEdit import ExpressionFloatLineEdit
from .SignalBlocker import SignalBlocker

from .util import updateValue

_type2ReturnCls = {
    Sdf.ValueTypeNames.Double2: Gf.Vec2d,
    Sdf.ValueTypeNames.Double3: Gf.Vec3d,
    Sdf.ValueTypeNames.Double4: Gf.Vec4d,
    Sdf.ValueTypeNames.Float2: Gf.Vec2f,
    Sdf.ValueTypeNames.Float3: Gf.Vec3f,
    Sdf.ValueTypeNames.Float4: Gf.Vec4f,
}


class FloatWidget(ExpressionFloatLineEdit):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self._do_copy = True
        self._currentTime = currentTime
        self.sync(currentTime)

    def _onValueChanged(self, _):
        value = self.value()
        updateValue(self._attr, value, self._currentTime, self._do_copy)
        self._do_copy = False

    def sync(self, currentTime):
        self._currentTime = currentTime
        with SignalBlocker(self):
            value = self._attr.Get(currentTime)
            if value is not None:
                self.setValue(value)


class Float2Widget(QWidget):
    valueChanged = Signal(float, float)

    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._widgetX = ExpressionFloatLineEdit(self)
        self._widgetY = ExpressionFloatLineEdit(self)
        self._layout.addWidget(self._widgetX)
        self._layout.addWidget(self._widgetY)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self._widgetX.valueChanged.connect(self._onValueChanged)
        self._widgetY.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self._do_copy = True
        self._currentTime = currentTime
        self.sync(currentTime)

    def _onValueChanged(self, _):
        value = self.value()
        updateValue(self._attr, value, self._currentTime, self._do_copy)
        self.valueChanged.emit(value[0], value[1])

    def value(self):
        return _type2ReturnCls[self._attr.GetTypeName()](
            self._widgetX.value(), self._widgetY.value()
        )

    def setValue(self, value):
        with SignalBlocker(self._widgetX):
            self._widgetX.setValue(value[0])
        with SignalBlocker(self._widgetY):
            self._widgetY.setValue(value[1])

    def sync(self, currentTime):
        self._currentTime = currentTime
        with SignalBlocker(self):
            value = self._attr.Get(currentTime)
            if value is not None:
                self.setValue(value)


class Float3Widget(QWidget):
    valueChanged = Signal(float, float, float)

    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._widgetX = ExpressionFloatLineEdit(self)
        self._widgetY = ExpressionFloatLineEdit(self)
        self._widgetZ = ExpressionFloatLineEdit(self)
        self._layout.addWidget(self._widgetX)
        self._layout.addWidget(self._widgetY)
        self._layout.addWidget(self._widgetZ)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self._widgetX.valueChanged.connect(self._onValueChanged)
        self._widgetY.valueChanged.connect(self._onValueChanged)
        self._widgetZ.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self._do_copy = True
        self._currentTime = currentTime
        self.sync(currentTime)

    def _onValueChanged(self, _):
        value = self.value()
        updateValue(self._attr, value, self._currentTime, self._do_copy)
        self.valueChanged.emit(value[0], value[1], value[2])

    def value(self):
        return _type2ReturnCls[self._attr.GetTypeName()](
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
        self._currentTime = currentTime
        with SignalBlocker(self):
            value = self._attr.Get(currentTime)
            if value is not None:
                self.setValue(value)


class Float4Widget(QWidget):
    valueChanged = Signal(float, float, float, float)

    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._widgetX = ExpressionFloatLineEdit(self)
        self._widgetY = ExpressionFloatLineEdit(self)
        self._widgetZ = ExpressionFloatLineEdit(self)
        self._widgetW = ExpressionFloatLineEdit(self)
        self._layout.addWidget(self._widgetX)
        self._layout.addWidget(self._widgetY)
        self._layout.addWidget(self._widgetZ)
        self._layout.addWidget(self._widgetW)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self._widgetX.valueChanged.connect(self._onValueChanged)
        self._widgetY.valueChanged.connect(self._onValueChanged)
        self._widgetZ.valueChanged.connect(self._onValueChanged)
        self._widgetW.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self._do_copy = True
        self._currentTime = currentTime
        self.sync(currentTime)

    def _onValueChanged(self, _):
        value = self.value()
        updateValue(self._attr, value, self._currentTime, self._do_copy)
        self.valueChanged.emit(value[0], value[1], value[2], value[3])

    def value(self):
        return _type2ReturnCls[self._attr.GetTypeName()](
            self._widgetX.value(),
            self._widgetY.value(),
            self._widgetZ.value(),
            self._widgetW.value(),
        )

    def setValue(self, value):
        with SignalBlocker(self._widgetX):
            self._widgetX.setValue(value[0])
        with SignalBlocker(self._widgetY):
            self._widgetY.setValue(value[1])
        with SignalBlocker(self._widgetZ):
            self._widgetZ.setValue(value[2])
        with SignalBlocker(self._widgetW):
            self._widgetW.setValue(value[3])

    def sync(self, currentTime):
        self._currentTime = currentTime
        with SignalBlocker(self):
            value = self._attr.Get(currentTime)
            if value is not None:
                self.setValue(value)
