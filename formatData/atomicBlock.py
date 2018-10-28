from formatData.graphObject import GraphObject
from formatData.censusBlockContainer import CensusBlockContainer
from geographyHelper import doesGeographyContainTheOther, intersectingGeometries, distanceBetweenBlocks
from tqdm import tqdm


class AtomicBlock(CensusBlockContainer, GraphObject):
    def __init__(self, childrenBlocks):
        CensusBlockContainer.__init__(self)
        self.blocks = childrenBlocks
        GraphObject.__init__(self, self.geometry.centroid)
        self.isWater = self.getWaterPropertyFromBlocks()
        AtomicBlock.atomicBlockList.append(self)

    atomicBlockList = []


    def updateBlockContainerData(self):
        super(AtomicBlock, self).updateBlockContainerData()
        self.updateCenterOfObject(self.geometry.centroid)


    def findClosestBlockToBlocks(self, otherBlocks):
        candidateBlocks = [block for block in otherBlocks if block is not self]
        distanceDict = {}
        for candidateBlock in candidateBlocks:
            distance = distanceBetweenBlocks(self, candidateBlock)
            distanceDict[distance] = candidateBlock
        shortestDistance = min(distanceDict.keys())
        closestBlock = distanceDict[shortestDistance]
        return closestBlock


    def importCensusBlock(self, censusBlock):
        self.blocks.append(censusBlock)
        self.isWater = self.getWaterPropertyFromBlocks()
        self.updateBlockContainerData()


    def getWaterPropertyFromBlocks(self):
        return all(block.isWater for block in self.blocks)


    def assignNeighborBlocksFromCandiateBlocks(self, candidateBlocks):
        neighborBlocks = []
        for candidateBlock in candidateBlocks:
            if candidateBlock is not self:
                if intersectingGeometries(self, candidateBlock):
                    neighborBlocks.append(candidateBlock)
        self.addNeighbors(neighbors=neighborBlocks)


def createAtomicBlockFromCensusBlock(censusBlock):
    newAtomicBlock = AtomicBlock(childrenBlocks=[censusBlock])
    return newAtomicBlock


def atomicBlockWithBlock(block, atomicBlockList):
    return next((atomicBlock for atomicBlock in atomicBlockList if block in atomicBlock.blocks), None)


def createAtomicBlocksFromBlockList(blockList):
    atomicBlockList = []
    with tqdm(total=len(blockList)) as pbar:
        for i in reversed(range(len(blockList))):
            block = blockList[i]
            convertedAtomicBlock = createAtomicBlockFromCensusBlock(block)
            atomicBlockList.append(convertedAtomicBlock)
            for j in reversed(range(len(blockList))):
                otherBlock = blockList[j]
                if block != otherBlock:
                    if doesGeographyContainTheOther(container=block, target=otherBlock):
                        #blockGeoJSON = shapelyGeometryToGeoJSON(block.geometry)
                        #otherBlockGeoJSON = shapelyGeometryToGeoJSON(otherBlock.geometry)
                        convertedAtomicBlock.importCensusBlock(otherBlock)
                        del blockList[blockList.index(otherBlock)]

                        atomicBlockThatAlreadyExists = atomicBlockWithBlock(block=otherBlock, atomicBlockList=atomicBlockList)
                        if atomicBlockThatAlreadyExists:
                            del atomicBlockList[atomicBlockList.index(atomicBlockThatAlreadyExists)]
            pbar.update(1)

    return atomicBlockList