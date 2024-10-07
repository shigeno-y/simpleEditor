# SPDX-License-Identifier: Apache-2.0


import os

from pxr import Tf, UsdGeom
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMessageBox

from .TokenValidator import TokenValidator


class AddXformOpDialog:
    def __init__(self, parent, xformable):
        self._ui = QUiLoader().load(
            os.path.join(os.path.dirname(__file__), "AddXformOpDialog.ui"), parent
        )
        self._xformable = xformable
        self._validator = TokenValidator()
        self._ui.setWindowTitle("Add XformOp")
        self._ui.leSuffix.setValidator(self._validator)
        self._ui.cbPrecision.addItem("(Default)", None)
        self._ui.cbPrecision.addItem("Double", UsdGeom.XformOp.PrecisionDouble)
        self._ui.cbPrecision.addItem("Float", UsdGeom.XformOp.PrecisionFloat)
        for orderName in ["XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX", "X", "Y", "Z"]:
            self._ui.cbOrder.addItem(orderName)
        self._ui.pbOK.clicked.connect(self.accept)

    def accept(self):
        precision = self._ui.cbPrecision.currentData()
        suffix = self._ui.leSuffix.text()
        isInverse = self._ui.cbInvert.isChecked()

        try:
            if self._ui.rbTranslateOp.isChecked():
                self._xformable.AddTranslateOp(
                    precision
                    if precision is not None
                    else UsdGeom.XformOp.PrecisionDouble,
                    suffix,
                    isInverse,
                )

            elif self._ui.rbScaleOp.isChecked():
                self._xformable.AddScaleOp(
                    precision
                    if precision is not None
                    else UsdGeom.XformOp.PrecisionFloat,
                    suffix,
                    isInverse,
                )

            elif self._ui.rbRotateOp.isChecked():
                orderText = self._ui.cbOrder.currentText()
                addFuncName = f"AddRotate{orderText}Op"
                getattr(self._xformable, addFuncName)(
                    precision
                    if precision is not None
                    else UsdGeom.XformOp.PrecisionFloat,
                    suffix,
                    isInverse,
                )

            elif self._ui.rbOrientOp.isChecked():
                self._xformable.AddOrientOp(
                    precision
                    if precision is not None
                    else UsdGeom.XformOp.PrecisionFloat,
                    suffix,
                    isInverse,
                )

            elif self._ui.rbTransform.isChecked():
                self._xformable.AddTransformOp(
                    precision
                    if precision is not None
                    else UsdGeom.XformOp.PrecisionDouble,
                    suffix,
                    isInverse,
                )
            else:
                return
        except Tf.ErrorException as e:
            QMessageBox.critical(self._ui, "Failed", f"Failed to add operation.\n{e}")
            return

        self._ui.accept()

    @classmethod
    def addXformOp(cls, parent, xformable) -> bool:
        dialog = cls(parent, xformable)
        return bool(dialog._ui.exec_())
