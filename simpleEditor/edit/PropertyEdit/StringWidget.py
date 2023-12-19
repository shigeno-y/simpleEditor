from PySide2.QtWidgets import QLineEdit
from .SignalBlocker import SignalBlocker


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
