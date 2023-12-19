from pxr import Tf
from PySide2.QtGui import QValidator


class TokenValidator(QValidator):
    """USD の Token に対する Validator."""

    def fixup(self, inStr: str):
        return Tf.MakeValidIdentifier(inStr)

    def validate(self, inStr, _):
        if Tf.IsValidIdentifier(inStr):
            return QValidator.State.Acceptable
        else:
            return QValidator.State.Invalid
