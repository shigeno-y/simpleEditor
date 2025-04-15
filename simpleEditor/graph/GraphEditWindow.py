# SPDX-License-Identifier: Apache-2.0


from pxr import Sdf, Tf, Usd
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
        self.__timeCodeBar = pyqtgraph.InfiniteLine(
            movable=False,
            angle=90,
            labelOpts={
                "position": 0.1,
                "color": (200, 200, 100),
                "fill": (200, 200, 200, 50),
                "movable": False,
            },
        )
        self.__scroll.setWidget(self.__widget)
        self.__api = usdviewApi
        self.__currentTarget = None
        self.__api.stage.SetFramesPerSecond(self.__api.stage.GetTimeCodesPerSecond())

        self.__api.dataModel.selection.signalComputedPropSelectionChanged.connect(
            self.slotPropSelectionChanged
        )
        self.__api._UsdviewApi__appController._ui.frameSlider.valueChanged.connect(
            self.slotTimecodeChanged
        )

        self.__eventListener = Tf.Notice.RegisterGlobally(
            Usd.Notice.StageContentsChanged, self.update
        )

    def slotPropSelectionChanged(self, *args, **kwargs):
        if self.__api.property is not None:
            self.__currentTarget = self.__api.property.GetPath()
            self.setWindowTitle(str(self.__currentTarget))
            self.update()
        else:
            self.update()

    def slotTimecodeChanged(self, newTimecode):
        self._updateTimeCodeBar(newTimecode)

    def _updateGraph(self, xs, ys, degrees):
        plot = self.__widget.getPlotItem()
        # plot.clear()

        legend = plot.addLegend(offset=(10, 10))
        legend.clear()

        interpolationType = self.__api.stage.GetInterpolationType()
        stepMode = "left" if interpolationType == Usd.InterpolationTypeHeld else None

        if len(degrees) == 1:
            series = plot.plot(
                x=xs, y=ys, name=degrees[0], clear=True, stepMode=stepMode
            )
        else:
            colors = ["r", "g", "b", "w"]
            for d, label in enumerate(degrees):
                pen = pyqtgraph.mkPen(color=colors[d], style=Qt.SolidLine)
                series = plot.plot(
                    x=xs,
                    y=[v[d] for v in ys],
                    name=label,
                    pen=pen,
                    clear=True if d == 0 else False,
                    stepMode=stepMode,
                )

        self.__widget.addItem(self.__timeCodeBar)

    def _updateTimeCodeBar(self, time: float):
        self.__timeCodeBar.setPos(time)

    def update(self, *args, time=None, **kwargs):
        if time is None:
            time = self.__api.frame.GetValue()

        if self.__currentTarget:
            prop = self.__api.stage.GetAttributeAtPath(self.__currentTarget)
            if prop is None or prop.GetTypeName() not in _type2degrees:
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
