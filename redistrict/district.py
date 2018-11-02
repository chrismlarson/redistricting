from formatData.blockBorderGraph import BlockBorderGraph

class District(BlockBorderGraph):
    def __init__(self, childrenGroups):
        BlockBorderGraph.__init__(self)
        self.children = childrenGroups
        District.districtList.append(self)

    districtList = []