from pathlib import Path

from pxr import Sdf, UsdUtils
from PySide2.QtGui import QIcon
from PySide2.QtCore import QEvent
from PySide2.QtWidgets import (
    QMainWindow,
    QScrollArea,
    QFileDialog,
    QPushButton,
    QFormLayout,
    QStyle,
)

from . import KeyValueWidget


class SimpleEditWindow(QMainWindow):
    def __init__(self, parent=None, *args, usdviewApi, **kwargs):
        super().__init__(*args, **kwargs)

        self.__scroll = QScrollArea(self)
        self.__scroll.setWidgetResizable(True)
        self.setCentralWidget(self.__scroll)

        self.__layout = QFormLayout(self.__scroll)
        self.__save_as_button = QPushButton("Save as")
        self.__save_as_button.setIcon(
            QIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        )
        self.__save_as_button.clicked.connect(self.handler_SaveAs)
        self.__layout.addRow("Save as", self.__save_as_button)

        self.__widget = KeyValueWidget.KeyValueWidget(self)
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

    def handler_SaveAs(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save as",
            str(Path(self.__api.stage.GetLayerStack()[-1].realPath).parent),
            "USD File (*.usd *.usda)",
        )

        # copied from
        # https://github.com/PixarAnimationStudios/OpenUSD/blob/0b18ad3f840c24eb25e16b795a5b0821cf05126e/pxr/usdImaging/usdviewq/appController.py#L2834
        rootLayer = self.__api.dataModel.stage.GetRootLayer()
        self.__api.dataModel.stage.GetSessionLayer().Export(
            filename, "Simple Editor, save program is almost UsdView"
        )
        targetLayer = Sdf.Layer.FindOrOpen(filename)
        UsdUtils.CopyLayerMetadata(rootLayer, targetLayer, skipSublayers=True)

        # We don't ever store self.realStartTimeCode or
        # self.realEndTimeCode in a layer, so we need to author them
        # here explicitly.
        if self.__api.stage.HasAuthoredMetadata("startTimeCode"):
            targetLayer.startTimeCode = self.__api.stage.GetStartTimeCode()
        if self.__api.stage.HasAuthoredMetadata("endTimeCode"):
            targetLayer.endTimeCode = self.__api.stage.GetEndTimeCode()

        targetLayer.subLayerPaths.append(
            self.__api.dataModel.stage.GetRootLayer().realPath
        )
        targetLayer.RemoveInertSceneDescription()
        targetLayer.Save()
