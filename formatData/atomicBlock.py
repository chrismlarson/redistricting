from censusData.censusBlockContainer import CensusBlockContainer


class AtomicBlock(CensusBlockContainer):
    def __init__(self, childrenBlocks):
        CensusBlockContainer.__init__(self)
        self.blocks = childrenBlocks
        AtomicBlock.atomicBlockList.append(self)

    atomicBlockList = []