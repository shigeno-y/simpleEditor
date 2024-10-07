# SPDX-License-Identifier: Apache-2.0


from PySide6.QtWidgets import QLabel


class UnsupportedAttributeWidget(QLabel):
    def __init__(self, _, __, parent):
        super().__init__(parent)
        self.setText("Unsupported Type.")

    def sync(self, currentTime):
        pass
