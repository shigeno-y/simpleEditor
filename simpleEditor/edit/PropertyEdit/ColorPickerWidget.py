# SPDX-License-Identifier: Apache-2.0


from pxr import Gf, Sdf
from PySide6.QtCore import (
    QSignalBlocker,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    # QValidator,      # TEMP: Expression を実装するときに使用する.
    QDoubleValidator,  # TEMP: Expression を実装したら使用しなくなる.
    QIcon,
    QImage,
    QIntValidator,  # TEMP: Expression を実装したら使用しなくなる.
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
    QWidget,
)

from .ExpressionFloatLineEdit import ExpressionFloatLineEdit
from .SignalBlocker import SignalBlocker


class ColorPickerWidget(QWidget):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._attr = attr
        self._layout = QHBoxLayout(self)
        self._openColorPicker = QPushButton("", self)
        self._openColorPicker.setIcon(
            QIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        )
        self._openColorPicker.clicked.connect(self.handlerColorPicker)

        self._widgetR = ExpressionFloatLineEdit(self)
        self._widgetG = ExpressionFloatLineEdit(self)
        self._widgetB = ExpressionFloatLineEdit(self)
        self._layout.addWidget(self._openColorPicker)
        self._layout.addWidget(self._widgetR)
        self._layout.addWidget(self._widgetG)
        self._layout.addWidget(self._widgetB)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self._widgetR.valueChanged.connect(self._onValueChanged)
        self._widgetG.valueChanged.connect(self._onValueChanged)
        self._widgetB.valueChanged.connect(self._onValueChanged)
        if self._attr.GetTypeName() == Sdf.ValueTypeNames.Color4f:
            self._widgetA = ExpressionFloatLineEdit(self)
            self._layout.addWidget(self._widgetA)
            self._widgetA.valueChanged.connect(self._onValueChanged)

        self.setLayout(self._layout)

        self._copiedFromBase = False
        self._currentTime = currentTime
        self.sync(self._currentTime)

    def _onValueChanged(self, _):
        if self._attr.IsAuthored() and self._attr.GetNumTimeSamples() > 0:
            timesamples = dict()

            if not self._copiedFromBase:
                self._copiedFromBase = True
                start = self._attr.GetStage().GetStartTimeCode()
                end = self._attr.GetStage().GetEndTimeCode()
                current = start

                while current < end:
                    # 1) If a sample exists at the desiredTime, set both upper and lower to desiredTime.
                    # 2) If samples exist surrounding, but not equal to the desiredTime, set lower and upper to the bracketing samples nearest to the desiredTime.
                    # 3) If the desiredTime is outside of the range of authored samples, clamp upper and lower to the nearest time sample.
                    # 4) If no samples exist, do not modify upper and lower and set hasTimeSamples to false.
                    range = self._attr.GetBracketingTimeSamples(current)

                    # case 4
                    if range is None:
                        break

                    # case 1
                    if current == range[0] and current == range[1]:
                        timesamples[range[1]] = self._attr.Get(range[1])

                    # case 2
                    if range[0] < current and current < range[1]:
                        timesamples[range[0]] = self._attr.Get(range[0])
                        timesamples[range[1]] = self._attr.Get(range[1])

                    # case 3, timesamples is latter than current
                    if range[0] == range[1] and current < range[0]:
                        timesamples[range[1]] = self._attr.Get(range[1])

                    # case 3, timesamples is earlier than current
                    # no more timesamples in latter
                    if range[0] == range[1] and range[1] < current:
                        break

                    current = range[1] + 0.1

            timesamples[self._currentTime] = self.value()

            for t, v in timesamples.items():
                self._attr.Set(v, t)
        else:
            self._attr.Set(self.value())

    def value(self):
        if self._attr.GetTypeName() == Sdf.ValueTypeNames.Color3f:
            return Gf.Vec3f(
                self._widgetR.value(), self._widgetG.value(), self._widgetB.value()
            )
        elif self._attr.GetTypeName() == Sdf.ValueTypeNames.Color4f:
            return Gf.Vec4f(
                self._widgetR.value(),
                self._widgetG.value(),
                self._widgetB.value(),
                self._widgetA.value(),
            )

    def setValue(self, value):
        with SignalBlocker(self._widgetR):
            self._widgetR.setValue(value[0])
        with SignalBlocker(self._widgetG):
            self._widgetG.setValue(value[1])
        with SignalBlocker(self._widgetB):
            self._widgetB.setValue(value[2])
        if self._attr.GetTypeName() == Sdf.ValueTypeNames.Color4f:
            with SignalBlocker(self._widgetA):
                self._widgetA.setValue(value[3])

    def sync(self, currentTime):
        self._currentTime = currentTime
        with SignalBlocker(self):
            val = self._attr.Get(self._currentTime)
            if val is not None:
                self.setValue(val)

    def handlerColorPicker(self):
        options = QColorDialog.ColorDialogOption()
        if self._attr.GetTypeName() == Sdf.ValueTypeNames.Color4f:
            options = QColorDialog.ColorDialogOption.ShowAlphaChannel

        c = QColorDialog.getColor(QColor.fromRgbF(*self.value()), options=options)
        if c is not None:
            cc = c.toRgb()
            if self._attr.GetTypeName() == Sdf.ValueTypeNames.Color3f:
                self.setValue(Gf.Vec3f(cc.redF(), cc.greenF(), cc.blueF()))
            elif self._attr.GetTypeName() == Sdf.ValueTypeNames.Color4f:
                self.setValue(Gf.Vec4f(cc.redF(), cc.greenF(), cc.blueF(), cc.alphaF()))

            self._onValueChanged(None)
