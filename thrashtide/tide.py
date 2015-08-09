from datetime import datetime, timedelta

import numpy as np
import pytides

from pytides import constituent as cons
from pytides.tide import Tide as PyTide

from .constants import DATE_FORMAT, FOOT, HIGH, UTC, METERS


NOAA_CONSTITUENTS = [c for c in cons.noaa if c != cons._Z0] + [cons._Z0]
SIX_HOURS = timedelta(hours=6, minutes=15)


class Tide(object):

    def __init__(self, constituents, mtl, mllw):
        self.amplitudes = [cst["amplitude"] for cst in constituents]
        self.phases = [cst["phase"] for cst in constituents]

        offset = mtl - mllw
        self.phases.append(0)
        self.amplitudes.append(offset)

        self.model = np.zeros(len(NOAA_CONSTITUENTS), dtype=PyTide.dtype)
        self.model['constituent'] = NOAA_CONSTITUENTS
        self.model['amplitude'] = self.amplitudes
        self.model['phase'] = self.phases

        self.tide = PyTide(model=self.model, radians=False)

    def extrema(self, start, stop, timezone, unit):
        extrema = self.tide.extrema(start - SIX_HOURS, stop + SIX_HOURS)
        return [self.format_extremum(time, height, hilo, timezone, unit) for time, height, hilo in extrema]

    @staticmethod
    def format_extremum(time, height, hilo, timezone, unit):
        return {"height": height if unit == METERS else height * FOOT,
                "high": hilo == HIGH,
                "time": time.astimezone(timezone).strftime(DATE_FORMAT)}
