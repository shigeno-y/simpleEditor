# SPDX-License-Identifier: Apache-2.0


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
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
        self._primTypeWidget = None
        self._uiWidgets = None
        self._layout = None
        self._currentPrim = None
        self._currentTime = None

    def update(self, prim, currentTime, *, force=False):
        self._currentTime = currentTime
        if force or self._currentPrim is None or self._currentPrim != prim:
            self._currentPrim = prim
            if self._widget is not None:
                for _ in range(self.layout().count()):
                    self.layout().takeAt(0)
                self._widget.deleteLater()
            self._widget = QWidget(self)
            self._layout = QFormLayout(self._widget)
            self._layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._uiWidgets = list()

            self._primTypeWidget = QLineEdit(self)
            self._primTypeWidget.editingFinished.connect(self._setPrimType)
            self._primTypeWidget.setText(prim.GetTypeName())
            self._layout.addRow("Type", self._primTypeWidget)

            bold_font = self.font()
            bold_font.setBold(True)

            def sortKey(attr):
                return f"{len(attr.GetName().split(':', 1))}{attr.GetName()}"

            attrs = prim.GetAttributes()
            attrs.sort(key=sortKey)
            currentNamespace = ""
            for attr in attrs:
                words = attr.GetName().split(":", 1)
                namespace = words[0] if len(words) == 2 else ""
                baseName = words[-1]
                if namespace == "xformOp":
                    continue
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
                label = QLabel(baseName, self)
                label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
                self._layout.addRow(label, attrWidget)
                self._uiWidgets.append(attrWidget)

            self.layout().addWidget(self._widget)
            self.layout().addStretch(1)

        else:
            for w in self._uiWidgets:
                w.setCurrentTime(currentTime)

    def _setPrimType(self):
        primTypeStr = self._primTypeWidget.text()
        self._currentPrim.SetTypeName(primTypeStr)
        self.update(self._currentPrim, self._currentTime, force=True)
