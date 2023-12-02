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


class SignalBlocker:
    """QSignalBlocker を with 句で使用するためのラッパ."""

    def __init__(self, widget):
        self._blocker = None
        self._widget = widget

    def __enter__(self):
        self._blocker = QSignalBlocker(self._widget)

    def __exit__(self, *_):
        del self._blocker


class ExpressionFloatValidator(QDoubleValidator):
    """数値, もしくは式を受け付ける小数バリデータ."""

    pass  # TODO:


class ExpressionIntValidator(QIntValidator):
    """数値, もしくは式を受け付ける整数バリデータ."""

    pass  # TODO:


class ExpressionFloatLineEdit(QLineEdit):
    """数値, もしくは式を受け付ける小数値ウィジット.
    加えて, マウスのドラッグで値が増えたり減ったりする.
    """

    valueChanged = Signal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = 0.0
        self._validator = ExpressionFloatValidator(self)
        self._pressedPosition = None
        self._pressedValue = None
        self._changeValueBias = None
        self.setValidator(self._validator)
        self.setText("0.000")
        self.editingFinished.connect(self._onEditingFinished)

    def _onEditingFinished(self):
        self.setValue(float(self.text()))

    def mousePressEvent(self, ev):
        if ev.buttons() == Qt.LeftButton and ev.modifiers() & Qt.ControlModifier:
            self._pressedPosition = ev.pos()
            self._pressedValue = self._value
            if ev.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
                self._changeValueBias = 10.0
            else:
                self._changeValueBias = 0.05
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
            self.setValue(self._pressedValue + diff * self._changeValueBias)
            ev.accept()
        else:
            super().mouseMoveEvent(ev)

    def wheelEvent(self, ev):
        if self.hasFocus():
            addv = float(ev.angleDelta().y()) / 120.0
            if ev.modifiers() == Qt.ShiftModifier:
                addv *= 10.0
            else:
                addv *= 0.05
            self.setValue(self._value + addv)
            ev.accept()
        else:
            super().wheelEvent(ev)

    def value(self) -> float:
        return self._value

    def setValue(self, value: float):
        self._value = float(value)
        with SignalBlocker(self):
            self.setText(f"{self._value:.03f}")
        self.valueChanged.emit(self._value)


class ExpressionIntLineEdit(QLineEdit):
    """数値, もしくは式を受け付ける整数値ウィジット.
    加えて, マウスのドラッグで値が増えたり減ったりする.
    """

    valueChanged = Signal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = 0.0
        self._validator = ExpressionIntValidator(self)
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
            self.setValue(self._pressedValue + diff * self._changeValueBias)
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
            self.setValue(self._value + addv)
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


class StringWidget(QLineEdit):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.textChanged.connect(self._onTextChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onTextChanged(self, text):
        self._attr.Set(text)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setText(self._attr.Get(currentTime))


class TokenWidget(QComboBox):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._attr = attr
        if attr.HasMetadata("allowedTokens"):
            allowedTokens = attr.GetMetadata("allowedTokens")
            for at in allowedTokens:
                self.addItem(at)
        else:
            self.setEditable(True)
        self.currentTextChanged.connect(self._onCurrentTextChanged)
        self.sync(currentTime)

    def _onCurrentTextChanged(self, text):
        self._attr.Set(text)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setCurrentText(self._attr.Get(currentTime))


class BoolWidget(QCheckBox):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.toggled.connect(self._onToggled)
        self._attr = attr
        self.setText(attr.GetBaseName())
        self.sync(currentTime)

    def _onToggled(self, flag):
        self._attr.Set(flag)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setChecked(self._attr.Get(currentTime) is True)

    def labelText(self):
        return ""


class FloatWidget(ExpressionFloatLineEdit):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onValueChanged(self, value):
        self._attr.Set(value)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setValue(self._attr.Get(currentTime))


class Float2Widget(QWidget):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._widgetX = ExpressionFloatLineEdit(self)
        self._widgetY = ExpressionFloatLineEdit(self)
        self._layout.addWidget(self._widgetX)
        self._layout.addWidget(self._widgetY)
        self._layout.setMargin(0)
        self.setLayout(self._layout)
        self._widgetX.valueChanged.connect(self._onValueChanged)
        self._widgetY.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onValueChanged(self, _):
        self._attr.Set(self.value())

    def value(self):
        return Gf.Vec2f(self._widgetX.value(), self._widgetY.value())

    def setValue(self, value):
        with SignalBlocker(self._widgetX):
            self._widgetX.setValue(value[0])
        with SignalBlocker(self._widgetY):
            self._widgetY.setValue(value[1])

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setValue(self._attr.Get(currentTime))


class Float3Widget(QWidget):
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


class Float4Widget(QWidget):
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
        self._layout.setMargin(0)
        self.setLayout(self._layout)
        self._widgetX.valueChanged.connect(self._onValueChanged)
        self._widgetY.valueChanged.connect(self._onValueChanged)
        self._widgetZ.valueChanged.connect(self._onValueChanged)
        self._widgetW.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onValueChanged(self, _):
        self._attr.Set(self.value())

    def value(self):
        return Gf.Vec4f(
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
        with SignalBlocker(self):
            self.setValue(self._attr.Get(currentTime))


class IntWidget(ExpressionIntLineEdit):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onValueChanged(self, value):
        self._attr.Set(value)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setValue(self._attr.Get(currentTime))


class UnsupportedAttributeWidget(QLabel):
    def __init__(self, _, __, parent):
        super().__init__(parent)
        self.setText("Unsupported Type.")

    def sync(self, currentTime):
        pass
