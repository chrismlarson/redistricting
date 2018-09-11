from shapely.geometry import shape
# On Windows, I needed to install Shapely manually
# Found whl file here: https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
# And then ran:
# from pip._internal import main
# def install_whl(path):
#     main(['install', path])
# install_whl("path_to_file\\Shapely-1.6.4.post1-cp37-cp37m-win32.whl")
# but not sure if this worked...


class County:
    def __init__(self, countyName, countyFIPS, countyGeoJSONGeometry):
        self.name = countyName
        self.FIPS = countyFIPS
        self.geometry = convertGeoJSONToShapely(countyGeoJSONGeometry)
        self.borderingCounties = []




def createCountiesFromRawData(rawCountyData):
    counties = []
    for rawCounty in rawCountyData:
        counties.append(County(countyName=rawCounty['NAME'],
                               countyFIPS=rawCounty['county'],
                               countyGeoJSONGeometry=rawCounty['geometry']))
    return counties


def convertGeoJSONToShapely(geoJSON):
    shapelyShape = shape(geoJSON)
    return shapelyShape


def setBorderingCountiesForCounties(countyList):
    for countyToCheck in countyList:
        for countyToCheckAgainst in countyList:
            if countyToCheck != countyToCheckAgainst:
                if countyToCheck.geometry.intersects(countyToCheckAgainst.geometry):
                    countyToCheck.borderingCounties.append(countyToCheckAgainst)
