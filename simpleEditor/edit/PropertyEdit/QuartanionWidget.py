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

from .util import shouldSetAsTimesamples

_type2ReturnCls = {
Sdf.ValueTypeNames.Quatd: Gf.Quatd,
Sdf.ValueTypeNames.Quatf: Gf.Quatf,
Sdf.ValueTypeNames.Quath: Gf.Quath,
}

class QuartanionWidget(QWidget):
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
        self._currentTime = currentTime
        self._timesamples=None
        self.sync(currentTime)

    def _onValueChanged(self, _):
        value = self.value()

        if shouldSetAsTimesamples(self._attr):
            if self._timesamples is None:
                self._timesamples = dict()
                timecodes = self._attr.GetTimeSamples()
                for t in timecodes:
                    self._timesamples[t] = self._attr.Get(t)
            self._timesamples[self._currentTime] = self.value()
            for t, v in self._timesamples.items():
                self._attr.Set(v, t)
        else:
            self._attr.Set(value)

        r = value.GetReal()
        i = value.GetImaginary()
        self.valueChanged.emit(i[0], i[1], i[2], r)

    def value(self):
        return _type2ReturnCls[self._attr.GetTypeName()](
            self._widgetX.value(),
            self._widgetY.value(),
            self._widgetZ.value(),
            self._widgetW.value(),
        ).GetNormalized()

    def setValue(self, value):
        value = value.GetNormalized()
        r = value.GetReal()
        i = value.GetImaginary()
        with SignalBlocker(self._widgetX):
            self._widgetX.setValue(i[0])
        with SignalBlocker(self._widgetY):
            self._widgetY.setValue(i[1])
        with SignalBlocker(self._widgetZ):
            self._widgetZ.setValue(i[2])
        with SignalBlocker(self._widgetW):
            self._widgetW.setValue(r)

    def sync(self, currentTime):
        self._currentTime = currentTime
        with SignalBlocker(self):
            value = self._attr.Get(currentTime)
            if value is not None:
                self.setValue(value)
