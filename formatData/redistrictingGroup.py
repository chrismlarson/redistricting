from exportData.displayShapes import plotBlocksForRedistrictingGroups, plotBlocksForRedistrictingGroup
from formatData.atomicBlock import createAtomicBlocksFromBlockList, validateAllAtomicBlocks, \
    assignNeighborBlocksFromCandiateBlocks
from formatData.blockBorderGraph import BlockBorderGraph
from formatData.graphObject import GraphObject
from geographyHelper import findContiguousGroupsOfGraphObjects, findClosestGeometry, intersectingGeometries, Alignment
from censusData import censusBlock
from multiprocessing.dummy import Pool
from itertools import repeat
from tqdm import tqdm

from redistrict.district import validateContiguousRedistrictingGroups


class RedistrictingGroup(BlockBorderGraph, GraphObject):
    def __init__(self, childrenBlocks):
        BlockBorderGraph.__init__(self)
        self.children = childrenBlocks
        GraphObject.__init__(self, centerOfObject=self.geometry.centroid)
        RedistrictingGroup.redistrictingGroupList.append(self)

    redistrictingGroupList = []

    def updateBlockContainerData(self):
        super(RedistrictingGroup, self).updateBlockContainerData()
        self.updateCenterOfObject(self.geometry.centroid)

    def removeWaterBlocks(self):
        nonWaterBlocks = [block for block in self.children if block.isWater == False]
        waterBlocks = [block for block in self.children if block.isWater == True]
        if any([waterBlock for waterBlock in waterBlocks if waterBlock.population > 0]):
            raise ValueError('Water block had a population')
        self.children = nonWaterBlocks

    def attachOrphanBlocksToClosestNeighbor(self):
        orphanBlocks = self.findOrphanBlocks()
        for orphanBlock in orphanBlocks:
            closestBlock = findClosestGeometry(originGeometry=self, otherGeometries=self.children)
            orphanBlock.addNeighbors(neighbors=[closestBlock])
            closestBlock.addNeighbors(neighbors=[orphanBlock])

    def findOrphanBlocks(self):
        return [block for block in self.children if block.hasNeighbors is False]

    def getGraphSplits(self, shouldDrawGraph=False):
        self.fillPopulationEnergyGraph(Alignment.northSouth)
        if shouldDrawGraph:
            plotBlocksForRedistrictingGroup(redistrictingGroup=self, showGraphHeatmap=True)
        northSouthSplit = self.getPopulationEnergySplit(Alignment.northSouth)
        self.clearPopulationEnergyGraph()

        self.fillPopulationEnergyGraph(Alignment.westEast)
        if shouldDrawGraph:
            plotBlocksForRedistrictingGroup(redistrictingGroup=self, showGraphHeatmap=True)
        westEastSplit = self.getPopulationEnergySplit(Alignment.westEast)
        self.clearPopulationEnergyGraph()

        northWestSplit = [group for group in northSouthSplit[0] if group in westEastSplit[0]]
        northEastSplit = [group for group in northSouthSplit[0] if group in westEastSplit[1]]
        southWestSplit = [group for group in northSouthSplit[1] if group in westEastSplit[0]]
        southEastSplit = [group for group in northSouthSplit[1] if group in westEastSplit[1]]
        return (RedistrictingGroup(childrenBlocks=northWestSplit),
                RedistrictingGroup(childrenBlocks=northEastSplit),
                RedistrictingGroup(childrenBlocks=southWestSplit),
                RedistrictingGroup(childrenBlocks=southEastSplit))

    def fillPopulationEnergyGraph(self, alignment):
        remainingObjects = self.children.copy()
        if alignment is Alignment.northSouth:
            blocksToActOn = self.westernChildBlocks
        else:
            blocksToActOn = self.northernChildBlocks

        for blockToActOn in blocksToActOn:
            blockToActOn.populationEnergy = blockToActOn.population
            remainingObjects.remove(blockToActOn)

        while len(remainingObjects) > 0:
            blocksToActOn = getNeighborsForGraphObjectsInList(graphObjects=blocksToActOn, inList=remainingObjects)
            filledBlocks = [block for block in self.children if block not in remainingObjects]

            for blockToActOn in blocksToActOn:
                previousNeighbors = getNeighborsForGraphObjectsInList(graphObjects=[blockToActOn], inList=filledBlocks)
                if len(previousNeighbors) is 0:
                    raise ReferenceError("Can't find previous neighbor for {0}".format(blockToActOn))

                lowestPopulationEnergyNeighbor = None
                for previousNeighbor in previousNeighbors:
                    if lowestPopulationEnergyNeighbor is None:
                        lowestPopulationEnergyNeighbor = previousNeighbor
                    elif previousNeighbor.populationEnergy < lowestPopulationEnergyNeighbor.populationEnergy:
                        lowestPopulationEnergyNeighbor = previousNeighbor

                blockToActOn.populationEnergy = lowestPopulationEnergyNeighbor.populationEnergy + blockToActOn.population
                remainingObjects.remove(blockToActOn)

    def clearPopulationEnergyGraph(self):
        for child in self.children:
            child.populationEnergy = 0

    def getPopulationEnergySplit(self, alignment):
        raise NotImplementedError

    def __lt__(self, other):
        if isinstance(other, RedistrictingGroup):
            return self.graphId < other.graphId
        return NotImplemented('Can only do a less than comparison with another RedistrictingGroup')


def getNeighborsForGraphObjectsInList(graphObjects, inList):
    neighborList = []
    for graphObject in graphObjects:
        for neighborObject in graphObject.allNeighbors:
            if neighborObject in inList and neighborObject not in neighborList and neighborObject not in graphObjects:
                neighborList.append(neighborObject)
    return neighborList


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
    tqdm.write('\n')
    tqdm.write('*** Removing Water Blocks From All Redistricting Groups ***')
    with tqdm(total=len(RedistrictingGroup.redistrictingGroupList)) as pbar:
        for redistrictingGroup in RedistrictingGroup.redistrictingGroupList:
            redistrictingGroup.removeWaterBlocks()
            pbar.update(1)


def splitNonContiguousRedistrictingGroups():
    for redistrictingGroup in RedistrictingGroup.redistrictingGroupList:
        contiguousGroups = findContiguousGroupsOfGraphObjects(redistrictingGroup.children)

        if len(contiguousGroups) > 1:
            RedistrictingGroup.redistrictingGroupList.remove(redistrictingGroup)
            for contiguousGroup in contiguousGroups:
                RedistrictingGroup(childrenBlocks=contiguousGroup)


def assignNeighboringBlocksToBlocksForAllRedistrictingGroups():
    tqdm.write('\n')
    tqdm.write('*** Assigning Neighbors To All Census Blocks ***')
    count = 1
    for redistrictingGroup in RedistrictingGroup.redistrictingGroupList:
        tqdm.write('\n')
        tqdm.write('    *** Assigning Neighbors To All Census Blocks for Redistricting Group {0} of {1} ***'
                   .format(count, len(RedistrictingGroup.redistrictingGroupList)))
        with tqdm(total=len(redistrictingGroup.children)) as pbar:
            threadPool = Pool(4)
            threadPool.starmap(assignNeighborBlocksFromCandiateBlocks,
                               zip(redistrictingGroup.children,
                                   repeat(redistrictingGroup.children),
                                   repeat(pbar)))
            # for atomicBlock in redistrictingGroup.children:
            #     atomicBlock.assignNeighborBlocksFromCandiateBlocks(candidateBlocks=redistrictingGroup.children)
            #     pbar.update(1)
        count += 1

    # find single orphaned atomic blocks and attach them to the closest neighbor.
    # That way we don't have too small of redistricting groups for splitting them in the next step.
    attachOrphanBlocksToClosestNeighborForAllRedistrictingGroups()


def attachOrphanRedistrictingGroupsToClosestNeighbor():
    contiguousRegions = findContiguousGroupsOfGraphObjects(RedistrictingGroup.redistrictingGroupList)
    while len(contiguousRegions) > 1:
        for isolatedRegion in contiguousRegions:
            closestRegion = findClosestGeometry(originGeometry=isolatedRegion,
                                                otherGeometries=[region for region in contiguousRegions if
                                                                 region is not isolatedRegion])

            closestGroupInIsolatedRegion = findClosestGeometry(originGeometry=closestRegion,
                                                               otherGeometries=isolatedRegion)
            closestGroupInClosestRegion = findClosestGeometry(originGeometry=isolatedRegion,
                                                              otherGeometries=closestRegion)

            # these two may already be neighbors from a previous iteration of this loop, so we check
            if not closestGroupInIsolatedRegion.isNeighbor(closestGroupInClosestRegion):
                closestGroupInIsolatedRegion.addNeighbors(neighbors=[closestGroupInClosestRegion])
                closestGroupInClosestRegion.addNeighbors(neighbors=[closestGroupInIsolatedRegion])
        contiguousRegions = findContiguousGroupsOfGraphObjects(RedistrictingGroup.redistrictingGroupList)


def assignNeighboringRedistrictingGroupsForAllRedistrictingGroups():
    for redistrictingGroupToCheck in RedistrictingGroup.redistrictingGroupList:
        for redistrictingGroupToCheckAgainst in RedistrictingGroup.redistrictingGroupList:
            if redistrictingGroupToCheck != redistrictingGroupToCheckAgainst:
                if intersectingGeometries(redistrictingGroupToCheck, redistrictingGroupToCheckAgainst):
                    redistrictingGroupToCheck.addNeighbors([redistrictingGroupToCheckAgainst])

    attachOrphanRedistrictingGroupsToClosestNeighbor()


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
        atomicBlocksForGroup = createAtomicBlocksFromBlockList(blockList=blockContainer.children)
        blockContainer.children = atomicBlocksForGroup  # this triggers a block container update
        count += 1


def validateAllRedistrictingGroups():
    validateContiguousRedistrictingGroups(RedistrictingGroup.redistrictingGroupList)

    for redistrictingGroup in RedistrictingGroup.redistrictingGroupList:
        redistrictingGroup.validateNeighborLists()


def createRedistrictingGroupsWithAtomicBlocksFromCensusData(censusData):
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
            redistrictingGroupWithCountyFIPS.children.append(blockFromData)
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
    assignNeighboringBlocksToBlocksForAllRedistrictingGroups()

    # split non-contiguous redistricting groups
    splitNonContiguousRedistrictingGroups()

    # find and set neighboring geometries
    assignNeighboringRedistrictingGroupsForAllRedistrictingGroups()

    validateAllRedistrictingGroups()
    validateAllAtomicBlocks()

    return RedistrictingGroup.redistrictingGroupList
