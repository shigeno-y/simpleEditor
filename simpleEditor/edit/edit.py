from pxr import Sdf
from PySide2.QtCore import QEvent
from PySide2.QtWidgets import (
    QFormLayout,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
    QToolButton,
    QMenu,
    QAction,
    QMainWindow,
    QScrollArea,
)


class SignalBlocker:
    def __init__(self, widget):
        self._blocker = None
        self._widget = widget

    def __enter__(self):
        self._blocker = SignalBlocker(self._widget)

    def __exit__(self, *_):
        del self._blocker


class StringWidget(QLineEdit):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.textChanged.connect(self._onTextChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onTextChanged(self, text):
        self._attr.Set(text)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setText(self._attr.Get(currentTime))


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


class BoolWidget(QCheckBox):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.toggled.connect(self._onToggled)
        self._attr = attr
        self.setText(attr.GetBaseName())
        self.sync(currentTime)

    def _onToggled(self, flag):
        self._attr.Set(flag)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setChecked(self._attr.Get(currentTime) is True)

    def labelText(self):
        return ""


class FloatWidget(QDoubleSpinBox):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.valueChanged.connect(self._onValueChanged)
        self._attr = attr
        self.sync(currentTime)

    def _onValueChanged(self, value):
        self._attr.Set(value)

    def sync(self, currentTime):
        with SignalBlocker(self):
            self.setValue(self._attr.Get(currentTime))


class UnsupportedAttributeWidget(QLabel):
    def __init__(self, _, __, parent):
        super().__init__(parent)
        self.setText("Unsupported Type.")


_type2widget = {
    Sdf.ValueTypeNames.Float: FloatWidget,
    # Sdf.ValueTypeNames.Float2: WidgetFloat2,
    # Sdf.ValueTypeNames.Float3: WidgetFloat3,
    # Sdf.ValueTypeNames.Float4: WidgetFloat4,
    # Sdf.ValueTypeNames.Int: QSpinBox,
    Sdf.ValueTypeNames.String: StringWidget,
    Sdf.ValueTypeNames.Token: TokenWidget,
    Sdf.ValueTypeNames.Bool: BoolWidget,
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


class KeyValueWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self._widget = None
        self._uiWidgets = None
        self._layout = None
        self._currentPrim = None

    def update(self, prim, currentTime):
        if self._currentPrim is None or self._currentPrim != prim.GetPath():
            self._currentPrim = prim.GetPath()
            if self._widget is not None:
                self.layout().takeAt(0)
                self._widget.deleteLater()
            self._widget = QWidget(self)
            self._layout = QFormLayout(self._widget)
            self._uiWidgets = list()

            bold_font = self.font()
            bold_font.setBold(True)

            attrs = prim.GetAttributes()
            attrs.sort(
                key=lambda attr: f"{len(attr.GetName().split(':'))}{attr.GetName()}"
            )
            currentNamespace = ""
            for attr in attrs:
                namespace = attr.GetNamespace()
                baseName = attr.GetBaseName()
                if namespace != currentNamespace:
                    label = QLabel(namespace, self._widget)
                    label.setStyleSheet("border: none; border-bottom: 1px solid black;")
                    label.setFont(bold_font)
                    self._layout.addRow(label)
                    currentNamespace = namespace

                attrWidget = AttributeWidget(attr, currentTime, self._widget)
                baseName = attrWidget.labelText(baseName)
                self._layout.addRow(baseName, attrWidget)
                self._uiWidgets.append(attrWidget)

            self.layout().addWidget(self._widget)

        else:
            for w in self._uiWidgets:
                w.setCurrentTime(currentTime)


class SimpleEditWindow(QMainWindow):
    def __init__(self, parent=None, *args, usdviewApi, **kwargs):
        super().__init__(*args, **kwargs)

        self.__scroll = QScrollArea(self)
        self.__scroll.setWidgetResizable(True)
        self.setCentralWidget(self.__scroll)

        self.__widget = KeyValueWidget(self)
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


__window = None


def edit(usdviewApi):
    global __window
    if __window is None:
        __window = SimpleEditWindow(usdviewApi=usdviewApi)
    __window.show()
    __window.update(usdviewApi.prim, usdviewApi.frame.GetValue())
