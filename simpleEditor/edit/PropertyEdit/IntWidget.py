from .SignalBlocker import SignalBlocker
from .ExpressionIntLineEdit import ExpressionIntLineEdit


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
