from pathlib import Path

from pxr import Sdf, UsdUtils
from PySide2.QtGui import QIcon
from PySide2.QtCore import QEvent
from PySide2.QtWidgets import (
    QMainWindow,
    QWidget,
    QScrollArea,
    QFileDialog,
    QPushButton,
    QVBoxLayout,
    QStyle,
)

from . import KeyValueWidget


class SimpleEditWindow(QMainWindow):
    def __init__(self, parent=None, *args, usdviewApi, **kwargs):
        super().__init__(*args, **kwargs)
        self.__rootWidget = QWidget(self)
        self.setCentralWidget(self.__rootWidget)
        self.__layout = QVBoxLayout(self.__rootWidget)

        self.__save_as_button = QPushButton("Save as", self.__rootWidget)
        self.__save_as_button.setIcon(
            QIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        )
        self.__save_as_button.clicked.connect(self.handler_SaveAs)
        self.__layout.addWidget(self.__save_as_button)

        self.__scroll = QScrollArea(self)
        self.__scroll.setWidgetResizable(True)
        self.__layout.addWidget(self.__scroll)

        self.__widget = KeyValueWidget.KeyValueWidget(self.__scroll)
        self.__scroll.setWidget(self.__widget)

        self.__api = usdviewApi
        self.__title = "/"

        self.__api.dataModel.selection.signalPrimSelectionChanged.connect(
            self.slotPrimSelectionChanged
        )

    def slotPrimSelectionChanged(self, newPrimPath, oldPrimPath):
        if len(newPrimPath) > 0:
            self.update(list(newPrimPath)[0])

    def update(self, newPrimPath, time=None):
        if time is None:
            time = self.__api.frame.GetValue()
        if self.__title != newPrimPath:
            self.__title = newPrimPath
            self.setWindowTitle(str(self.__title))

        prim = self.__api.stage.GetPrimAtPath(newPrimPath)
        self.__widget.update(prim, time)

    def handler_SaveAs(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save as",
            str(Path(self.__api.stage.GetLayerStack()[-1].realPath).parent),
            "USD File (*.usd *.usda)",
        )
        if not filename:
            return

        layer1 = self.__api.stage.GetSessionLayer()
        layer2 = self.__api.stage.GetRootLayer()

        flatten_layer = Sdf.Layer.CreateAnonymous()
        flatten_layer.TransferContent(layer1)

        UsdUtils.StitchLayers(flatten_layer, layer2)

        flatten_layer.subLayerPaths.clear()
        for p in layer2.subLayerPaths:
            flatten_layer.subLayerPaths.append(p)

        flatten_layer.Export(filename)
