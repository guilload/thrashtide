import json

import scrapy


HARCON_HEADER = ("index", "name", "amplitude", "phase", "speed")


class Station(scrapy.Item):

    constituents = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    MLLW = scrapy.Field()
    MTL = scrapy.Field()
    noaa_id = scrapy.Field()
    noaa_name = scrapy.Field()
    state = scrapy.Field()


class NOAASpider(scrapy.Spider):
    name = "NOAA"
    start_urls = ["http://tidesandcurrents.noaa.gov/stations.html?type=Harmonic+Constituents"]

    def parse(self, response):
        for noaa_id in [noaa_id[1:] for noaa_id in response.xpath("//div[contains(@class, 'station')]/@id").extract()]:
            station = Station(noaa_id=noaa_id)

            datums_path = "datums.html?units=1&epoch=0&id={}".format(noaa_id)
            datums_url = response.urljoin(datums_path)
            yield scrapy.Request(datums_url, callback=self.parse_datums, meta={'station': station})

    def parse_datums(self, response):
        station = response.meta['station']
        xpath = "//tbody/tr/td/a[text() = '{}']/../../td[2]/text()"
        noaa_id = station["noaa_id"]

        for datum in ("MLLW", "MTL"):
            value = response.xpath(xpath.format(datum))[0].extract()
            station[datum] = float(value)

        harcon_path = "harcon.html?unit=0&timezone=0&id={}".format(noaa_id)
        harcon_url = response.urljoin(harcon_path)
        yield scrapy.Request(harcon_url, callback=self.parse_harcons, meta={'station': station})

    def parse_harcons(self, response):
        station = response.meta['station']
        noaa_id = station["noaa_id"]

        harcons = []

        for tr in response.xpath("//tbody/tr"):
            harcon = {}

            for i, td in enumerate(tr.xpath("td/text()")[:5]):
                harcon[HARCON_HEADER[i]] = td.extract()

            for key, func in (("index", int), ("amplitude", float), ("phase", float), ("speed", float)):
                harcon[key] = func(harcon[key])

            harcons.append(harcon)

        station["constituents"] = harcons

        stationhome_path = "stationhome.html?id={}".format(noaa_id)
        stationhome_url = response.urljoin(stationhome_path)
        yield scrapy.Request(stationhome_url, callback=self.parse_station, meta={'station': station})

    def parse_station(self, response):
        station = response.meta['station']

        location, _ = response.xpath("//h3/text()")[0].extract().strip().rsplit('-', 1)
        name, state = location.rsplit(',', 1)

        station["noaa_name"] = name.strip()
        station["state"] = state.strip()

        texts = response.xpath("//td/text()").extract()
        latitude = self.ugly_search(texts, "Latitude")
        longitude = self.ugly_search(texts, "Longitude")

        station["latitude"] = self.ugly_convert_coordinate(latitude)
        station["longitude"] = self.ugly_convert_coordinate(longitude)

        yield station

    @staticmethod
    def ugly_convert_coordinate(coordinate):
        degrees, minutes, _ = coordinate.split()
        degrees = "".join([c for c in degrees if c.isdigit() or c == '.'])
        minutes = "".join([c for c in minutes if c.isdigit() or c == '.'])
        return round(float(degrees) + float(minutes) / 60, 2)

    @staticmethod
    def ugly_search(elements, key):
        for i, element in enumerate(elements):
            if element == key:
                return elements[i + 1]

        raise KeyError("key '{}' no found".format(key))
