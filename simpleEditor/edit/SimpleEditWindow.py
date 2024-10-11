# SPDX-License-Identifier: Apache-2.0


from pathlib import Path

from pxr import Sdf, Tf, UsdUtils
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QMenu,
    QMenuBar,
    QScrollArea,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import KeyValueWidget
from .resources.icons import getIcon


class SimpleEditWindow(QDockWidget):
    def __init__(self, parent=None, *args, usdviewApi, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.__rootWidget = QWidget(self)
        self.__layout = QVBoxLayout(self.__rootWidget)
        self.__layout.setContentsMargins(6, 0, 6, 6)
        self.__layout.setSpacing(0)

        self.setWindowTitle("/")
        self.setFeatures(
            QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
        )
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFloating(True)
        self.setWidget(self.__rootWidget)
        self.setMinimumWidth(300)

        self.__menuBar = QMenuBar(self)
        # --- Menu: Stage
        self.__menuStage = QMenu(self)
        self.__menuStage.setTitle("&Stage")
        self.__actionSave = QAction("&Save", self)
        self.__actionSave.setIcon(getIcon("Save"))
        self.__actionSave.triggered.connect(self.handler_Save)
        self.__actionSave.setShortcut("Ctrl+S")
        self.__actionSaveAs = QAction("Save &As...", self)
        self.__actionSaveAs.setIcon(getIcon("SaveAs"))
        self.__actionSaveAs.triggered.connect(self.handler_SaveAs)
        self.__actionSaveAs.setShortcut("Ctrl+Shift+S")
        self.__menuStage.addAction(self.__actionSave)
        self.__menuStage.addAction(self.__actionSaveAs)
        self.__menuBar.addMenu(self.__menuStage)
        # --- Menu: Prim
        self.__menuPrim = QMenu(self)
        self.__menuPrim.setTitle("&Prim")
        self.__actionAddChildPrimSpec = QAction("&Add child PrimSpec", self)
        self.__actionAddChildPrimSpec.setIcon(getIcon("AddPrim"))
        self.__actionAddChildPrimSpec.triggered.connect(self.handler_AddChildPrim)
        self.__actionRemovePrimSpec = QAction("&Remove PrimSpec", self)
        self.__actionRemovePrimSpec.setIcon(getIcon("RemovePrim"))
        self.__actionRemovePrimSpec.triggered.connect(self.handler_RemoveThisPrim)
        self.__menuPrim.addAction(self.__actionAddChildPrimSpec)
        self.__menuPrim.addAction(self.__actionRemovePrimSpec)
        self.__menuBar.addMenu(self.__menuPrim)
        # ---
        self.__layout.addWidget(self.__menuBar)

        self.__toolBar = QToolBar(self.__rootWidget)
        self.__toolBar.setStyleSheet(
            """
            QToolButton { border: none; border-radius: 3px; padding: 3px; background: transparent; }
            QToolButton:hover { background: #303030; }
            QToolButton:pressed { background: #3F3F3F; }
        """
        )
        self.__toolBar.setIconSize(QSize(16, 16))
        self.__toolSaveButton = QToolButton(self)
        self.__toolSaveButton.setText("Save")
        self.__toolSaveButton.setIcon(getIcon("Save"))
        self.__toolSaveButton.clicked.connect(self.handler_Save)
        self.__toolSaveAsButton = QToolButton(self)
        self.__toolSaveAsButton.setText("Save As")
        self.__toolSaveAsButton.setIcon(getIcon("SaveAs"))
        self.__toolSaveAsButton.clicked.connect(self.handler_SaveAs)
        self.__toolAddChildPrimSpec = QToolButton(self)
        self.__toolAddChildPrimSpec.setText("Add Child PrimSpec")
        self.__toolAddChildPrimSpec.setIcon(getIcon("AddPrim"))
        self.__toolAddChildPrimSpec.clicked.connect(self.handler_AddChildPrim)
        self.__toolRemovePrimSpec = QToolButton(self)
        self.__toolRemovePrimSpec.setText("Remove PrimSpec")
        self.__toolRemovePrimSpec.setIcon(getIcon("RemovePrim"))
        self.__toolRemovePrimSpec.clicked.connect(self.handler_RemoveThisPrim)
        self.__toolBar.addWidget(self.__toolSaveButton)
        self.__toolBar.addWidget(self.__toolSaveAsButton)
        self.__toolBar.addSeparator()
        self.__toolBar.addWidget(self.__toolAddChildPrimSpec)
        self.__toolBar.addWidget(self.__toolRemovePrimSpec)
        self.__layout.addWidget(self.__toolBar)

        self.__scroll = QScrollArea(self)
        self.__scroll.setWidgetResizable(True)
        self.__layout.addWidget(self.__scroll)

        self.__widget = KeyValueWidget.KeyValueWidget(self.__scroll)
        self.__scroll.setWidget(self.__widget)

        self.__api = usdviewApi
        self.__currentTarget = "/"
        self.__api.stage.SetFramesPerSecond(self.__api.stage.GetTimeCodesPerSecond())

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

    def save(self, filename):
        layer1 = self.__api.stage.GetSessionLayer()
        layer2 = self.__api.stage.GetRootLayer()

        flatten_layer = Sdf.Layer.CreateAnonymous()
        flatten_layer.TransferContent(layer1)

        UsdUtils.StitchLayers(flatten_layer, layer2)

        flatten_layer.subLayerPaths.clear()
        for p in layer2.subLayerPaths:
            flatten_layer.subLayerPaths.append(p)

        flatten_layer.Export(filename)
        self.__api.PrintStatus(f"Saved! {filename}")

    def handler_Save(self):
        self.save(self.__api.stage.GetRootLayer().identifier)

    def handler_SaveAs(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save as",
            str(Path(self.__api.stage.GetLayerStack()[-1].realPath).parent),
            "USD File (*.usd *.usda)",
        )
        if not filename:
            return
        self.save(filename)

    def handler_RemoveThisPrim(self):
        self.__api.stage.RemovePrim(self.__currentTarget)

    def handler_AddChildPrim(self):
        text, ok = QInputDialog().getText(
            self, "New PrimSpec Name", "", QLineEdit.Normal
        )
        if ok and Tf.IsValidIdentifier(text):
            prim = self.__api.stage.DefinePrim(
                self.__api.prim.GetPath().AppendChild(text)
            )
            self.__api._UsdviewApi__appController._resetPrimView()
            self.__api.ClearPrimSelection()
            self.__api._UsdviewApi__appController._updatePrimViewSelection(
                [prim.GetPath()], ["/"]
            )
            self.__api._UsdviewApi__appController._ui.primView.ExpandItemRecursively(
                self.__api._UsdviewApi__appController._getItemAtPath(prim.GetPath())
            )
