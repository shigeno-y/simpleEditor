# SPDX-License-Identifier: Apache-2.0


from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtGui import (
    # QValidator,      # TEMP: Expression を実装するときに使用する.
    QIntValidator,  # TEMP: Expression を実装したら使用しなくなる.
)
from PySide6.QtWidgets import (
    QLineEdit,
)

from .SignalBlocker import SignalBlocker


class ExpressionUIntValidator(QIntValidator):
    """非負数値, もしくは式を受け付ける整数バリデータ."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBottom(0)


class ExpressionUIntLineEdit(QLineEdit):
    """数値, もしくは式を受け付ける整数値ウィジット.
    加えて, マウスのドラッグで値が増えたり減ったりする.
    """

    valueChanged = Signal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = 0.0
        self._validator = ExpressionUIntValidator(self)
        self._pressedPosition = None
        self._pressedValue = None
        self._changeValueBias = None
        self.setValidator(self._validator)
        self.setText("0")
        self.editingFinished.connect(self._onEditingFinished)

    def _onEditingFinished(self):
        self.setValue(int(self.text()))

    def mousePressEvent(self, ev):
        if ev.buttons() == Qt.LeftButton and ev.modifiers() & Qt.ControlModifier:
            self._pressedPosition = ev.pos()
            self._pressedValue = self._value
            if ev.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
                self._changeValueBias = 10
            else:
                self._changeValueBias = 1
            ev.accept()
        else:
            super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev):
        if self._pressedPosition is not None and ev.button() == Qt.LeftButton:
            self._pressedPosition = None
            self._pressedValue = None
            ev.accept()
        else:
            super().mouseReleaseEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._pressedPosition is not None:
            diff = (ev.pos() - self._pressedPosition).x()
            self.setValue(max(self._pressedValue + diff * self._changeValueBias, 0))
            ev.accept()
        else:
            super().mouseMoveEvent(ev)

    def wheelEvent(self, ev):
        if self.hasFocus():
            addv = 1
            if ev.modifiers() == Qt.ShiftModifier:
                addv = 10
            if ev.angleDelta().y() < 0:
                addv *= -1
            self.setValue(max(self._value + addv, 0))
            ev.accept()
        else:
            super().wheelEvent(ev)

    def value(self) -> int:
        return self._value

    def setValue(self, value: int):
        self._value = int(value)
        with SignalBlocker(self):
            self.setText(str(self._value))
        self.valueChanged.emit(self._value)
