# SPDX-License-Identifier: Apache-2.0


from pxr import (
    Gf,
    Usd,
)

from PySide6.QtWidgets import (
    QWidget,
)


def shouldSetAsTimesamples(attr: Usd.Attribute):
    ts = attr.GetTimeSamples()
    return attr.IsAuthored() and (ts is not None and len(ts) > 0)


def hasTimeSamplesAtTimeCode(attr: Usd.Attribute, t: Usd.TimeCode):
    ct = attr.GetTimeSamplesInInterval(Gf.Interval(t))
    return ct is not None and len(ct) == 1


def updateValue(
    attr: Usd.Attribute, value, current_time: Usd.TimeCode, do_copy: bool = False
):
    from pprint import pprint

    if shouldSetAsTimesamples(attr):
        if do_copy:
            timesamples = dict()

            for t in attr.GetTimeSamples():
                timesamples[t] = attr.Get(t)

            attr.Clear()

            for t, v in timesamples.items():
                attr.Set(v, t)
            print(attr, "INITIAL")
            pprint(timesamples)

        attr.Set(value, current_time)
        print(attr)
        pprint({t: attr.Get(t) for t in attr.GetTimeSamples()})

    else:
        attr.Set(value)


def updateBackgroundColorOnTimeSamples(propertyEdit: QWidget):
    ts = propertyEdit._attr.GetTimeSamples()
    if hasTimeSamplesAtTimeCode(propertyEdit._attr, propertyEdit._currentTime):
        # we have timesample at this timecode!
        propertyEdit.setStyleSheet("background-color: #b58900;")
    elif ts is not None and len(ts) > 0:
        # we have at least 1 timesample somewhere
        propertyEdit.setStyleSheet("background-color: #859900;")
