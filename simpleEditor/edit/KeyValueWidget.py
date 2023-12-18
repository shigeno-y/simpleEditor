from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from . import AttributeWidget


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
                for _ in range(self.layout().count()):
                    self.layout().takeAt(0)
                self._widget.deleteLater()
            self._widget = QWidget(self)
            self._layout = QFormLayout(self._widget)
            self._layout.setLabelAlignment(Qt.AlignRight)
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
                    label.setMinimumHeight(38)
                    label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
                    label.setStyleSheet(
                        "border: none; border-bottom: 1px solid #666666;"
                    )
                    label.setFont(bold_font)
                    self._layout.addRow(label)
                    currentNamespace = namespace

                attrWidget = AttributeWidget.AttributeWidget(
                    attr, currentTime, self._widget
                )
                baseName = attrWidget.labelText(baseName)
                self._layout.addRow(baseName, attrWidget)
                self._uiWidgets.append(attrWidget)

            self.layout().addWidget(self._widget)
            self.layout().addStretch(1)

        else:
            for w in self._uiWidgets:
                w.setCurrentTime(currentTime)
