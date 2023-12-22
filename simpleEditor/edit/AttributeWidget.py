from pxr import Gf, Sdf, UsdGeom
from PySide2.QtWidgets import (
    QAction,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QStackedWidget,
    QToolButton,
    QWidget,
)

from .PropertyEdit import (
    AssetWidget,
    BoolWidget,
    ColorPickerWidget,
    FloatWidget,
    Float2Widget,
    Float3Widget,
    Float4Widget,
    IntWidget,
    StringWidget,
    TokenWidget,
    UnsupportedAttributeWidget,
    XformOpWidget,
)

_type2widget = {
    Sdf.ValueTypeNames.Asset: AssetWidget,
    Sdf.ValueTypeNames.Float: FloatWidget,
    Sdf.ValueTypeNames.Float2: Float2Widget,
    Sdf.ValueTypeNames.Float3: Float3Widget,
    Sdf.ValueTypeNames.Float4: Float4Widget,
    Sdf.ValueTypeNames.Double: FloatWidget,
    Sdf.ValueTypeNames.Double2: Float2Widget,
    Sdf.ValueTypeNames.Double3: Float3Widget,
    Sdf.ValueTypeNames.Double4: Float4Widget,
    Sdf.ValueTypeNames.Int: IntWidget,
    Sdf.ValueTypeNames.String: StringWidget,
    Sdf.ValueTypeNames.Token: TokenWidget,
    Sdf.ValueTypeNames.Bool: BoolWidget,
    Sdf.ValueTypeNames.Color3f: ColorPickerWidget,
}

_type2defaultValue = {
    Sdf.ValueTypeNames.Asset: Sdf.AssetPath(),
    Sdf.ValueTypeNames.Float: 0.0,
    Sdf.ValueTypeNames.Float2: Gf.Vec2f(),
    Sdf.ValueTypeNames.Float3: Gf.Vec3f(),
    Sdf.ValueTypeNames.Float4: Gf.Vec4f(),
    Sdf.ValueTypeNames.Double: 0.0,
    Sdf.ValueTypeNames.Double2: Gf.Vec2d(),
    Sdf.ValueTypeNames.Double3: Gf.Vec3d(),
    Sdf.ValueTypeNames.Double4: Gf.Vec4d(),
    Sdf.ValueTypeNames.Int: 0,
    Sdf.ValueTypeNames.String: "",
    Sdf.ValueTypeNames.Token: "",
    Sdf.ValueTypeNames.Bool: False,
    Sdf.ValueTypeNames.Color3f: Gf.Vec3f(),
    Sdf.ValueTypeNames.TokenArray: list(),
}


class AttributeWidget(QWidget):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._attr = attr
        self._currentTime = currentTime
        self._stackedWidget = QStackedWidget(self)
        self._stackedWidget.setContentsMargins(0, 0, 0, 0)

        # Unauthored Widget
        self._unauthoredWidget = QPushButton(self._stackedWidget)
        self._unauthoredWidget.setText("None")
        self._unauthoredWidget.setStyleSheet("text-align: left;")
        if self._attr.GetTypeName() not in _type2defaultValue:
            self._unauthoredWidget.setEnabled(False)
            self._unauthoredWidget.setText("None (Unsupported Type.)")
        self._unauthoredWidget.clicked.connect(self._authorDefaultValue)
        self._stackedWidget.addWidget(self._unauthoredWidget)

        # Editor Widget
        widgetClass = None
        if attr.GetPrim().IsA(UsdGeom.Xformable) and UsdGeom.Xformable(attr.GetPrim()).GetXformOpOrderAttr() == attr:
            # xformOpOrder の特殊対応
            widgetClass = XformOpWidget
        else:
            widgetClass = _type2widget.get(attr.GetTypeName(), UnsupportedAttributeWidget)
        self._widget = widgetClass(attr, currentTime, self._stackedWidget)
        self._stackedWidget.addWidget(self._widget)
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
        self.layout().addWidget(self._stackedWidget)

        self._sync()

    def _clear(self):
        self._attr.ClearAtTime(self._currentTime)
        self._sync()

    def _clearAll(self):
        self._attr.Clear()
        self._sync()

    def _block(self):
        self._attr.Block()
        self._sync()

    def _authorDefaultValue(self):
        defaultValue = _type2defaultValue.get(self._attr.GetTypeName(), None)
        if defaultValue is not None:
            self._attr.Set(defaultValue)
            self._sync()

    def _sync(self):
        if self._attr.Get(self._currentTime) is not None:
            self._widget.sync(self._currentTime)
            self._stackedWidget.setCurrentWidget(self._widget)
        else:
            self._stackedWidget.setCurrentWidget(self._unauthoredWidget)

    def getWidget(self):
        return self._widget

    def setCurrentTime(self, currentTime):
        self._currentTime = currentTime
        self._sync()

    def labelText(self, defaultValue):
        return self._widget.labelText() if hasattr(self._widget, "labelText") else defaultValue
