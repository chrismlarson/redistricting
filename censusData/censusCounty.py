from tqdm import tqdm
from censusData.censusGeography import CensusGeography

class County(CensusGeography):
    def __init__(self, countyName, countyFIPS, countyGeoJSONGeometry):
        CensusGeography.__init__(self, FIPS=countyFIPS, geoJSONGeometry=countyGeoJSONGeometry)
        self.name = countyName
        self.blocks = []
        County.countyList.append(self)

    countyList = []


def createCountiesFromRawData(rawCountyData):
    counties = []
    tqdm.write('*** Creating Counties from raw data ***')
    with tqdm(total=len(rawCountyData)) as pbar:
        for rawCounty in rawCountyData:
            counties.append(County(countyName=rawCounty['NAME'],
                                   countyFIPS=rawCounty['county'],
                                   countyGeoJSONGeometry=rawCounty['geometry']))
            pbar.update(1)
    return counties


def getCountyWithFIPS(countyFIPS):
    return next((item for item in County.countyList if item.FIPS == countyFIPS), None)

