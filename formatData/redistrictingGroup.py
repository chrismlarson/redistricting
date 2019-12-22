from exportData.displayShapes import plotGraphObjectGroups, plotPolygons, plotRedistrictingGroups, \
    plotBlocksForRedistrictingGroup
from shapely.geometry import MultiPolygon
from exportData.exportData import saveDataToFileWithDescription
from formatData.atomicBlock import createAtomicBlocksFromBlockList, validateAllAtomicBlocks, \
    assignNeighborBlocksFromCandidateBlocks
from formatData.blockBorderGraph import BlockBorderGraph
from formatData.graphObject import GraphObject
from geographyHelper import findContiguousGroupsOfGraphObjects, findClosestGeometry, intersectingGeometries, Alignment, \
    mostCardinalOfGeometries, CardinalDirection, polygonFromMultipleGeometries, polygonFromMultiplePolygons, \
    doesPolygonContainTheOther, getPolygonThatContainsGeometry, intersectingPolygons, allIntersectingPolygons
from enum import Enum
from censusData import censusBlock
from multiprocessing.dummy import Pool
from itertools import repeat
from tqdm import tqdm


class RedistrictingGroup(BlockBorderGraph, GraphObject):
    def __init__(self, childrenBlocks, allowEmpty=False):
        BlockBorderGraph.__init__(self)
        self.children = childrenBlocks
        GraphObject.__init__(self, centerOfObject=self.geometry.centroid)
        if not allowEmpty and len(self.children) == 0:
            raise AttributeError(
                "Can't create a redistricting group with no children. GraphId: {0}".format(self.graphId))
        self.previousParentId = None

    def __setstate__(self, state):
        # if not hasattr(state, 'previousParentId'):
        #     state['previousParentId'] = None
        super(RedistrictingGroup, self).__setstate__(state)

    def updateBlockContainerData(self):
        super(RedistrictingGroup, self).updateBlockContainerData()
        self.updateCenterOfObject(self.geometry.centroid)

    def removeWaterBlocks(self):
        nonWaterBlocks = [block for block in self.children if block.isWater is False]
        waterBlocks = [block for block in self.children if block.isWater is True]
        if any([waterBlock for waterBlock in waterBlocks if waterBlock.population > 0]):
            raise ValueError('Water block had a population')
        self.children = nonWaterBlocks

    def attachOrphanBlocksToClosestNeighbor(self):
        orphanBlocks = self.findOrphanBlocks()
        for orphanBlock in orphanBlocks:
            otherBlocks = [block for block in self.children if block is not orphanBlock]
            closestBlock = findClosestGeometry(originGeometry=self, otherGeometries=otherBlocks)
            orphanBlock.addNeighbors(neighbors=[closestBlock])
            closestBlock.addNeighbors(neighbors=[orphanBlock])

    def findOrphanBlocks(self):
        return [block for block in self.children if block.hasNeighbors is False]

    def createRedistrictingGroupForEachChild(self):
        tqdm.write('            *** Creating Redistricting Group for each child: {0} ***'.format(self.graphId))
        childGroups = []
        for redistrictingGroupChild in self.children:
            redistrictingGroupChild.clearNeighborGraphObjects()
            childGroups.append(RedistrictingGroup(childrenBlocks=[redistrictingGroupChild]))
        return childGroups

    def getGraphSplits(self, alignment=Alignment.all, shouldDrawGraph=False, countForProgress=None):
        if len(self.children) == 1:
            raise RuntimeError("Can't split RedistrictingGroup with a single child. GraphId: {0}".format(self.graphId))

        if countForProgress is None:
            pbar = None
        else:
            tqdm.write('         *** Finding seams for graph split {0} - GraphId: {1} - Block count: {2} ***'
                       .format(countForProgress, self.graphId, len(self.children)))
            if alignment is Alignment.all:
                progressTotal = 4
            else:
                progressTotal = 2
            pbar = tqdm(total=progressTotal)

        northSouthSplit = None
        westEastSplit = None

        if alignment is Alignment.all or alignment is Alignment.northSouth:
            self.fillPopulationEnergyGraph(Alignment.northSouth)
            if pbar is not None:
                pbar.update(1)
            northSouthSplitResult = self.getPopulationEnergySplit(Alignment.northSouth, shouldDrawGraph=shouldDrawGraph)
            northSouthSplitResultType = northSouthSplitResult[0]
            if northSouthSplitResultType is SplitType.NoSplit:
                northSouthSplit = None
            elif northSouthSplitResultType is SplitType.ForceSplitAllBlocks:
                return self.createRedistrictingGroupForEachChild()
            else:
                northSouthSplit = northSouthSplitResult[1]
            if pbar is not None:
                pbar.update(1)
            self.clearPopulationEnergyGraph()

        if alignment is Alignment.all or alignment is Alignment.westEast:
            self.fillPopulationEnergyGraph(Alignment.westEast)
            if pbar is not None:
                pbar.update(1)
            westEastSplitResult = self.getPopulationEnergySplit(Alignment.westEast, shouldDrawGraph=shouldDrawGraph)
            westEastSplitResultType = westEastSplitResult[0]
            if westEastSplitResultType is SplitType.NoSplit:
                westEastSplit = None
            elif westEastSplitResultType is SplitType.ForceSplitAllBlocks:
                return self.createRedistrictingGroupForEachChild()
            else:
                westEastSplit = westEastSplitResult[1]
            if pbar is not None:
                pbar.update(1)
            self.clearPopulationEnergyGraph()

        if pbar is not None:
            pbar.close()

        if northSouthSplit is None and westEastSplit is None:
            return self.createRedistrictingGroupForEachChild()

        if countForProgress is not None:
            tqdm.write('            *** Creating new Redistricting Groups in {0} ***'.format(countForProgress))

        splitGroups = []
        if northSouthSplit and not westEastSplit:
            northSplit = RedistrictingGroup(childrenBlocks=northSouthSplit[0])
            splitGroups.append(northSplit)

            southSplit = RedistrictingGroup(childrenBlocks=northSouthSplit[1])
            splitGroups.append(southSplit)
        elif not northSouthSplit and westEastSplit:
            westSplit = RedistrictingGroup(childrenBlocks=westEastSplit[0])
            splitGroups.append(westSplit)

            eastSplit = RedistrictingGroup(childrenBlocks=westEastSplit[1])
            splitGroups.append(eastSplit)
        else:
            northWestSplitChildren = [group for group in northSouthSplit[0] if group in westEastSplit[0]]
            northEastSplitChildren = [group for group in northSouthSplit[0] if group in westEastSplit[1]]
            southWestSplitChildren = [group for group in northSouthSplit[1] if group in westEastSplit[0]]
            southEastSplitChildren = [group for group in northSouthSplit[1] if group in westEastSplit[1]]

            splitChildrenList = [northWestSplitChildren,
                                 northEastSplitChildren,
                                 southWestSplitChildren,
                                 southEastSplitChildren]

            for splitChildren in splitChildrenList:
                if len(splitChildren) > 0:
                    splitGroup = RedistrictingGroup(childrenBlocks=splitChildren)
                    splitGroups.append(splitGroup)

        if countForProgress is not None:
            tqdm.write(
                '            *** Re-assigning neighboring blocks to new Redistricting Groups in {0} ***'.format(
                    countForProgress))

        # check for orphan blocks and validate existing neighboring blocks and attach to intersecting group
        splitGroups = reorganizeAtomicBlockBetweenRedistrictingGroups(redistrictingGroups=splitGroups)

        for splitGroup in splitGroups:
            if shouldDrawGraph:
                plotBlocksForRedistrictingGroup(splitGroup)
            splitGroup.removeOutdatedNeighborConnections()
            splitGroup.validateBlockNeighbors()

        if shouldDrawGraph:
            plotRedistrictingGroups(redistrictingGroups=splitGroups)

        return splitGroups

    def fillPopulationEnergyGraph(self, alignment):
        remainingObjects = self.children.copy()
        if alignment is Alignment.northSouth:
            blocksToActOn = self.westernChildBlocks
        else:
            blocksToActOn = self.northernChildBlocks

        # work west to east or north to south
        if len(blocksToActOn) > 0:
            for blockToActOn in blocksToActOn:
                blockToActOn.populationEnergy = blockToActOn.population
                remainingObjects.remove(blockToActOn)

            filledBlocks = blocksToActOn.copy()
            while len(remainingObjects) > 0:
                neighborsOfBlocks = getNeighborsForGraphObjectsInList(graphObjects=blocksToActOn,
                                                                      inList=remainingObjects)
                if len(neighborsOfBlocks) > 0:
                    blocksToActOn = neighborsOfBlocks
                else:
                    saveDataToFileWithDescription(data=self,
                                                  censusYear='',
                                                  stateName='',
                                                  descriptionOfInfo='ErrorCase-NoNeighborsForGraphGroups')
                    plotGraphObjectGroups([self.children, blocksToActOn], showDistrictNeighborConnections=True)
                    plotBlocksForRedistrictingGroup(self, showBlockNeighborConnections=True)
                    raise RuntimeError("Can't find neighbors for graph objects")

                blocksToActOnThisRound = blocksToActOn.copy()
                while len(blocksToActOnThisRound) > 0:
                    blocksActedUpon = []
                    for blockToActOn in blocksToActOnThisRound:
                        previousNeighbors = getNeighborsForGraphObjectsInList(graphObjects=[blockToActOn],
                                                                              inList=filledBlocks)
                        if len(previousNeighbors) is not 0:
                            lowestPopulationEnergyNeighbor = min(previousNeighbors,
                                                                 key=lambda block: block.populationEnergy)

                            blockToActOn.populationEnergy = lowestPopulationEnergyNeighbor.populationEnergy + blockToActOn.population
                            remainingObjects.remove(blockToActOn)
                            blocksActedUpon.append(blockToActOn)
                            filledBlocks.append(blockToActOn)
                    blocksToActOnThisRound = [block for block in blocksToActOnThisRound if block not in blocksActedUpon]
                    if len(blocksActedUpon) == 0:
                        saveDataToFileWithDescription(data=self,
                                                      censusYear='',
                                                      stateName='',
                                                      descriptionOfInfo='ErrorCase-BlocksCanNotFindPreviousNeighbor')
                        plotGraphObjectGroups([filledBlocks, blocksToActOnThisRound])
                        plotBlocksForRedistrictingGroup(self, showBlockNeighborConnections=True, showGraphHeatmap=True,
                                                        showBlockGraphIds=True)
                        raise ReferenceError("Can't find previous neighbor for {0}".format(blocksToActOnThisRound))

        # add population to surrounding neighbors population energy
        # this is to help create smoother graphs in urban areas
        for block in self.children:
            for neighborBlock in block.allNeighbors:
                neighborBlock.populationEnergy += block.population

    def clearPopulationEnergyGraph(self):
        for child in self.children:
            child.populationEnergy = 0

    def getPopulationEnergySplit(self, alignment, shouldDrawGraph=False):
        polygonSplitResult = self.getPopulationEnergyPolygonSplit(alignment=alignment, shouldDrawGraph=shouldDrawGraph)
        polygonSplitResultType = polygonSplitResult[0]
        if polygonSplitResultType is SplitType.NoSplit:
            return SplitType.NoSplit, None
        elif polygonSplitResultType is SplitType.ForceSplitAllBlocks:
            return SplitType.ForceSplitAllBlocks, None

        polygonSplits = polygonSplitResult[1]

        aSplitPolygon = polygonSplits[0]
        bSplitPolygon = polygonSplits[1]

        if polygonSplitResultType is SplitType.SplitIncludedInSeam:
            seamOnEdge = True
            seamSplitPolygon = None
        else:
            seamOnEdge = False
            seamSplitPolygon = polygonSplitResult[2]

        aSplit = []
        bSplit = []
        seamSplit = []
        for block in self.children:
            if doesPolygonContainTheOther(container=aSplitPolygon, target=block.geometry, ignoreInteriors=False):
                aSplit.append(block)
            elif doesPolygonContainTheOther(container=bSplitPolygon, target=block.geometry, ignoreInteriors=False):
                bSplit.append(block)
            elif not seamOnEdge and doesPolygonContainTheOther(container=seamSplitPolygon, target=block.geometry,
                                                               ignoreInteriors=False):
                seamSplit.append(block)
            # elif allIntersectingPolygons(seamSplitPolygon, block.geometry):
            #     seamSplit.append(block)
            #     plotPolygons([block.geometry])
            else:
                saveDataToFileWithDescription(data=[self, alignment, aSplitPolygon, bSplitPolygon, seamSplitPolygon,
                                                    block.geometry, seamOnEdge, polygonSplitResultType],
                                              censusYear='',
                                              stateName='',
                                              descriptionOfInfo='ErrorCase-CouldNotFindContainerForBlock')
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

        return SplitType.NormalSplit, (aSplit, bSplit)

    def getPopulationEnergyPolygonSplit(self, alignment, shouldDrawGraph=False):
        finishingBlocksToAvoid = []
        while True:
            lowestEnergySeamResult = self.getLowestPopulationEnergySeam(alignment=alignment,
                                                                        finishingBlocksToAvoid=finishingBlocksToAvoid)
            if lowestEnergySeamResult is None:
                return SplitType.NoSplit, None
            lowestEnergySeam = lowestEnergySeamResult[0]
            energySeamFinishingBlock = lowestEnergySeamResult[1]
            energySeamStartingEnergy = lowestEnergySeamResult[2]

            seamSplitPolygon = polygonFromMultipleGeometries(geometryList=lowestEnergySeam)
            polygonWithoutSeam = self.geometry.difference(seamSplitPolygon)

            # if the polygon without the seam is empty, that means we have a small enough redistricting group where
            # we need to break it up completely. Because our seams can no longer break up any further.
            if polygonWithoutSeam.is_empty:
                return SplitType.ForceSplitAllBlocks, None

            if type(polygonWithoutSeam) is MultiPolygon:
                seamOnEdge = False
                splitPolygons = list(polygonWithoutSeam)
            else:
                seamOnEdge = True
                splitPolygons = [polygonWithoutSeam, seamSplitPolygon]

            if alignment is Alignment.northSouth:
                aSplitRepresentativeBlockDirection = CardinalDirection.north
                bSplitRepresentativeBlockDirection = CardinalDirection.south
            else:
                aSplitRepresentativeBlockDirection = CardinalDirection.west
                bSplitRepresentativeBlockDirection = CardinalDirection.east

            # Identify which polygon is in which direction
            # Note: Need to make sure we don't select a block in the seam so we supply a list without those blocks
            #   If the seam is completely on the edge though, let's include the seam
            if seamOnEdge:
                borderChildrenRepresentativeCandidates = self.borderChildren
            else:
                borderChildrenRepresentativeCandidates = [child for child in self.borderChildren if
                                                          child not in lowestEnergySeam]

            if len(borderChildrenRepresentativeCandidates) == 0:
                return SplitType.NoSplit, None

            aSplitRepresentativeBlock = mostCardinalOfGeometries(geometryList=borderChildrenRepresentativeCandidates,
                                                                 direction=aSplitRepresentativeBlockDirection)

            bSplitRepresentativeBlock = mostCardinalOfGeometries(geometryList=borderChildrenRepresentativeCandidates,
                                                                 direction=bSplitRepresentativeBlockDirection)

            aSplitPolygon = getPolygonThatContainsGeometry(polygonList=splitPolygons,
                                                           targetGeometry=aSplitRepresentativeBlock,
                                                           useTargetRepresentativePoint=True)
            bSplitPolygon = getPolygonThatContainsGeometry(polygonList=splitPolygons,
                                                           targetGeometry=bSplitRepresentativeBlock,
                                                           useTargetRepresentativePoint=True)
            leftOverPolygons = [geometry for geometry in splitPolygons if
                                geometry is not aSplitPolygon and geometry is not bSplitPolygon]
            if aSplitPolygon is None or bSplitPolygon is None:
                plotPolygons(splitPolygons + [aSplitRepresentativeBlock.geometry, bSplitRepresentativeBlock.geometry])
                saveDataToFileWithDescription(data=self,
                                              censusYear='',
                                              stateName='',
                                              descriptionOfInfo='ErrorCase-AorBSplitIsNone')
                raise RuntimeError('Split a or b not found')

            if aSplitPolygon is bSplitPolygon:
                finishingBlocksToAvoid.append(energySeamFinishingBlock)
                continue

            if len(leftOverPolygons) is not len(splitPolygons) - 2:
                saveDataToFileWithDescription(data=self,
                                              censusYear='',
                                              stateName='',
                                              descriptionOfInfo='ErrorCase-MissingPolygons')
                raise RuntimeError('Missing some polygons for mapping. Split polygons: {0} Left over polygon: {1}'
                                   .format(len(splitPolygons), len(leftOverPolygons)))

            polygonSplits = (aSplitPolygon, bSplitPolygon)

            if shouldDrawGraph:
                plotPolygons(polygonSplits)

            if seamOnEdge:
                return SplitType.SplitIncludedInSeam, polygonSplits, None, energySeamStartingEnergy
            else:
                seamSplitPolygon = polygonFromMultiplePolygons(polygonList=[seamSplitPolygon] + leftOverPolygons)
                return SplitType.NormalSplit, polygonSplits, seamSplitPolygon, energySeamStartingEnergy

    def getLowestPopulationEnergySeam(self, alignment, shouldDrawGraph=False, finishingBlocksToAvoid=None):
        if alignment is Alignment.northSouth:
            startingCandidates = self.easternChildBlocks
            borderBlocksToAvoid = self.northernChildBlocks + self.southernChildBlocks + startingCandidates
            finishCandidates = self.westernChildBlocks
        else:
            startingCandidates = self.southernChildBlocks
            borderBlocksToAvoid = self.westernChildBlocks + self.easternChildBlocks + startingCandidates
            finishCandidates = self.northernChildBlocks

        if finishingBlocksToAvoid:
            finishCandidates = [candidate for candidate in finishCandidates if candidate not in finishingBlocksToAvoid]

        if len(startingCandidates) == 0 or len(finishCandidates) == 0:
            return None

        startingBlock = min(startingCandidates, key=lambda block: block.populationEnergy)
        startingBlockEnergy = startingBlock.populationEnergy
        blockToActOn = startingBlock

        lowestPopulationEnergySeam = [blockToActOn]
        failedStartingBlocks = []
        avoidingAdjacentBorderBlocks = True
        finishedSeam = False
        finishingBlock = None
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

            # If we don't have any neighbors in the direction we're headed,
            # we need to find the next best block candidate
            if len(neighborCandidates) is 0:
                failedStartingBlocks.append(startingBlock)

                remainingStartingCandidates = [startingCandidate for startingCandidate in startingCandidates if
                                               startingCandidate not in failedStartingBlocks]

                # If there are no more starting candidates, remove the adjacent border blocks to avoid rule
                if len(remainingStartingCandidates) is 0:
                    if avoidingAdjacentBorderBlocks:
                        avoidingAdjacentBorderBlocks = False
                        borderBlocksToAvoid = startingCandidates
                        failedStartingBlocks = []
                        startingBlock = min(startingCandidates, key=lambda block: block.populationEnergy)
                        blockToActOn = startingBlock
                        lowestPopulationEnergySeam = [blockToActOn]
                        continue
                    else:  # not sure there is anything more we can do but split everything up
                        # plotGraphObjectGroups([self.children, failedStartingBlocks, finishingBlocksToAvoid])
                        tqdm.write("Can't find a {0} path through {1}. Tried and failed on {2} starting blocks"
                                   .format(alignment, self.graphId, len(failedStartingBlocks)))
                        return None

                startingBlock = min(remainingStartingCandidates, key=lambda block: block.populationEnergy)
                blockToActOn = startingBlock
                lowestPopulationEnergySeam = [blockToActOn]
                continue

            lowestPopulationEnergyNeighbor = min(neighborCandidates, key=lambda block: block.populationEnergy)
            if shouldDrawGraph:
                plotGraphObjectGroups(graphObjectGroups=[self.children,
                                                         lowestPopulationEnergySeam,
                                                         neighborCandidates,
                                                         [lowestPopulationEnergyNeighbor],
                                                         failedStartingBlocks],
                                      showGraphHeatmapForFirstGroup=True,
                                      saveImages=True,
                                      saveDescription='SeamFinding{0}-{1}-{2}'.format(count, alignment, id(self)))

            blockToActOn = lowestPopulationEnergyNeighbor

            lowestPopulationEnergySeam.append(blockToActOn)

            if blockToActOn in finishCandidates:
                finishedSeam = True
                finishingBlock = blockToActOn

            count += 1
        return lowestPopulationEnergySeam, finishingBlock, startingBlockEnergy

    def validateBlockNeighbors(self):
        contiguousRegions = findContiguousGroupsOfGraphObjects(self.children)
        if len(contiguousRegions) > 1:
            saveDataToFileWithDescription(data=[self, contiguousRegions],
                                          censusYear='',
                                          stateName='',
                                          descriptionOfInfo='ErrorCase-BlocksNotContiguous')
            plotGraphObjectGroups(contiguousRegions, showDistrictNeighborConnections=True)
            plotBlocksForRedistrictingGroup(self, showBlockNeighborConnections=True, showBlockGraphIds=True)
            raise RuntimeError("Don't have a contiguous set of AtomicBlocks. There are {0} distinct groups.".format(
                len(contiguousRegions)))

        for block in self.children:
            neighborBlocksNotInGroup = [neighborBlock for neighborBlock in block.allNeighbors
                                        if neighborBlock not in self.children]
            if len(neighborBlocksNotInGroup):
                saveDataToFileWithDescription(data=[self, block],
                                              censusYear='',
                                              stateName='',
                                              descriptionOfInfo='ErrorCase-BlockHasNeighborOutsideRedistrictingGroup')
                plotBlocksForRedistrictingGroup(self, showBlockNeighborConnections=True, showBlockGraphIds=True)
                raise RuntimeError("Some blocks have neighbor connections with block outside the redistricting group")

    def assignNeighboringBlocksToBlocks(self):
        with tqdm(total=len(self.children)) as pbar:
            threadPool = Pool(4)
            threadPool.starmap(assignNeighborBlocksFromCandidateBlocks,
                               zip(self.children,
                                   repeat(self.children),
                                   repeat(pbar)))

    def __lt__(self, other):
        if isinstance(other, RedistrictingGroup):
            return self.graphId < other.graphId
        return NotImplemented('Can only do a less than comparison with another RedistrictingGroup')


class SplitType(Enum):
    NoSplit = 0
    NormalSplit = 1
    SplitIncludedInSeam = 2
    ForceSplitAllBlocks = 3


def getNeighborsForGraphObjectsInList(graphObjects, inList):
    neighborList = []
    for graphObject in graphObjects:
        for neighborObject in graphObject.allNeighbors:
            if neighborObject in inList and neighborObject not in neighborList and neighborObject not in graphObjects:
                neighborList.append(neighborObject)
    return neighborList


def attachOrphanBlocksToClosestNeighborForRedistrictingGroups(redistrictingGroupList):
    for blockContainer in redistrictingGroupList:
        blockContainer.attachOrphanBlocksToClosestNeighbor()


def reorganizeAtomicBlockBetweenRedistrictingGroups(redistrictingGroups):
    for redistrictingGroup in redistrictingGroups:
        for borderBlock in redistrictingGroup.borderChildren:
            borderBlock.removeNonIntersectingNeighbors()

    atomicBlockGroupDict = {}
    for redistrictingGroup in redistrictingGroups:
        atomicBlockGroupDict[redistrictingGroup.graphId] = redistrictingGroup.children.copy()

    atomicBlockGroups = atomicBlockGroupDict.values()
    for atomicBlockGroup in atomicBlockGroups:
        contiguousRegions = findContiguousGroupsOfGraphObjects(atomicBlockGroup)
        while len(contiguousRegions) > 1:
            smallestContiguousRegion = min(contiguousRegions,
                                           key=lambda contiguousRegion: len(contiguousRegion))
            smallestContiguousRegionPolygon = polygonFromMultipleGeometries(smallestContiguousRegion)

            otherRegion = None
            otherSplitChildrenList = [x for x in atomicBlockGroups if x is not atomicBlockGroup]
            for otherSplitChildren in otherSplitChildrenList:
                otherSplitChildrenPolygon = polygonFromMultipleGeometries(otherSplitChildren)
                if intersectingPolygons(smallestContiguousRegionPolygon, otherSplitChildrenPolygon):
                    otherRegion = otherSplitChildren
                    break

            if otherRegion is None:
                allBlocksInOtherSplits = [block for blockList in otherSplitChildrenList for block in blockList]
                closestBlock = findClosestGeometry(smallestContiguousRegionPolygon, allBlocksInOtherSplits)
                closestSplit = next((blockList for blockList in otherSplitChildrenList if closestBlock in blockList),
                                    None)
                otherRegion = closestSplit

            for childBlock in smallestContiguousRegion:
                atomicBlockGroup.remove(childBlock)
                childBlock.removeNeighborConnections()

                otherRegion.append(childBlock)
                assignNeighborBlocksFromCandidateBlocks(block=childBlock, candidateBlocks=otherRegion)
            contiguousRegions = findContiguousGroupsOfGraphObjects(atomicBlockGroup)

    for key, value in atomicBlockGroupDict.items():
        groupWithId = next((redistrictingGroup for redistrictingGroup in redistrictingGroups
                            if redistrictingGroup.graphId == key), None)
        groupWithId.children = value

    for redistrictingGroup in redistrictingGroups:
        redistrictingGroup.attachOrphanBlocksToClosestNeighbor()

    return redistrictingGroups


# def updateAllBlockContainersData():
#     tqdm.write('*** Updating All Block Container Data ***')
#     with tqdm(total=len(RedistrictingGroup.redistrictingGroupList)) as pbar:
#         for blockContainer in RedistrictingGroup.redistrictingGroupList:
#             tqdm.write('   *** One more ***')
#             blockContainer.updateBlockContainerData()
#             pbar.update(1)


def removeWaterBlocksFromRedistrictingGroups(redistrictingGroupList):
    tqdm.write('\n')
    tqdm.write('*** Removing Water Blocks From All Redistricting Groups ***')
    with tqdm(total=len(redistrictingGroupList)) as pbar:
        for redistrictingGroup in redistrictingGroupList:
            redistrictingGroup.removeWaterBlocks()
            pbar.update(1)


def splitNonContiguousRedistrictingGroups(redistrictingGroupList):
    tqdm.write('\n')
    tqdm.write('*** Splitting Non-contiguous Redistricting Groups ***')
    groupsToRemove = []
    with tqdm(total=len(redistrictingGroupList)) as pbar:
        for redistrictingGroup in redistrictingGroupList:
            contiguousGroups = findContiguousGroupsOfGraphObjects(redistrictingGroup.children)

            if len(contiguousGroups) > 1:
                groupsToRemove.append(redistrictingGroup)
                for contiguousGroup in contiguousGroups:
                    splitGroup = RedistrictingGroup(childrenBlocks=contiguousGroup)
                    redistrictingGroupList.append(splitGroup)
            pbar.update(1)

    for groupToRemove in groupsToRemove:
        redistrictingGroupList.remove(groupToRemove)


def assignNeighboringBlocksToBlocksForRedistrictingGroups(redistrictingGroupList):
    tqdm.write('\n')
    tqdm.write('*** Assigning Neighbors To All Census Blocks ***')
    count = 1
    for redistrictingGroup in redistrictingGroupList:
        tqdm.write('\n')
        tqdm.write('    *** Assigning Neighbors To All Census Blocks for Redistricting Group {0} of {1} ***'
                   .format(count, len(redistrictingGroupList)))
        redistrictingGroup.assignNeighboringBlocksToBlocks()
        count += 1

    # find single orphaned atomic blocks and attach them to the closest neighbor.
    # That way we don't have too small of redistricting groups for splitting them in the next step.
    attachOrphanBlocksToClosestNeighborForRedistrictingGroups(redistrictingGroupList)


def attachOrphanRedistrictingGroupsToClosestNeighbor(neighborsToAttach):
    tqdm.write('\n')
    tqdm.write('*** Attaching Orphan Redistricting Groups To Closest Neighbor ***')

    contiguousRegions = findContiguousGroupsOfGraphObjects(neighborsToAttach)
    while len(contiguousRegions) > 1:
        tqdm.write('   *** Found {0} Isolated Regions ***'.format(len(contiguousRegions)))
        isolatedRegion = contiguousRegions[0]
        closestRegion = findClosestGeometry(originGeometry=isolatedRegion,
                                            otherGeometries=[region for region in contiguousRegions if
                                                             region is not isolatedRegion])

        closestGroupInIsolatedRegion = findClosestGeometry(originGeometry=closestRegion,
                                                           otherGeometries=isolatedRegion)
        closestGroupInClosestRegion = findClosestGeometry(originGeometry=isolatedRegion,
                                                          otherGeometries=closestRegion)

        closestGroupInIsolatedRegion.addNeighbors(neighbors=[closestGroupInClosestRegion])
        closestGroupInClosestRegion.addNeighbors(neighbors=[closestGroupInIsolatedRegion])

        contiguousRegions = findContiguousGroupsOfGraphObjects(neighborsToAttach)
    tqdm.write('   *** No More Orphaned Redistricting Groups ***')


def assignNeighboringRedistrictingGroupsForRedistrictingGroups(redistrictingGroupList, shouldAttachOrphans=True):
    assignNeighboringRedistrictingGroupsToRedistrictingGroups(
        changedRedistrictingGroups=redistrictingGroupList,
        allNeighborCandidates=redistrictingGroupList,
        shouldAttachOrphans=shouldAttachOrphans)


def assignNeighboringRedistrictingGroupsToRedistrictingGroups(changedRedistrictingGroups,
                                                              allNeighborCandidates,
                                                              shouldAttachOrphans=True):
    tqdm.write('\n')
    tqdm.write('*** Removing Outdated Neighbor Connections ***')
    with tqdm(total=len(allNeighborCandidates)) as pbar:
        # remove outdated neighbor connections
        for redistrictingGroup in allNeighborCandidates:
            outdatedNeighborConnections = [neighbor for neighbor in redistrictingGroup.allNeighbors
                                           if neighbor not in allNeighborCandidates]
            if outdatedNeighborConnections:
                redistrictingGroup.removeNeighbors(outdatedNeighborConnections)
            pbar.update(1)

    tqdm.write('\n')
    tqdm.write('*** Assign Neighbors to Changed Redistricting Groups ***')
    with tqdm(total=len(changedRedistrictingGroups)) as pbar:
        # assign neighbors to changed groups and those that they touch
        for changedRedistrictingGroup in changedRedistrictingGroups:
            changedRedistrictingGroup.clearNeighborGraphObjects()
            for redistrictingGroupToCheckAgainst in [aGroup for aGroup in allNeighborCandidates
                                                     if aGroup is not changedRedistrictingGroup]:
                if intersectingGeometries(changedRedistrictingGroup, redistrictingGroupToCheckAgainst):
                    changedRedistrictingGroup.addNeighbors([redistrictingGroupToCheckAgainst])
                    redistrictingGroupToCheckAgainst.addNeighbors([changedRedistrictingGroup])
            pbar.update(1)

        unionOfRedistrictingGroups = list(set(changedRedistrictingGroups) | set(allNeighborCandidates))

    if shouldAttachOrphans:
        attachOrphanRedistrictingGroupsToClosestNeighbor(unionOfRedistrictingGroups)


def mergeGroupsOfRedistrictingGroups(groupsOfRedistrictingGroups):
    mergedRedistrictingGroups = []
    with tqdm(total=len(groupsOfRedistrictingGroups)) as pbar:
        for groupOfRedistrictingGroups in groupsOfRedistrictingGroups:
            if len(groupOfRedistrictingGroups) == 1:
                mergedRedistrictingGroups.append(groupOfRedistrictingGroups[0])
            else:
                allBorderBlocks = []
                allBlocks = []
                for redistrictingGroup in groupOfRedistrictingGroups:
                    allBorderBlocks.extend(redistrictingGroup.borderChildren)
                    allBlocks.extend(redistrictingGroup.children)

                # assign block neighbors to former border blocks
                tqdm.write('      *** Starting a merge with {0} border blocks and {1} total blocks ***'.format(
                    len(allBorderBlocks), len(allBlocks)))
                for formerBorderBlock in allBorderBlocks:
                    assignNeighborBlocksFromCandidateBlocks(block=formerBorderBlock,
                                                            candidateBlocks=allBlocks)

                contiguousRegions = findContiguousGroupsOfGraphObjects(allBlocks)

                mergedRedistrictingGroupsForPrevious = []
                for contiguousRegion in contiguousRegions:
                    contiguousRegionGroup = RedistrictingGroup(childrenBlocks=contiguousRegion)
                    # assign block neighbors to former border blocks
                    for borderBlock in contiguousRegionGroup.borderChildren:
                        assignNeighborBlocksFromCandidateBlocks(block=borderBlock,
                                                                candidateBlocks=contiguousRegionGroup.children)
                    contiguousRegionGroup.validateBlockNeighbors()
                    mergedRedistrictingGroupsForPrevious.append(contiguousRegionGroup)
                mergedRedistrictingGroups.extend(mergedRedistrictingGroupsForPrevious)
            pbar.update(1)

    return mergedRedistrictingGroups


def getRedistrictingGroupWithCountyFIPS(countyFIPS, redistrictingGroupList):
    # for use when first loading redistricting group
    return next((item for item in redistrictingGroupList if item.FIPS == countyFIPS), None)


def convertAllCensusBlocksToAtomicBlocks(redistrictingGroupList):
    tqdm.write('\n')
    tqdm.write('*** Converting All Census Blocks to Atomic Blocks ***')
    count = 1
    for blockContainer in redistrictingGroupList:
        tqdm.write('\n')
        tqdm.write('    *** Converting to Atomic Blocks for Redistricting Group {0} of {1} ***'
                   .format(count, len(redistrictingGroupList)))
        atomicBlocksForGroup = createAtomicBlocksFromBlockList(blockList=blockContainer.children)
        blockContainer.children = atomicBlocksForGroup  # this triggers a block container update
        count += 1


def validateRedistrictingGroups(groupList):
    tqdm.write('\n')
    tqdm.write('*** Validating Redistricting Groups ***')
    validateContiguousRedistrictingGroups(groupList)

    with tqdm(total=len(groupList)) as pbar:
        for redistrictingGroup in groupList:
            redistrictingGroup.validateNeighborLists()
            redistrictingGroup.validateBlockNeighbors()
            pbar.update(1)


def validateContiguousRedistrictingGroups(groupList):
    contiguousRegions = findContiguousGroupsOfGraphObjects(groupList)
    if len(contiguousRegions) > 1:
        saveDataToFileWithDescription(data=contiguousRegions,
                                      censusYear='',
                                      stateName='',
                                      descriptionOfInfo='ErrorCase-GroupsAreNotContiguous')
        plotGraphObjectGroups(contiguousRegions,
                              showDistrictNeighborConnections=True)
        raise ValueError("Don't have a contiguous set of RedistrictingGroups. There are {0} distinct groups".format(
            len(contiguousRegions)))


def createRedistrictingGroupsWithAtomicBlocksFromCensusData(censusData):
    redistrictingGroupList = []
    tqdm.write('\n')
    tqdm.write('*** Creating Redistricting Groups from Census Data ***')
    with tqdm(total=len(censusData)) as pbar:
        for censusBlockDict in censusData:
            redistrictingGroupWithCountyFIPS = getRedistrictingGroupWithCountyFIPS(censusBlockDict['county'],
                                                                                   redistrictingGroupList)
            if redistrictingGroupWithCountyFIPS is None:
                redistrictingGroupWithCountyFIPS = RedistrictingGroup(childrenBlocks=[], allowEmpty=True)
                redistrictingGroupWithCountyFIPS.FIPS = censusBlockDict['county']
                redistrictingGroupList.append(redistrictingGroupWithCountyFIPS)

            isWater = False
            if censusBlockDict['block'][0] == '0':
                isWater = True
            blockFromData = censusBlock.CensusBlock(countyFIPS=censusBlockDict['county'],
                                                    tractFIPS=censusBlockDict['tract'],
                                                    blockFIPS=censusBlockDict['block'],
                                                    population=int(censusBlockDict['P001001']),
                                                    isWater=isWater,
                                                    geoJSONGeometry=censusBlockDict['geometry'])
            redistrictingGroupWithCountyFIPS.children.append(blockFromData)
            pbar.update(1)

    # remove FIPS info from the groups to not pollute data later
    for redistrictingGroup in redistrictingGroupList:
        del redistrictingGroup.FIPS

    # convert census blocks to atomic blocks
    convertAllCensusBlocksToAtomicBlocks(redistrictingGroupList)

    return redistrictingGroupList


def prepareBlockGraphsForRedistrictingGroups(redistrictingGroupList, shouldRemoveWaterBlocks=True):
    if shouldRemoveWaterBlocks:
        # remove water blocks
        removeWaterBlocksFromRedistrictingGroups(redistrictingGroupList)

    # assign neighboring blocks to atomic blocks
    assignNeighboringBlocksToBlocksForRedistrictingGroups(redistrictingGroupList)

    return redistrictingGroupList


def prepareGraphsForRedistrictingGroups(redistrictingGroupList):
    # split non-contiguous redistricting groups
    splitNonContiguousRedistrictingGroups(redistrictingGroupList)

    # find and set neighboring geometries
    assignNeighboringRedistrictingGroupsForRedistrictingGroups(redistrictingGroupList)

    validateRedistrictingGroups(redistrictingGroupList)
    validateAllAtomicBlocks()

    return redistrictingGroupList


def mergeContiguousRedistrictingGroups(redistrictingGroupList):
    for redistrictingGroup in redistrictingGroupList:
        redistrictingGroup.clearNeighborGraphObjects()

    assignNeighboringRedistrictingGroupsForRedistrictingGroups(redistrictingGroupList, shouldAttachOrphans=False)
    contiguousRedistrictingGroups = findContiguousGroupsOfGraphObjects(redistrictingGroupList)
    mergedGroupsOfRedistrictingGroups = mergeGroupsOfRedistrictingGroups(contiguousRedistrictingGroups)

    # find and set neighboring geometries
    assignNeighboringRedistrictingGroupsForRedistrictingGroups(mergedGroupsOfRedistrictingGroups)

    validateRedistrictingGroups(mergedGroupsOfRedistrictingGroups)
    validateAllAtomicBlocks()

    return mergedGroupsOfRedistrictingGroups
