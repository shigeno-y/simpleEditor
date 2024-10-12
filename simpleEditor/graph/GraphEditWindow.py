# SPDX-License-Identifier: Apache-2.0


from pxr import Sdf
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import pyqtgraph


_type2degrees = {
    Sdf.ValueTypeNames.Float: ["value"],
    Sdf.ValueTypeNames.Float2: ["X", "Y"],
    Sdf.ValueTypeNames.Float3: ["X", "Y", "Z"],
    Sdf.ValueTypeNames.Float4: ["X", "Y", "Z", "W"],
    Sdf.ValueTypeNames.Double: ["value"],
    Sdf.ValueTypeNames.Double2: ["X", "Y"],
    Sdf.ValueTypeNames.Double3: ["X", "Y", "Z"],
    Sdf.ValueTypeNames.Double4: ["X", "Y", "Z", "W"],
    Sdf.ValueTypeNames.Int: ["value"],
    Sdf.ValueTypeNames.UInt: ["value"],
    Sdf.ValueTypeNames.Bool: ["value"],
    Sdf.ValueTypeNames.Color3f: ["R", "G", "B"],
    Sdf.ValueTypeNames.Color4f: ["R", "G", "B", "A"],
    Sdf.ValueTypeNames.Quatd: ["i", "j", "k", "r"],
    Sdf.ValueTypeNames.Quatf: ["i", "j", "k", "r"],
    Sdf.ValueTypeNames.Quath: ["i", "j", "k", "r"],
}


def debug(*args, **kwargs):
    print(*args, **kwargs)


class GraphEditWindow(QDockWidget):
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

        self.__scroll = QScrollArea(self)
        self.__scroll.setWidgetResizable(True)
        self.__layout.addWidget(self.__scroll)

        self.__widget = pyqtgraph.PlotWidget(parent=self.__scroll)
        self.__scroll.setWidget(self.__widget)

        self.__api = usdviewApi
        self.__currentTarget = None
        self.__api.stage.SetFramesPerSecond(self.__api.stage.GetTimeCodesPerSecond())

        self.__api.dataModel.selection.signalComputedPropSelectionChanged.connect(
            self.slotPropSelectionChanged
        )

    def slotPropSelectionChanged(self, *args, **kwargs):
        newPropPath = None
        if self.__api.property is not None:
            newPropPath = self.__api.property.GetPath()
            self.update(newPropPath)
        else:
            self.update()

    def _updateGraph(self, xs, ys, degrees):
        plot = self.__widget.getPlotItem()
        plot.clear()

        legend = plot.addLegend(offset=(10, 10))
        legend.clear()

        if len(degrees) == 1:
            series = plot.plot(x=xs, y=ys, name=degrees[0], symbol="x")
            series.sigPointsClicked.connect(debug)
        else:
            colors = ["r", "g", "b", "w"]
            for d, label in enumerate(degrees):
                pen = pyqtgraph.mkPen(color=colors[d], style=Qt.SolidLine)
                series = plot.plot(
                    x=xs,
                    y=[v[d] for v in ys],
                    name=label,
                    pen=pen,
                    symbol="x",
                )
                series.sigPointsClicked.connect(debug)

    def update(self, newPropPath=None, time=None):
        if newPropPath is None:
            newPropPath = self.__currentTarget
        if time is None:
            time = self.__api.frame.GetValue()
        if self.__currentTarget != newPropPath:
            self.__currentTarget = newPropPath
            self.setWindowTitle(str(self.__currentTarget))

        if self.__currentTarget:
            prop = self.__api.stage.GetAttributeAtPath(newPropPath)
            if prop and prop.GetTypeName() not in _type2degrees:
                # no graph repl
                return

            xs = prop.GetTimeSamples()
            ys = [prop.Get(t) for t in xs]

            if prop.GetTypeName() in (
                Sdf.ValueTypeNames.Quatd,
                Sdf.ValueTypeNames.Quatf,
                Sdf.ValueTypeNames.Quath,
            ):
                ys = [
                    (
                        q.GetImaginary()[0],
                        q.GetImaginary()[1],
                        q.GetImaginary()[2],
                        q.GetReal(),
                    )
                    for q in ys
                ]

            self._updateGraph(xs, ys, _type2degrees[prop.GetTypeName()])
