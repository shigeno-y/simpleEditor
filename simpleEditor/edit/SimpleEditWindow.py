from pathlib import Path

from pxr import Sdf, UsdUtils
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStyle,
    QVBoxLayout,
    QWidget,
    QLineEdit,
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

        self.__remove_this_prim_button = QPushButton("Remove PrimSpec", self.__rootWidget)
        self.__remove_this_prim_button.setIcon(
            QIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        )
        self.__remove_this_prim_button.clicked.connect(self.handler_RemoveThisPrim)
        self.__layout.addWidget(self.__remove_this_prim_button)


        self.__scroll = QScrollArea(self)
        self.__scroll.setWidgetResizable(True)
        self.__layout.addWidget(self.__scroll)

        self.__widget = KeyValueWidget.KeyValueWidget(self.__scroll)
        self.__scroll.setWidget(self.__widget)

        self.__api = usdviewApi
        self.__currentTarget = "/"

        self.__api.dataModel.selection.signalPrimSelectionChanged.connect(
            self.slotPrimSelectionChanged
        )
        self.__api._UsdviewApi__appController._ui.frameSlider.valueChanged.connect(
            self.slotTimecodeChanged
        )

    def slotPrimSelectionChanged(self, newPrimPath=None, oldPrimPath=None):
        if newPrimPath is None or len(newPrimPath) < 1:
            self.update()
        else:
            self.update(list(newPrimPath)[0])

    def slotTimecodeChanged(self, newTimecode):
        self.update(self.__currentTarget, newTimecode)

    def update(self, newPrimPath=None, time=None):
        if newPrimPath is None:
            newPrimPath = self.__currentTarget
        if time is None:
            time = self.__api.frame.GetValue()
        if self.__currentTarget != newPrimPath:
            self.__currentTarget = newPrimPath
            self.setWindowTitle(str(self.__currentTarget))

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

    def handler_RemoveThisPrim(self):
        self.__api.stage.RemovePrim(self.__currentTarget)
