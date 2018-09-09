class County:
    def __init__(self, countyName, countyFIPS, countyGeoJSONGeometry):
        self.name = countyName
        self.FIPS = countyFIPS
        #todo: convert to shapely geometry for comparisons
        self.geometry = countyGeoJSONGeometry

def createCountiesFromRawData(rawCountyData):
    counties = []
    for rawCounty in rawCountyData:
        counties.append(County(countyName=rawCounty['NAME'],
                               countyFIPS=rawCounty['county'],
                               countyGeoJSONGeometry=rawCounty['geometry']))
    return counties


