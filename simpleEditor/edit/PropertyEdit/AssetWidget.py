from pathlib import Path

from pxr import (
    Gf,
)
from PySide2.QtCore import (
    QSignalBlocker,
    Qt,
    Signal,
)
from PySide2.QtGui import (
    QColor,
    # QValidator,      # TEMP: Expression を実装するときに使用する.
    QDoubleValidator,  # TEMP: Expression を実装したら使用しなくなる.
    QIcon,
    QImage,
    QIntValidator,  # TEMP: Expression を実装したら使用しなくなる.
    QPainter,
    QPixmap,
)
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
    QWidget,
)

from simpleEditor.edit.PropertyEditWidgets import SignalBlocker


class AssetWidget(QWidget):
    def __init__(self, attr, currentTime, parent):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._openAsset = QPushButton("", self)
        self._openAsset.setIcon(QIcon(self.style().standardIcon(QStyle.SP_ArrowForward)))
        self._openAsset.clicked.connect(self.handlerAssetPicker)
        self._assetPath = QLineEdit(self)
        self._layout.addWidget(self._openAsset)
        self._layout.addWidget(self._assetPath)
        self._layout.setMargin(0)

        self.setLayout(self._layout)
        self._assetPath.textChanged.connect(self._onTextChanged)
        self._attr = attr
        self._copiedFromBase = False
        self._currentTime = currentTime
        self.sync(self._currentTime)

    def _onTextChanged(self, text):
        self._attr.Set(text)

    def sync(self, currentTime):
        with SignalBlocker(self):
            attrVal = self._attr.Get()
            if attrVal is not None and hasattr(attrVal, "path"):
                self._assetPath.setText(attrVal.path)

    def handlerAssetPicker(self):
        attrVal = self._attr.Get()
        base_path = Path(self._attr.GetStage().GetLayerStack()[1].realPath).parent
        default_path = None
        if attrVal is not None and hasattr(attrVal, "resolvedPath"):
            default_path = Path(attrVal.resolvedPath).parent

        filename, _ = QFileDialog.getOpenFileName(
            self, "Select asset", str(default_path if default_path else base_path)
        )
        if not filename:
            return

        target = Path(filename).relative_to(base_path).as_posix()

        self._assetPath.setText(target)
        self._onTextChanged(target)
