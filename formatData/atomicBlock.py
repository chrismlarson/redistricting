from formatData.censusBlockContainer import CensusBlockContainer


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


def createAtomicBlocksFromBlockList(blockList):
    atomicBlockList = []
    for block in blockList:
        temp = 0

    return atomicBlockList