from geographyHelper import findDirectionOfShapeFromPoint, CardinalDirection


class BlockGraphObject:
    def __init__(self, centerOfObject):
        self.northernNeighborBlocks = []
        self.westernNeighborBlocks = []
        self.easternNeighborBlocks = []
        self.southernNeighborBlocks = []
        self.updateCenterOfObject(centerOfObject)

    @property
    def hasNeighbors(self):
        if self.northernNeighborBlocks or \
                self.westernNeighborBlocks or \
                self.easternNeighborBlocks or \
                self.southernNeighborBlocks:
            return True
        else:
            return False

    def updateCenterOfObject(self, center):
        self.__centerOfObject = center

    def isNeighbor(self, block):
        if block in self.northernNeighborBlocks or \
           block in self.westernNeighborBlocks or \
           block in self.easternNeighborBlocks or \
           block in self.southernNeighborBlocks:
            return True
        else:
            return False

    def clearNeighborBlocks(self):
        self.northernNeighborBlocks = []
        self.westernNeighborBlocks = []
        self.easternNeighborBlocks = []
        self.southernNeighborBlocks = []

    def addNeighborBlocks(self, neighborBlocks):
        for neighborBlock in neighborBlocks:
            direction = findDirectionOfShapeFromPoint(basePoint=self.__centerOfObject,
                                                      targetShape=neighborBlock.geometry)
            self.addNeighborBlock(block=neighborBlock, direction=direction)

    def addNeighborBlock(self, block, direction):
        if direction == CardinalDirection.north:
            self.northernNeighborBlocks.append(block)
        elif direction == CardinalDirection.west:
            self.westernNeighborBlocks.append(block)
        elif direction == CardinalDirection.east:
            self.easternNeighborBlocks.append(block)
        elif direction == CardinalDirection.south:
            self.southernNeighborBlocks.append(block)
