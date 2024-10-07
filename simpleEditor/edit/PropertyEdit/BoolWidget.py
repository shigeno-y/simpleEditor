# SPDX-License-Identifier: Apache-2.0


from PySide6.QtWidgets import QCheckBox

from .SignalBlocker import SignalBlocker


class BoolWidget(QCheckBox):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.toggled.connect(self._onToggled)
        self._attr = attr
        self.setText(attr.GetName().split(":", 1)[-1])
        self.sync(currentTime)

    def _onToggled(self, flag):
        self._attr.Set(flag)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setChecked(self._attr.Get(currentTime) is True)

    def labelText(self):
        return ""
