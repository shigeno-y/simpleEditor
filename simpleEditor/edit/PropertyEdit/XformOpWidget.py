from pxr import UsdGeom
from PySide2.QtCore import (
    QAbstractItemModel,
    Qt,
    QModelIndex,
    QSize,
    QStringListModel,
)
from PySide2.QtGui import (
    QIcon,
    QBrush,
    QFont,
)
from PySide2.QtWidgets import (
    QAction,
    QHBoxLayout,
    QListView,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from .SignalBlocker import SignalBlocker
from .AddXformOpDialog import AddXformOpDialog


class XformOpWidget(QWidget):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._attr = attr
        self._currentTime = currentTime
        self._model = QStringListModel()
        self._layout = QHBoxLayout()
        self._listView = QListView(self)
        self._listView.setModel(self._model)
        self._cmdLayout = QVBoxLayout()
        self._addButton = QPushButton(self)
        self._forwardButton = QPushButton(self)
        self._backButton = QPushButton(self)
        self._removeButton = QPushButton(self)
        self._addButton.setText("+")
        self._forwardButton.setText("↑")
        self._backButton.setText("↓")
        self._removeButton.setText("-")
        self._cmdLayout.addWidget(self._addButton)
        self._cmdLayout.addStretch()
        self._cmdLayout.addWidget(self._forwardButton)
        self._cmdLayout.addWidget(self._backButton)
        self._cmdLayout.addStretch()
        self._cmdLayout.addWidget(self._removeButton)
        self._cmdLayout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._listView)
        self._layout.addLayout(self._cmdLayout)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self.setContentsMargins(0, 0, 0, 0)

        # signal
        self._addButton.clicked.connect(self._addXformOp)

        self.sync(currentTime)

    def sync(self, currentTime):
        self._currentTime = currentTime
        with SignalBlocker(self):
            value = self._attr.Get(currentTime)
            self._model.setStringList(value if value else list())

    def _addXformOp(self):
        if AddXformOpDialog.addXformOp(self, self._attr.GetPrim()):
            self.sync(self._currentTime)
