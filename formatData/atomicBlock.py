from formatData.censusBlockContainer import CensusBlockContainer
from geographyHelper import doesGeographyContainTheOther, shapelyGeometryToGeoJSON
from tqdm import tqdm


class AtomicBlock(CensusBlockContainer):
    def __init__(self, childrenBlocks):
        CensusBlockContainer.__init__(self)
        self.blocks = childrenBlocks
        AtomicBlock.atomicBlockList.append(self)


    def importCensusBlock(self, censusBlock):
        self.blocks.append(censusBlock)
        self.updateBlockContainerData()


    atomicBlockList = []


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