# SPDX-License-Identifier: Apache-2.0


from PySide6.QtWidgets import QLineEdit

from .SignalBlocker import SignalBlocker


class ConnectionWidget(QLineEdit):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.textChanged.connect(self._onTextChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onTextChanged(self, conns):
        print("current:", self._attr.GetConnections())
        print("new:", conns)
        # self._attr.Set(text)

    def sync(self, currentTime):
        with SignalBlocker(self):
            conns = self._attr.GetConnections()
            if len(conns) > 0:
                self.setText(str(conns[0]))
