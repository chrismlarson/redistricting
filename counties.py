import geographyHelper


class County:
    def __init__(self, countyName, countyFIPS, countyGeoJSONGeometry):
        self.name = countyName
        self.FIPS = countyFIPS
        self.geometry = geographyHelper.convertGeoJSONToShapely(countyGeoJSONGeometry)
        self.blocks = []
        self.borderingCounties = []
        County.countyList.append(self)

    countyList = []


def createCountiesFromRawData(rawCountyData):
    counties = []
    for rawCounty in rawCountyData:
        counties.append(County(countyName=rawCounty['NAME'],
                               countyFIPS=rawCounty['county'],
                               countyGeoJSONGeometry=rawCounty['geometry']))
    geographyHelper.setBorderingCountiesForCounties(countyList=counties)
    return counties


def getCountyWithFIPS(countyFIPS):
    return next((item for item in County.countyList if item.FIPS == countyFIPS), None)
