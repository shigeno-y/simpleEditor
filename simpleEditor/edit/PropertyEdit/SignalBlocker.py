# SPDX-License-Identifier: Apache-2.0


from PySide2.QtCore import QSignalBlocker


class SignalBlocker:
    """QSignalBlocker を with 句で使用するためのラッパ."""

    def __init__(self, widget):
        self._blocker = None
        self._widget = widget

    def __enter__(self):
        self._blocker = QSignalBlocker(self._widget)

    def __exit__(self, *_):
        del self._blocker
