import geographyHelper
from tqdm import tqdm
from censusGeography import CensusGeography
from censusBlockContainer import CensusBlockContainer
from censusBlock import getAllBlocksWithCountyFIPS
from redistrictingGroup import RedistrictingGroup

class County(CensusGeography, CensusBlockContainer):
    def __init__(self, countyName, countyFIPS, countyGeoJSONGeometry):
        CensusGeography.__init__(self, FIPS=countyFIPS, geoJSONGeometry=countyGeoJSONGeometry)
        CensusBlockContainer.__init__(self)
        self.name = countyName
        self.borderingCounties = []
        County.countyList.append(self)

    countyList = []


def createCountiesFromRawData(rawCountyData):
    counties = []
    print('*** Creating Counties from raw data ***')
    with tqdm(total=len(rawCountyData)) as pbar:
        for rawCounty in rawCountyData:
            counties.append(County(countyName=rawCounty['NAME'],
                                   countyFIPS=rawCounty['county'],
                                   countyGeoJSONGeometry=rawCounty['geometry']))
            pbar.update(1)
    return counties


def getCountyWithFIPS(countyFIPS):
    return next((item for item in County.countyList if item.FIPS == countyFIPS), None)


def createRedistrictingGroupsFromCounties():
    redistrictingGroupList = []
    print('*** Creating Redistricting Groups from Counties ***')
    with tqdm(total=len(County.countyList)) as pbar:
        for county in County.countyList:
            blocksInCounty = getAllBlocksWithCountyFIPS(county.FIPS)
            redistrictingGroupList.append(RedistrictingGroup(childrenBlocks=blocksInCounty))
            pbar.update(1)

    geographyHelper.setBorderingRedistrictingGroups(redistrictingGroupList=redistrictingGroupList)
    return redistrictingGroupList
