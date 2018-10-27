from exportData.exportData import loadDataFromFile
from formatData.atomicBlock import createAtomicBlocksFromBlockList
from formatData.blockBorderGraph import BlockBorderGraph
from geographyHelper import findContiguousGroupsOfAtomicBlocks
from censusData import censusBlock
import geographyHelper
from tqdm import tqdm


class RedistrictingGroup(BlockBorderGraph):
    def __init__(self, childrenBlocks):
        BlockBorderGraph.__init__(self)
        self.blocks = childrenBlocks
        self.neighboringGroups = []
        RedistrictingGroup.redistrictingGroupList.append(self)

    redistrictingGroupList = []

    def removeWaterBlocks(self):
        nonWaterBlocks = [block for block in self.blocks if block.isWater == False]
        waterBlocks = [block for block in self.blocks if block.isWater == True]
        if any([waterBlock for waterBlock in waterBlocks if waterBlock.population > 0]):
            raise ValueError('Water block had a population')
        self.blocks = nonWaterBlocks

    def attachOrphanBlocksToClosestNeighbor(self):
        orphanBlocks = self.findOrphanBlocks()
        for orphanBlock in orphanBlocks:
            closestBlock = orphanBlock.findClosestBlockToBlocks(otherBlocks=self.blocks)
            orphanBlock.addNeighborBlocks(neighborBlocks=[closestBlock])
            closestBlock.addNeighborBlocks(neighborBlocks=[orphanBlock])

    def findOrphanBlocks(self):
        return [block for block in self.blocks if block.hasNeighbors is False]


def attachOrphanBlocksToClosestNeighborForAllRedistrictingGroups():
    for blockContainer in RedistrictingGroup.redistrictingGroupList:
        blockContainer.attachOrphanBlocksToClosestNeighbor()


def updateAllBlockContainersData():
    tqdm.write('*** Updating All Block Container Data ***')
    with tqdm(total=len(RedistrictingGroup.redistrictingGroupList)) as pbar:
        for blockContainer in RedistrictingGroup.redistrictingGroupList:
            tqdm.write('   *** One more ***')
            blockContainer.updateBlockContainerData()
            pbar.update(1)


def removeWaterBlocksFromAllRedistrictingGroups():
    for redistrictingGroup in RedistrictingGroup.redistrictingGroupList:
        redistrictingGroup.removeWaterBlocks()


def splitNonContiguousRedistrictingGroups():
    for redistrictingGroup in RedistrictingGroup.redistrictingGroupList:
        contiguousGroups = findContiguousGroupsOfAtomicBlocks(redistrictingGroup.blocks)

        if len(contiguousGroups) > 1:
            RedistrictingGroup.redistrictingGroupList.remove(redistrictingGroup)
            for contiguousGroup in contiguousGroups:
                RedistrictingGroup(childrenBlocks=contiguousGroup)


def assignNeghboringBlocksToBlocksForAllRedistrictingGroups():
    tqdm.write('\n')
    tqdm.write('*** Assigning Neighbors To All Census Blocks ***')
    count = 1
    for redistrictingGroup in RedistrictingGroup.redistrictingGroupList:
        tqdm.write('\n')
        tqdm.write('    *** Assigning Neighbors To All Census Blocks for Redistricting Group {0} of {1} ***'
                   .format(count, len(RedistrictingGroup.redistrictingGroupList)))
        with tqdm(total=len(redistrictingGroup.blocks)) as pbar:
            for atomicBlock in redistrictingGroup.blocks:
                atomicBlock.assignNeighborBlocksFromCandiateBlocks(candidateBlocks=redistrictingGroup.blocks)
                pbar.update(1)
        count += 1


def setBorderingRedistrictingGroupsForAllRedistrictingGroups():
    for redistrictingGroupToCheck in RedistrictingGroup.redistrictingGroupList:
        for redistrictingGroupToCheckAgainst in RedistrictingGroup.redistrictingGroupList:
            if redistrictingGroupToCheck != redistrictingGroupToCheckAgainst:
                if geographyHelper.intersectingGeometries(redistrictingGroupToCheck, redistrictingGroupToCheckAgainst):
                    redistrictingGroupToCheck.neighboringGroups.append(redistrictingGroupToCheckAgainst)


def getRedistrictingGroupWithCountyFIPS(countyFIPS):
    # for use when first loading redistricting group
    return next((item for item in RedistrictingGroup.redistrictingGroupList if item.FIPS == countyFIPS), None)


def convertAllCensusBlocksToAtomicBlocks():
    tqdm.write('\n')
    tqdm.write('*** Converting All Census Blocks to Atomic Blocks ***')
    count = 1
    for blockContainer in RedistrictingGroup.redistrictingGroupList:
        tqdm.write('\n')
        tqdm.write('    *** Converting to Atomic Blocks for Redistricting Group {0} of {1} ***'
                   .format(count, len(RedistrictingGroup.redistrictingGroupList)))
        atomicBlocksForGroup = createAtomicBlocksFromBlockList(blockList=blockContainer.blocks)
        blockContainer.blocks = atomicBlocksForGroup  # this triggers a block container update
        count += 1


def createRedistrictingGroupsWithAtomicBlocksFromCensusData(filePath):
    censusData = loadDataFromFile(filePath=filePath)
    tqdm.write('\n')
    tqdm.write('*** Creating Redistricting Groups from Census Data ***')
    with tqdm(total=len(censusData)) as pbar:
        for censusBlockDict in censusData:
            redistrictingGroupWithCountyFIPS = getRedistrictingGroupWithCountyFIPS(censusBlockDict['county'])
            if redistrictingGroupWithCountyFIPS is None:
                redistrictingGroupWithCountyFIPS = RedistrictingGroup(childrenBlocks=[])
                redistrictingGroupWithCountyFIPS.FIPS = censusBlockDict['county']

            isWater = False
            if censusBlockDict['block'][0] == '0':
                isWater = True
            blockFromData = censusBlock.CensusBlock(countyFIPS=censusBlockDict['county'],
                                                    tractFIPS=censusBlockDict['tract'],
                                                    blockFIPS=censusBlockDict['block'],
                                                    population=int(censusBlockDict['P0010001']),
                                                    isWater=isWater,
                                                    geoJSONGeometry=censusBlockDict['geometry'])
            redistrictingGroupWithCountyFIPS.blocks.append(blockFromData)
            pbar.update(1)

    # remove FIPS info from the groups to not pollute data later
    for redistrictingGroup in RedistrictingGroup.redistrictingGroupList:
        del redistrictingGroup.FIPS

    # convert census blocks to atomic blocks
    convertAllCensusBlocksToAtomicBlocks()

    return RedistrictingGroup.redistrictingGroupList


def prepareGraphsForAllRedistrictingGroups():
    # remove water blocks
    removeWaterBlocksFromAllRedistrictingGroups()

    # assign neighboring blocks to atomic blocks
    assignNeghboringBlocksToBlocksForAllRedistrictingGroups()

    # find single orphaned atomic blocks and attach them to the closest neighbor
    attachOrphanBlocksToClosestNeighborForAllRedistrictingGroups()

    # split non-contiguous redistricting groups
    splitNonContiguousRedistrictingGroups()

    # find and set neighboring geometries
    setBorderingRedistrictingGroupsForAllRedistrictingGroups()

    return RedistrictingGroup.redistrictingGroupList
