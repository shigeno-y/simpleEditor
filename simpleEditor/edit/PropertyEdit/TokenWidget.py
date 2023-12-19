from PySide2.QtWidgets import QComboBox
from .SignalBlocker import SignalBlocker


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
