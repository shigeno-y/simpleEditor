from pxr import UsdGeom, Sdf
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
    QFrame,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from .SignalBlocker import SignalBlocker
from .AddXformOpDialog import AddXformOpDialog
from simpleEditor.edit.resources.icons import getIcon


class XformOpWidget(QWidget):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QFrame#xopsWidget { border: 1px solid #888888; border-radius: 2px; }
            QToolButton { border: none; border-radius: 0; margin: 0; padding: 0; }
        """
        )
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(QVBoxLayout())
        self.layout().setMargin(0)
        self._rootWidget = None
        self._layout = None
        self._addButton = QPushButton()
        self._addButton.setIcon(getIcon("Plus"))
        self._addButton.clicked.connect(self._addXformOp)
        self._currentTime = currentTime
        self._attr = attr
        self._xform = UsdGeom.Xformable(self._attr.GetPrim())
        self._ops = list()
        self._opsDirty = True
        self.sync(self._currentTime)

    def sync(self, currentTime):
        from simpleEditor.edit.AttributeWidget import AttributeWidget

        if self._opsDirty:
            self.layout().takeAt(0)
            if self._rootWidget:
                self._rootWidget.deleteLater()
            self._rootWidget = QFrame()
            self._rootWidget.setObjectName("xopsWidget")
            self._layout = QGridLayout()
            self._layout.setHorizontalSpacing(4)
            self._layout.setVerticalSpacing(4)
            self._rootWidget.setLayout(self._layout)
            self._ops.clear()
            ops = self._xform.GetOrderedXformOps()
            rowCount = len(ops)
            for row, op in enumerate(ops):
                opAttr = op.GetAttr()
                label = QLabel()
                labelText = op.GetOpName().split(":", 2)[1]
                if op.IsInverseOp():
                    labelText = "[INV]" + labelText
                label.setText(labelText)
                fwdButton = QToolButton(self._rootWidget)
                fwdButton.setIcon(getIcon("UpArrow"))
                fwdButton.setVisible(row > 0)
                fwdButton.clicked.connect(lambda *, r=row, f=-1: self._moveOp(r, f))
                backButton = QToolButton(self._rootWidget)
                backButton.setIcon(getIcon("DownArrow"))
                backButton.setVisible(row < (rowCount - 1))
                backButton.clicked.connect(lambda *, r=row, f=1: self._moveOp(r, f))
                removeButton = QToolButton(self._rootWidget)
                removeButton.setIcon(getIcon("Cross"))
                removeButton.clicked.connect(lambda *, r=row: self._removeOp(r))
                opWidget = AttributeWidget(opAttr, currentTime, self._rootWidget)
                if hasattr(opWidget.getWidget(), "valueChanged"):
                    opWidget.getWidget().valueChanged.connect(self._resync)
                self._layout.addWidget(fwdButton, row, 0)
                self._layout.addWidget(backButton, row, 1)
                self._layout.addWidget(label, row, 2, Qt.AlignVCenter | Qt.AlignRight)
                self._layout.addWidget(opWidget, row, 3)
                self._layout.addWidget(removeButton, row, 4)
                self._ops.append((op, opWidget, fwdButton, backButton, label, removeButton))
            self._layout.addWidget(self._addButton, rowCount, 2)
            self._layout.setColumnStretch(3, 1)
            self.layout().addWidget(self._rootWidget)
            self._opsDirty = False
        else:
            for op in self._ops:
                op[1].getWidget().sync(currentTime)
        self._currentTime = currentTime

    def _addXformOp(self):
        if AddXformOpDialog.addXformOp(self._addButton, self._xform):
            self._opsDirty = True
            self.sync(self._currentTime)

    def _moveOp(self, row, f):
        ops = list(self._xform.GetXformOpOrderAttr().Get())
        dst = row + f
        ops[row], ops[dst] = ops[dst], ops[row]
        self._attr.Set(ops)
        self._opsDirty = True
        self.sync(self._currentTime)

    def _removeOp(self, row):
        ops = list(self._attr.Get())
        del ops[row]
        self._attr.Set(ops)
        self._opsDirty = True
        self.sync(self._currentTime)

    def _resync(self):
        self.sync(self._currentTime)
