# SPDX-License-Identifier: Apache-2.0


from . import GraphEditWindow

__window = None


def graph(usdviewApi):
    global __window
    if __window is None:
        __window = GraphEditWindow.GraphEditWindow(
            usdviewApi.qMainWindow, usdviewApi=usdviewApi
        )
    __window.show()
    __window.update(usdviewApi.property.GetPath())
