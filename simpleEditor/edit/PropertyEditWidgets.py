from PySide2.QtWidgets import (
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
)


class SignalBlocker:
    def __init__(self, widget):
        self._blocker = None
        self._widget = widget

    def __enter__(self):
        self._blocker = SignalBlocker(self._widget)

    def __exit__(self, *_):
        del self._blocker


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


class FloatWidget(QDoubleSpinBox):
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
