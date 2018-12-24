from shapely.geometry import MultiPolygon
from censusData.censusBlock import CensusBlock
from exportData.displayShapes import plotPolygons
from exportData.exportData import saveDataToFileWithDescription
from formatData.graphObject import GraphObject
from formatData.censusContainer import CensusContainer
from geographyHelper import doesGeographyContainTheOther, intersectingGeometries
from tqdm import tqdm
import math


class AtomicBlock(CensusContainer, GraphObject):
    def __init__(self, childrenBlocks):
        CensusContainer.__init__(self)
        self.children = childrenBlocks
        GraphObject.__init__(self, self.geometry.centroid)
        self.isWater = self.getWaterPropertyFromBlocks()
        AtomicBlock.atomicBlockList.append(self)

    atomicBlockList = []

    def updateBlockContainerData(self):
        super(AtomicBlock, self).updateBlockContainerData()
        self.updateCenterOfObject(self.geometry.centroid)

    def importCensusBlock(self, censusBlock):
        self.children.append(censusBlock)
        self.isWater = self.getWaterPropertyFromBlocks()
        self.updateBlockContainerData()

    def getWaterPropertyFromBlocks(self):
        return all(block.isWater for block in self.children)


def assignNeighborBlocksFromCandidateBlocks(block, candidateBlocks, progressObject=None):
    block.clearNeighborGraphObjects()
    neighborBlocks = []
    for candidateBlock in candidateBlocks:
        if candidateBlock is not block:
            if intersectingGeometries(block, candidateBlock):
                neighborBlocks.append(candidateBlock)
    block.addNeighbors(neighbors=neighborBlocks)

    for neighborBlock in neighborBlocks:
        if block not in neighborBlock.allNeighbors:
            neighborBlock.addNeighbor(block)

    if progressObject:
        progressObject.update(1)


def createAtomicBlockFromCensusBlock(censusBlock):
    newAtomicBlock = AtomicBlock(childrenBlocks=[censusBlock])
    return newAtomicBlock


def atomicBlockWithBlock(block, atomicBlockList):
    return next((atomicBlock for atomicBlock in atomicBlockList if block in atomicBlock.children), None)


def createAtomicBlocksFromBlockList(blockList):
    # some blocks aren't contiguous (typically uninhabited islands), so we break them up into separate blocks
    tqdm.write('       *** Separating Blocks if necessary ***')
    updatedBlocks = []
    with tqdm(total=len(blockList)) as pbar:
        for block in blockList:
            if type(block.geometry) is MultiPolygon:
                blockPolygons = list(block.geometry)
                popSplit = math.floor(block.population / len(blockPolygons))

                popTotalSoFar = 0
                i = 1
                for blockPolygon in blockPolygons:
                    popTotalSoFar += popSplit
                    if blockPolygons.index(blockPolygon) == len(blockPolygons) - 1:
                        diffInPop = block.population - popTotalSoFar
                        popSplit += diffInPop
                    newFIPS = block.FIPS + str(i)
                    splitBlock = CensusBlock(countyFIPS=block.countyFIPS,
                                             tractFIPS=block.tractFIPS,
                                             blockFIPS=newFIPS,
                                             population=int(popSplit),
                                             isWater=block.isWater,
                                             geometry=blockPolygon)
                    updatedBlocks.append(splitBlock)
                    i += 1
            else:
                updatedBlocks.append(block)
            pbar.update(1)

    tqdm.write('       *** Creating Atomic Blocks ***')
    atomicBlockList = []
    with tqdm(total=len(updatedBlocks)) as pbar:
        for i in reversed(range(len(updatedBlocks))):
            block = updatedBlocks[i]
            convertedAtomicBlock = createAtomicBlockFromCensusBlock(block)
            atomicBlockList.append(convertedAtomicBlock)
            for j in reversed(range(len(updatedBlocks))):
                otherBlock = updatedBlocks[j]
                if block != otherBlock:
                    if doesGeographyContainTheOther(container=block, target=otherBlock):
                        convertedAtomicBlock.importCensusBlock(otherBlock)
                        del updatedBlocks[updatedBlocks.index(otherBlock)]

                        atomicBlockThatAlreadyExists = atomicBlockWithBlock(block=otherBlock,
                                                                            atomicBlockList=atomicBlockList)
                        if atomicBlockThatAlreadyExists:
                            del atomicBlockList[atomicBlockList.index(atomicBlockThatAlreadyExists)]
            pbar.update(1)

    return atomicBlockList


def validateAllAtomicBlocks():
    for atomicBlock in AtomicBlock.atomicBlockList:
        atomicBlock.validateNeighborLists()
