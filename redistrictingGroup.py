from censusBlockContainer import CensusBlockContainer
from censusCounty import County
from censusBlock import getAllBlocksWithCountyFIPS
import geographyHelper
from tqdm import tqdm

class RedistrictingGroup(CensusBlockContainer):
    def __init__(self, childrenBlocks):
        CensusBlockContainer.__init__(self)
        self.blocks = childrenBlocks
        self.neighboringGroups = []
        RedistrictingGroup.redistrictingGroupList.append(self)

    redistrictingGroupList = []

def setBorderingRedistrictingGroups(redistrictingGroupList):
    for redistrictingGroupToCheck in redistrictingGroupList:
        for redistrictingGroupToCheckAgainst in redistrictingGroupList:
            if redistrictingGroupToCheck != redistrictingGroupToCheckAgainst:
                if geographyHelper.intersectingGeometries(redistrictingGroupToCheck, redistrictingGroupToCheckAgainst):
                    redistrictingGroupToCheck.neighboringGroups.append(redistrictingGroupToCheckAgainst)

def createRedistrictingGroupsFromCounties():
    redistrictingGroupList = []
    tqdm.write('*** Creating Redistricting Groups from Counties ***')
    with tqdm(total=len(County.countyList)) as pbar:
        for county in County.countyList:
            blocksInCounty = getAllBlocksWithCountyFIPS(county.FIPS)
            redistrictingGroupList.append(RedistrictingGroup(childrenBlocks=blocksInCounty))
            pbar.update(1)

    setBorderingRedistrictingGroups(redistrictingGroupList=redistrictingGroupList)
    assignNeighboringBlocksToEveryBlock()
    return redistrictingGroupList


def assignNeighboringBlocksToEveryBlock():
    temp = 0

