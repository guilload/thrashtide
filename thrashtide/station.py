from json import loads

from .tide import Tide
from .config import STATIONS_PATH


class Station(object):

    def __init__(self, station):
        self.latitude = station["latitude"]
        self.longitude = station["longitude"]
        self.noaa_id = station['noaa_id']
        self.noaa_name = station['noaa_name']
        self.tide = Tide(station['constituents'], station["MTL"],
                         station["MLLW"])

    @property
    def description(self):
        return {"noaa_id": self.noaa_id, "noaa_name": self.noaa_name,
                "latitude": self.latitude, "longitude": self.longitude}

    @staticmethod
    def get(latitude, longitude):
        return STATIONS[0]  # FIXME

    @staticmethod
    def load(filepath):
        with open(filepath) as stations:
            return [Station(station) for station in loads(stations.read())]


STATIONS = Station.load(STATIONS_PATH)  # FIXME
