from pxr import UsdGeom


def addCube(usdviewApi):
    UsdGeom.Cube.Define(usdviewApi.stage, usdviewApi.prim.GetPath().AppendChild("cube"))
