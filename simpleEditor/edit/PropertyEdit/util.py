# SPDX-License-Identifier: Apache-2.0


from pxr import (
    Gf,
    Usd,
)

def shouldSetAsTimesamples(attr:Usd.Attribute):
    ts = attr.GetTimeSamples()
    return attr.IsAuthored() and (ts is not None and len(ts) > 0)

def hasTimeSamplesAtTimeCode(attr:Usd.Attribute, t:Usd.TimeCode):
    ct = attr.GetTimeSamplesInInterval(Gf.Interval(t))
    return (ct is not None and len(ct) == 1)
