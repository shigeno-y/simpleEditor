from PySide2.QtWidgets import (
    QLineEdit,
)

from simpleEditor.edit.PropertyEditWidgets import SignalBlocker


class AssetWidget(QLineEdit):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.textChanged.connect(self._onTextChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onTextChanged(self, text):
        self._attr.Set(text)

    def sync(self, currentTime):
        with SignalBlocker(self):
            attrVal = self._attr.Get()
            if attrVal is not None and hasattr(attrVal, "resolvedPath"):
                self.setText(attrVal.resolvedPath)
