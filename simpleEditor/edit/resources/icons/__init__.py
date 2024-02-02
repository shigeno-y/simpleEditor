# SPDX-License-Identifier: Apache-2.0


_icons = dict()


def getIcon(name):
    """
    アイコンを名前から取得します.

    # アイコンファイルの命名規則
    <NAME>_<TYPENAME>_<SIZE>.png
    NAME: camel case の名前. getIcon() の引数についてキーとなる文字列.
    TYPENAME: nf, nn, df, dn, af, an, sf, sn のいずれか.
    SIZE: 数値[px]. 正方形アイコンの一辺の長さ. (長方形には必要になったら対応.)
    """
    from PySide2.QtCore import QSize
    from PySide2.QtGui import QIcon

    global _icons

    _str2typeMap = {
        "nf": (QIcon.Normal, QIcon.Off),
        "nn": (QIcon.Normal, QIcon.On),
        "df": (QIcon.Disabled, QIcon.Off),
        "dn": (QIcon.Disabled, QIcon.On),
        "af": (QIcon.Active, QIcon.Off),
        "an": (QIcon.Active, QIcon.On),
        "sf": (QIcon.Selected, QIcon.Off),
        "sn": (QIcon.Selected, QIcon.On),
    }

    if name not in _icons:
        import glob
        import os

        rootDir = os.path.dirname(__file__)
        files = glob.glob(os.path.join(rootDir, f"{name}_*.png"))
        if not files:
            raise RuntimeError("Iconfile Not Found")
        icon = QIcon()

        for filename in files:
            try:
                _, typeName, size = os.path.splitext(os.path.basename(filename))[0].split("_", 3)
                iconMode, iconState = _str2typeMap[typeName]
                size = int(size)
                icon.addFile(filename, QSize(size, size), iconMode, iconState)
            except Exception as e:
                raise RuntimeError(f"Invalid Icon. {e}") from e
        _icons[name] = icon
    return _icons[name]
