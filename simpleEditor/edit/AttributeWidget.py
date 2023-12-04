from pxr import Sdf
from PySide2.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QToolButton,
    QMenu,
    QAction,
)

from .PropertyEditWidgets import (
    StringWidget,
    TokenWidget,
    BoolWidget,
    FloatWidget,
    Float2Widget,
    Float3Widget,
    Float4Widget,
    IntWidget,
    UnsupportedAttributeWidget,
)

_type2widget = {
    Sdf.ValueTypeNames.Float: FloatWidget,
    Sdf.ValueTypeNames.Float2: Float2Widget,
    Sdf.ValueTypeNames.Float3: Float3Widget,
    Sdf.ValueTypeNames.Float4: Float4Widget,
    Sdf.ValueTypeNames.Int: IntWidget,
    Sdf.ValueTypeNames.String: StringWidget,
    Sdf.ValueTypeNames.Token: TokenWidget,
    Sdf.ValueTypeNames.Bool: BoolWidget,
    Sdf.ValueTypeNames.Color3f: Float3Widget,
}


class AttributeWidget(QWidget):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._attr = attr
        self._currentTime = currentTime
        widgetClass = _type2widget.get(attr.GetTypeName(), UnsupportedAttributeWidget)
        self._widget = widgetClass(attr, currentTime, self)
        self._optionButton = QToolButton(self)
        self._optionButton.setText("...")

        self._menu = QMenu(self._optionButton)
        self._clearAction1 = QAction("Clear Default Value and All TimeSamples.")
        self._clearAction1.triggered.connect(self._clearAll)
        self._clearAction2 = QAction("Clear Current TimeSampled Value.")
        self._clearAction2.triggered.connect(self._clear)
        self._blockAction = QAction("Block Value")
        self._blockAction.triggered.connect(self._block)
        self._menu.addAction(self._clearAction1)
        self._menu.addAction(self._clearAction2)
        self._menu.addAction(self._blockAction)
        self._optionButton.setMenu(self._menu)
        self._optionButton.clicked.connect(self._optionButton.showMenu)

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(QHBoxLayout(self))
        self.layout().setMargin(0)
        self.layout().addWidget(self._optionButton)
        self.layout().addWidget(self._widget)

    def _clear(self):
        self._attr.ClearAtTime(self._currentTime)
        self._widget.sync(self._currentTime)

    def _clearAll(self):
        self._attr.Clear()
        self._widget.sync(self._currentTime)

    def _block(self):
        self._attr.Block()
        self._widget.sync(self._currentTime)

    def setCurrentTime(self, currentTime):
        self._currentTime = currentTime
        self._widget.sync(self._currentTime)

    def labelText(self, defaultValue):
        return (
            self._widget.labelText()
            if hasattr(self._widget, "labelText")
            else defaultValue
        )
