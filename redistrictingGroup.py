from censusBlockContainer import CensusBlockContainer
from censusCounty import County
from censusBlock import getAllBlocksWithCountyFIPS
import geographyHelper
from tqdm import tqdm
import exportData


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


def findCandidateNeighborsForBlock(block, parentGroup):
    #todo: maybe speed this up by finding close by objects (tracts?)
    candidateNeighbors = parentGroup.blocks.copy()
    if block in parentGroup.borderBlocks:
        for neighborGroup in parentGroup.neighboringGroups:
            if geographyHelper.intersectingGeometries(neighborGroup, block):
                candidateNeighbors = candidateNeighbors + neighborGroup.borderBlocks
    return candidateNeighbors


def findNeighboringBlocksFromCandidatesForBlock(block, candidates):
    neighboringBlocks = []
    for candidate in candidates:
        if block is not candidate:
            if geographyHelper.intersectingGeometries(block, candidate):
                if geographyHelper.containingGeometries(block, candidate):
                    # containingBlocks = [block, candidate]
                    # exportData.exportGeographiesToShapefile(geographyList=containingBlocks,
                    #                                         descriptionOfInfo='ContainingBlocks')
                    #todo: ignore for now, but need to group these all together earlier
                    temp=0
                else:
                    # intersectingBlocks = [block, candidate]
                    # exportData.exportGeographiesToShapefile(geographyList=intersectingBlocks,
                    #                                         descriptionOfInfo='IntersectingBlocks')
                    neighboringBlocks.append(candidate)
    return neighboringBlocks


def assignNeighboringBlocksToEveryBlock():
    for redistrictingGroup in RedistrictingGroup.redistrictingGroupList:
        tqdm.write('*** Finding Neighboring Blocks within Group {0} of {1} ***'.format(
            RedistrictingGroup.redistrictingGroupList.index(redistrictingGroup) + 1,
            len(RedistrictingGroup.redistrictingGroupList)))

        with tqdm(total=len(redistrictingGroup.blocks)) as pbar:
            for block in redistrictingGroup.blocks:
                candidateNeighbors = findCandidateNeighborsForBlock(block=block, parentGroup=redistrictingGroup)
                neighboringBlocks = findNeighboringBlocksFromCandidatesForBlock(block=block, candidates=candidateNeighbors)
                block.neighboringBlocks = neighboringBlocks
                pbar.update(1)
