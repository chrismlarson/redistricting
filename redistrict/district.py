from formatData.blockBorderGraph import BlockBorderGraph

class District(BlockBorderGraph):
    def __init__(self, childrenGroups):
        BlockBorderGraph.__init__(self)
        self.children = childrenGroups
        District.districtList.append(self)

    districtList = []


def createDistrictFromRedistrictingGroups(redistrictingGroups):
    initialDistrict = District(childrenGroups=redistrictingGroups)
    return initialDistrict


def splitDistrict(districtToSplit, numberOfDistricts):
    if numberOfDistricts == 1:
        return [districtToSplit]
    else:
        raise NotImplementedError('splitDistrict not yet implemented')