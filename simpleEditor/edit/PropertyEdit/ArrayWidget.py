# SPDX-License-Identifier: Apache-2.0


from pxr import Sdf
from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QTableView,
    QWidget,
)

_valueStringifiers = {
    Sdf.ValueTypeNames.AssetArray: lambda v: v.path,
    Sdf.ValueTypeNames.StringArray: str,
    Sdf.ValueTypeNames.TokenArray: str,
    Sdf.ValueTypeNames.BoolArray: lambda v: "True" if v else "False",
    Sdf.ValueTypeNames.IntArray: str,
    Sdf.ValueTypeNames.Int64Array: str,
    Sdf.ValueTypeNames.FloatArray: lambda v: f"{v:.3f}",
    Sdf.ValueTypeNames.Float2Array: lambda v: f"({v[0]:.3f}, {v[1]:.3f})",
    Sdf.ValueTypeNames.Float3Array: lambda v: f"({v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f})",
    Sdf.ValueTypeNames.Float4Array: lambda v: f"({v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f}, {v[3]:.3f})",
    Sdf.ValueTypeNames.DoubleArray: lambda v: f"{v:.3f}",
    Sdf.ValueTypeNames.Double2Array: lambda v: f"({v[0]:.3f}, {v[1]:.3f})",
    Sdf.ValueTypeNames.Double3Array: lambda v: f"({v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f})",
    Sdf.ValueTypeNames.Double4Array: lambda v: f"({v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f}, {v[3]:.3f})",
}


class ArrayValueTableModel(QAbstractTableModel):
    def __init__(self, parent, attr, currentTime):
        super().__init__(parent)
        self._attr = attr
        self._stringifier = _valueStringifiers.get(self._attr.GetTypeName(), str)
        self._currentTime = currentTime
        self._values = list()

    def updateTime(self, currentTime):
        self._currentTime = currentTime
        self.beginResetModel()
        self._values = self._attr.Get(self._currentTime)
        self.endResetModel()

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self._values) + 1
        else:
            return 0

    def columnCount(self, parent):
        if not parent.isValid():
            return 1
        else:
            return 0

    def data(self, index, role):
        if index.column() == 0:
            row = index.row()
            if row < len(self._values):
                if role == Qt.DisplayRole:
                    return self._stringifier(self._values[row])
                if role == Qt.UserRole:
                    return self._values[row]
            else:
                if role == Qt.DisplayRole:
                    return "- Append Here -"
                if role == Qt.ForegroundRole:
                    return QBrush(QColor(150, 150, 150))

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return "Value"
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            if section < len(self._values):
                return f"[{section}]"
            else:
                return ""

    def flags(self, index):
        if index.isValid():
            if index.column() == 0:
                return (
                    Qt.ItemIsSelectable
                    | Qt.ItemIsEditable
                    | Qt.ItemIsEnabled
                    | Qt.ItemNeverHasChildren
                )
        return Qt.NoItemFlags

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole and index.column() == 0:
            pass
        return False


class ArrayWidget(QTableView):
    def __init__(self, attr, currentTime, parent, scalarWidgetClass):
        super().__init__(parent)
        self._scalarWidgetClass = scalarWidgetClass
        self._model = ArrayValueTableModel(parent, attr, currentTime)
        self.setModel(self._model)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(20)
        self.verticalHeader().setMinimumSectionSize(20)
        self.setStyleSheet(
            """
            QHeaderView::section { padding: 0; }
        """
        )

    def sync(self, currentTime):
        self._model.updateTime(currentTime)
