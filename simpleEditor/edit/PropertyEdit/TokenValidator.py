# SPDX-License-Identifier: Apache-2.0


from pxr import Tf
from PySide6.QtGui import QValidator


class TokenValidator(QValidator):
    """USD の Token に対する Validator."""

    def fixup(self, inStr: str):
        if inStr:
            return Tf.MakeValidIdentifier(inStr)
        else:
            return ""

    def validate(self, inStr, _):
        if not inStr:
            return QValidator.State.Intermidiate
        elif Tf.IsValidIdentifier(inStr):
            return QValidator.State.Acceptable
        else:
            return QValidator.State.Invalid
