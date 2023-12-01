from pxr import Sdf
from PySide2.QtWidgets import (
    QFormLayout,
    QWidget,
    QLabel,
    QVBoxLayout,
    QScrollArea,
    QHBoxLayout,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QMainWindow,
)

from PySide2.QtCore import QEvent


class WidgetFloat4(QWidget):
    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(QDoubleSpinBox(self))
        self.layout().addWidget(QDoubleSpinBox(self))
        self.layout().addWidget(QDoubleSpinBox(self))
        self.layout().addWidget(QDoubleSpinBox(self))


class WidgetFloat3(QWidget):
    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(QDoubleSpinBox(self))
        self.layout().addWidget(QDoubleSpinBox(self))
        self.layout().addWidget(QDoubleSpinBox(self))


class WidgetFloat2(QWidget):
    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(QDoubleSpinBox(self))
        self.layout().addWidget(QDoubleSpinBox(self))


class WidgetTokens(QComboBox):
    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

    def setAttr(self, attr):
        try:
            allowedTokens = attr.GetMetadata("allowedTokens")
            for at in allowedTokens:
                self.addItem(at)
        except Exception as e:
            print(attr)
            print(allowedTokens)
            print(e)


_type2widget = {
    Sdf.ValueTypeNames.Float: QDoubleSpinBox,
    Sdf.ValueTypeNames.Float2: WidgetFloat2,
    Sdf.ValueTypeNames.Float3: WidgetFloat3,
    Sdf.ValueTypeNames.Float4: WidgetFloat4,
    Sdf.ValueTypeNames.Int: QSpinBox,
    Sdf.ValueTypeNames.String: QLineEdit,
    Sdf.ValueTypeNames.Token: WidgetTokens,
    Sdf.ValueTypeNames.Bool: QCheckBox,
}


class KeyValueWidget(QWidget):
    def __init__(self, parent=None, *args, usdviewApi, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.__api = usdviewApi
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self._widget = None
        self._layout = None

        self.installEventFilter(self)

    def eventFilter(self, watched, event: QEvent) -> bool:
        if event.type() == QEvent.WindowActivate:
            self.setPrim(self.__api.prim)
        return super().eventFilter(watched, event)

    def setPrim(self, prim):
        if self._widget is not None:
            self.layout().takeAt(0)
            self._widget.deleteLater()
        self._widget = QWidget(self)
        self._layout = QFormLayout(self._widget)

        bold_font = self.font()
        bold_font.setBold(True)

        attrs = prim.GetAttributes()
        attrs.sort(key=lambda attr: f"{len(attr.GetName().split(':'))}{attr.GetName()}")
        currentNamespace = ""
        for attr in attrs:
            namespace = attr.GetNamespace()
            baseName = attr.GetBaseName()
            if namespace != currentNamespace:
                label = QLabel(namespace, self._widget)
                label.setFont(bold_font)
                self._layout.addRow(label)
                currentNamespace = namespace

            widgetClass = _type2widget.get(attr.GetTypeName(), QLineEdit)
            widget = widgetClass(self._widget)
            if hasattr(widget, "setAttr"):
                widget.setAttr(attr)
            elif hasattr(widget, "setValue"):
                widget.setValue(attr.Get())
            self._layout.addRow(baseName, widget)

        self.layout().addWidget(self._widget)


__window = None
__scroll = None
__widget = None


def edit(usdviewApi):
    global __window
    global __scroll
    global __widget
    if __window is None:
        __window = QMainWindow()

        __scroll = QScrollArea(__window)
        __scroll.setWidgetResizable(True)
        __window.setCentralWidget(__scroll)

        __widget = KeyValueWidget(__window, usdviewApi=usdviewApi)
        __scroll.setWidget(__widget)
    __window.show()

    if __widget is not None:
        __widget.setPrim(usdviewApi.prim)
