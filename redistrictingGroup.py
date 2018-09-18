from censusBlockContainer import CensusBlockContainer
from tqdm import tqdm

class RedistrictingGroup(CensusBlockContainer):
    def __init__(self, childrenBlocks):
        CensusBlockContainer.__init__(self)
        self.blocks = childrenBlocks
        self.neighboringGroups = []

def createRedistrictingGroupFromCounties(countyList):
    counties = []
    #todo: convert counties to redistricting groups
    return counties

