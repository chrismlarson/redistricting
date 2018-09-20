from censusBlockContainer import CensusBlockContainer

class RedistrictingGroup(CensusBlockContainer):
    def __init__(self, childrenBlocks):
        CensusBlockContainer.__init__(self)
        self.blocks = childrenBlocks
        self.neighboringGroups = []
        RedistrictingGroup.redistrictingGroupList.append(self)

    redistrictingGroupList = []


def assignNeighboringBlocksToEveryBlock():
    temp = 0

