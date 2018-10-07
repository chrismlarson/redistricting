from formatData.blockGraph import BlockGraph
from censusData import censusBlock
import geographyHelper
import csvHelper
import csv
import ast
from tqdm import tqdm


class RedistrictingGroup(BlockGraph):
    def __init__(self, childrenBlocks):
        BlockGraph.__init__(self)
        self.blocks = childrenBlocks
        self.neighboringGroups = []
        RedistrictingGroup.redistrictingGroupList.append(self)

    redistrictingGroupList = []


def updateAllBlockContainersData():
    tqdm.write('*** Updating All Block Container Data ***')
    with tqdm(total=len(RedistrictingGroup.redistrictingGroupList)) as pbar:
        for blockContainer in RedistrictingGroup.redistrictingGroupList:
            blockContainer.updateBlockContainerData()
            pbar.update(1)


def setBorderingRedistrictingGroups(redistrictingGroupList):
    for redistrictingGroupToCheck in redistrictingGroupList:
        for redistrictingGroupToCheckAgainst in redistrictingGroupList:
            if redistrictingGroupToCheck != redistrictingGroupToCheckAgainst:
                if geographyHelper.intersectingGeometries(redistrictingGroupToCheck, redistrictingGroupToCheckAgainst):
                    redistrictingGroupToCheck.neighboringGroups.append(redistrictingGroupToCheckAgainst)


def getRedistrictingGroupWithCountyFIPS(countyFIPS):
    # for use when first loading redistricting group
    return next((item for item in RedistrictingGroup.redistrictingGroupList if item.FIPS == countyFIPS), None)


# def createRedistrictingGroupsFromCounties():
#     redistrictingGroupList = []
#     tqdm.write('*** Creating Redistricting Groups from Counties ***')
#     with tqdm(total=len(County.countyList)) as pbar:
#         for county in County.countyList:
#             blocksInCounty = censusBlock.getAllBlocksWithCountyFIPS(county.FIPS)
#             redistrictingGroupList.append(RedistrictingGroup(childrenBlocks=blocksInCounty))
#             pbar.update(1)
#
#     setBorderingRedistrictingGroups(redistrictingGroupList=redistrictingGroupList)
#     assignNeighboringBlocksToEveryBlock()
#     return redistrictingGroupList


def createRedistrictingGroupsFromCensusDataCSV(csvPath):
    csvHelper.setCSVLimitToMaxAcceptable()
    numOfCSVRows = csvHelper.getNumOfCSVRows(csvPath=csvPath)

    tqdm.write('*** Loading Census CSV as Redistricting Groups ***')
    redistrictingGroupList = []
    with tqdm(total=numOfCSVRows) as pbar:
        with open(csvPath, newline='\n') as csvFile:
            dictReader = csv.DictReader(csvFile)
            for row in dictReader:
                redistrictingGroupWithCountyFIPS = getRedistrictingGroupWithCountyFIPS(row['county'])
                if redistrictingGroupWithCountyFIPS is None:
                    redistrictingGroupWithCountyFIPS = RedistrictingGroup(childrenBlocks=[])
                    redistrictingGroupWithCountyFIPS.FIPS = row['county']
                    redistrictingGroupList.append(redistrictingGroupWithCountyFIPS)

                isWater = False
                if row['block'][0] == '0':
                    isWater = True
                blockFromCSV = censusBlock.CensusBlock(countyFIPS=row['county'],
                                                       tractFIPS=row['tract'],
                                                       blockFIPS=row['block'],
                                                       population=int(row['P0010001']),
                                                       isWater=isWater,
                                                       geoJSONGeometry=ast.literal_eval(row['geometry']))
                redistrictingGroupWithCountyFIPS.blocks.append(blockFromCSV)
                pbar.update(1)

    #setting parent geometries and populations
    updateAllBlockContainersData()

    #find and set neighboring geometries
    setBorderingRedistrictingGroups(redistrictingGroupList=redistrictingGroupList)

    #remove FIPS info from the groups to not pollute data later
    for redistrictingGroup in redistrictingGroupList:
        del redistrictingGroup.FIPS

    return redistrictingGroupList

#
# def findCandidateNeighborsForBlock(block, parentGroup):
#     # todo: maybe speed this up by finding close by objects (tracts?)
#     candidateNeighbors = parentGroup.blocks.copy()
#     if block in parentGroup.borderBlocks:
#         for neighborGroup in parentGroup.neighboringGroups:
#             if geographyHelper.intersectingGeometries(neighborGroup, block):
#                 candidateNeighbors = candidateNeighbors + neighborGroup.borderBlocks
#     return candidateNeighbors
#
#
# def findNeighboringBlocksFromCandidatesForBlock(block, candidates):
#     neighboringBlocks = []
#     for candidate in candidates:
#         if block is not candidate:
#             if geographyHelper.intersectingGeometries(block, candidate):
#                 if geographyHelper.containingGeometries(block, candidate):
#                     # containingBlocks = [block, candidate]
#                     # exportData.exportGeographiesToShapefile(geographyList=containingBlocks,
#                     #                                         descriptionOfInfo='ContainingBlocks')
#                     # todo: ignore for now, but need to group these all together earlier
#                     temp = 0
#                 else:
#                     # intersectingBlocks = [block, candidate]
#                     # exportData.exportGeographiesToShapefile(geographyList=intersectingBlocks,
#                     #                                         descriptionOfInfo='IntersectingBlocks')
#                     neighboringBlocks.append(candidate)
#     return neighboringBlocks
#
#
# def assignNeighboringBlocksToEveryBlock():
#     for redistrictingGroup in RedistrictingGroup.redistrictingGroupList:
#         tqdm.write('*** Finding Neighboring Blocks within Group {0} of {1} ***'.format(
#             RedistrictingGroup.redistrictingGroupList.index(redistrictingGroup) + 1,
#             len(RedistrictingGroup.redistrictingGroupList)))
#
#         with tqdm(total=len(redistrictingGroup.blocks)) as pbar:
#             for block in redistrictingGroup.blocks:
#                 candidateNeighbors = findCandidateNeighborsForBlock(block=block, parentGroup=redistrictingGroup)
#                 neighboringBlocks = findNeighboringBlocksFromCandidatesForBlock(block=block,
#                                                                                 candidates=candidateNeighbors)
#                 block.neighboringBlocks = neighboringBlocks
#                 pbar.update(1)
