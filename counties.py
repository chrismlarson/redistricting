import geographyHelper

class County:
    def __init__(self, countyName, countyFIPS, countyGeoJSONGeometry):
        self.name = countyName
        self.FIPS = countyFIPS
        self.geometry = geographyHelper.convertGeoJSONToShapely(countyGeoJSONGeometry)
        self.borderingCounties = []


def createCountiesFromRawData(rawCountyData):
    counties = []
    for rawCounty in rawCountyData:
        counties.append(County(countyName=rawCounty['NAME'],
                               countyFIPS=rawCounty['county'],
                               countyGeoJSONGeometry=rawCounty['geometry']))
    return counties


def setBorderingCountiesForCounties(countyList):
    for countyToCheck in countyList:
        for countyToCheckAgainst in countyList:
            if countyToCheck != countyToCheckAgainst:
                if countyToCheck.geometry.intersects(countyToCheckAgainst.geometry):
                    countyToCheck.borderingCounties.append(countyToCheckAgainst)
