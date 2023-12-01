from PySide2.QtCore import QEvent
from PySide2.QtWidgets import (
    QMainWindow,
    QScrollArea,
)

from . import KeyValueWidget


class SimpleEditWindow(QMainWindow):
    def __init__(self, parent=None, *args, usdviewApi, **kwargs):
        super().__init__(*args, **kwargs)

        self.__scroll = QScrollArea(self)
        self.__scroll.setWidgetResizable(True)
        self.setCentralWidget(self.__scroll)

        self.__widget = KeyValueWidget.KeyValueWidget(self)
        self.__scroll.setWidget(self.__widget)

        self.installEventFilter(self)

        self.__api = usdviewApi
        self.__title = "Simple Editor"

    def eventFilter(self, watched, event: QEvent) -> bool:
        if event.type() == QEvent.WindowActivate:
            self.update(self.__api.prim, self.__api.frame.GetValue())
        return super().eventFilter(watched, event)

    def update(self, prim, time):
        newPrimPath = str(prim.GetPath())
        if self.__title != newPrimPath:
            self.__title = newPrimPath
            self.setWindowTitle(self.__title)
        self.__widget.update(prim, time)
