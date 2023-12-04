from . import SimpleEditWindow

__window = None


def edit(usdviewApi):
    global __window
    if __window is None:
        __window = SimpleEditWindow.SimpleEditWindow(usdviewApi=usdviewApi)
    __window.show()
    __window.update(usdviewApi.prim.GetPath())
