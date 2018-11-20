from exportData.displayShapes import plotGraphObjectGroups, plotPolygons, plotRedistrictingGroups
from shapely.geometry import Polygon
from formatData.atomicBlock import createAtomicBlocksFromBlockList, validateAllAtomicBlocks, \
    assignNeighborBlocksFromCandiateBlocks
from formatData.blockBorderGraph import BlockBorderGraph
from formatData.graphObject import GraphObject
from geographyHelper import findContiguousGroupsOfGraphObjects, findClosestGeometry, intersectingGeometries, Alignment, \
    mostCardinalOfGeometries, CardinalDirection, geometryFromMultipleGeometries, getPolygonThatIntersectsGeometry, \
    geometryFromMultiplePolygons, doesPolygonContainTheOther
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

    def getGraphSplits(self, shouldDrawGraph=False, countForProgress=None):
        if countForProgress is not None:
            tqdm.write('         *** Finding seams for graph split {0} - GraphId: {1} ***'
                       .format(countForProgress, self.graphId))
        with tqdm(total=4) as pbar:
            self.fillPopulationEnergyGraph(Alignment.northSouth)
            pbar.update(1)
            northSouthSplit = self.getPopulationEnergySplit(Alignment.northSouth, shouldDrawGraph=shouldDrawGraph)
            pbar.update(1)
            self.clearPopulationEnergyGraph()

            self.fillPopulationEnergyGraph(Alignment.westEast)
            pbar.update(1)
            westEastSplit = self.getPopulationEnergySplit(Alignment.westEast, shouldDrawGraph=shouldDrawGraph)
            pbar.update(1)
            self.clearPopulationEnergyGraph()

        if countForProgress is not None:
            tqdm.write('         *** Re-assigning neighboring blocks to new Redistricting Groups in {0} ***'.format(
                countForProgress))

        northWestSplit = RedistrictingGroup(
            childrenBlocks=[group for group in northSouthSplit[0] if group in westEastSplit[0]])
        northWestSplit.removeOutdatedNeighborConnections(borderBlocksOnly=True)

        northEastSplit = RedistrictingGroup(
            childrenBlocks=[group for group in northSouthSplit[0] if group in westEastSplit[1]])
        northEastSplit.removeOutdatedNeighborConnections(borderBlocksOnly=True)

        southWestSplit = RedistrictingGroup(
            childrenBlocks=[group for group in northSouthSplit[1] if group in westEastSplit[0]])
        southWestSplit.removeOutdatedNeighborConnections(borderBlocksOnly=True)

        southEastSplit = RedistrictingGroup(
            childrenBlocks=[group for group in northSouthSplit[1] if group in westEastSplit[1]])
        southEastSplit.removeOutdatedNeighborConnections(borderBlocksOnly=True)

        if shouldDrawGraph:
            plotRedistrictingGroups(
                redistrictingGroups=[northWestSplit, northEastSplit, southWestSplit, southEastSplit])

        return (northWestSplit,
                northEastSplit,
                southWestSplit,
                southEastSplit)

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

                lowestPopulationEnergyNeighbor = min(previousNeighbors, key=lambda block: block.populationEnergy)

                blockToActOn.populationEnergy = lowestPopulationEnergyNeighbor.populationEnergy + blockToActOn.population
                remainingObjects.remove(blockToActOn)

    def clearPopulationEnergyGraph(self):
        for child in self.children:
            child.populationEnergy = 0

    def getPopulationEnergySplit(self, alignment, shouldDrawGraph=False):
        polygonSplits = self.getPopulationEnergyPolygonSplit(alignment=alignment, shouldDrawGraph=shouldDrawGraph)
        aSplitPolygon = polygonSplits[0]
        bSplitPolygon = polygonSplits[1]
        seamSplitPolygon = polygonSplits[2]

        aSplit = []
        bSplit = []
        seamSplit = []
        for block in self.children:
            if doesPolygonContainTheOther(container=aSplitPolygon, target=block.geometry, ignoreInteriors=False):
                aSplit.append(block)
            elif doesPolygonContainTheOther(container=bSplitPolygon, target=block.geometry, ignoreInteriors=False):
                bSplit.append(block)
            elif doesPolygonContainTheOther(container=seamSplitPolygon, target=block.geometry, ignoreInteriors=False):
                seamSplit.append(block)
            else:
                plotPolygons([aSplitPolygon, bSplitPolygon, seamSplitPolygon, block.geometry])
                raise RuntimeError("Couldn't find a container for block: {0}".format(block.geometry))

        aSplitPopulation = sum(block.population for block in aSplit)
        bSplitPopulation = sum(block.population for block in bSplit)

        if aSplitPopulation < bSplitPopulation:
            aSplit += seamSplit
        else:
            bSplit += seamSplit

        if shouldDrawGraph:
            plotGraphObjectGroups(graphObjectGroups=[aSplit, bSplit])

        return (aSplit, bSplit)

    def getPopulationEnergyPolygonSplit(self, alignment, shouldDrawGraph=False):
        lowestEnergySeam = self.getLowestPopulationEnergySeam(alignment)

        seamSplitPolygon = geometryFromMultipleGeometries(geometryList=lowestEnergySeam)
        polygonWithoutSeam = self.geometry.difference(seamSplitPolygon)
        splitPolygons = list(polygonWithoutSeam)

        if alignment is Alignment.northSouth:
            aSplitRepresentativeBlockDirection = CardinalDirection.north
            bSplitRepresentativeBlockDirection = CardinalDirection.south
        else:
            aSplitRepresentativeBlockDirection = CardinalDirection.west
            bSplitRepresentativeBlockDirection = CardinalDirection.east

        aSplitRepresentativeBlock = mostCardinalOfGeometries(geometryList=self.borderChildren,
                                                             direction=aSplitRepresentativeBlockDirection)

        bSplitRepresentativeBlock = mostCardinalOfGeometries(geometryList=self.borderChildren,
                                                             direction=bSplitRepresentativeBlockDirection)

        aSplitPolygon = getPolygonThatIntersectsGeometry(polygonList=splitPolygons,
                                                         targetGeometry=aSplitRepresentativeBlock)
        bSplitPolygon = getPolygonThatIntersectsGeometry(polygonList=splitPolygons,
                                                         targetGeometry=bSplitRepresentativeBlock)
        leftOverPolygons = [geometry for geometry in splitPolygons if
                            geometry is not aSplitPolygon and geometry is not bSplitPolygon]
        if aSplitPolygon is bSplitPolygon:
            plotPolygons([self.geometry, aSplitPolygon, bSplitPolygon, seamSplitPolygon,
                          aSplitRepresentativeBlock.geometry,
                          bSplitRepresentativeBlock.geometry])
            raise RuntimeError('The split a and b are the same polygon')
        if len(leftOverPolygons) is not len(splitPolygons) - 2:
            raise RuntimeError('Missing some polygons for mapping. Split polygons: {0} Left over polygon: {1}'
                               .format(len(splitPolygons), len(leftOverPolygons)))
        seamSplitPolygon = geometryFromMultiplePolygons(polygonList=[seamSplitPolygon] + leftOverPolygons)

        if shouldDrawGraph:
            plotPolygons([aSplitPolygon, bSplitPolygon, seamSplitPolygon])

        return (aSplitPolygon, bSplitPolygon, seamSplitPolygon)

    def getLowestPopulationEnergySeam(self, alignment, shouldDrawGraph=False):
        if alignment is Alignment.northSouth:
            startingCandidates = self.easternChildBlocks
            borderBlocksToAvoid = self.northernChildBlocks + self.southernChildBlocks + startingCandidates
            finishCandidates = self.westernChildBlocks
        else:
            startingCandidates = self.southernChildBlocks
            borderBlocksToAvoid = self.westernChildBlocks + self.easternChildBlocks + startingCandidates
            finishCandidates = self.northernChildBlocks

        blockToActOn = min(startingCandidates, key=lambda block: block.populationEnergy)

        lowestPopulationEnergySeam = [blockToActOn]
        finishedSeam = False
        count = 1
        while not finishedSeam:
            if alignment is Alignment.northSouth:
                primaryNeighborCandidates = blockToActOn.westernNeighbors
            else:
                primaryNeighborCandidates = blockToActOn.northernNeighbors
            neighborCandidates = [block for block in primaryNeighborCandidates
                                  if block not in lowestPopulationEnergySeam and
                                  block not in borderBlocksToAvoid]

            if len(neighborCandidates) is 0:
                neighborCandidates = [block for block in blockToActOn.allNeighbors
                                      if block not in lowestPopulationEnergySeam and
                                      block not in borderBlocksToAvoid]

            if len(neighborCandidates) is 0:
                raise RuntimeError("Can't find a {0} path through {1}".format(alignment, self.graphId))

            lowestPopulationEnergyNeighbor = min(neighborCandidates, key=lambda block: block.populationEnergy)
            if shouldDrawGraph:
                plotGraphObjectGroups(graphObjectGroups=[self.children,
                                                         neighborCandidates,
                                                         startingCandidates,
                                                         finishCandidates,
                                                         [],
                                                         [],
                                                         [],
                                                         lowestPopulationEnergySeam,
                                                         [lowestPopulationEnergyNeighbor]],
                                      showGraphHeatmapForFirstGroup=True,
                                      saveImages=True,
                                      saveDescription='SeamFinding{0}'.format(count))

            blockToActOn = lowestPopulationEnergyNeighbor

            lowestPopulationEnergySeam.append(blockToActOn)

            if blockToActOn in finishCandidates:
                finishedSeam = True

            count += 1
        return lowestPopulationEnergySeam

    def assignNeighboringBlocksToBlocks(self):
        with tqdm(total=len(self.children)) as pbar:
            threadPool = Pool(4)
            threadPool.starmap(assignNeighborBlocksFromCandiateBlocks,
                               zip(self.children,
                                   repeat(self.children),
                                   repeat(pbar)))

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
        redistrictingGroup.assignNeighboringBlocksToBlocks()
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
        if type(redistrictingGroup.geometry) is not Polygon:
            raise RuntimeError(
                "Found a redistricting group without a Polygon geometry: {0}".format(redistrictingGroup.graphId))


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
