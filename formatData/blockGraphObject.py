from geographyHelper import findDirectionOfShapeFromPoint, CardinalDirection


class BlockGraphObject:
    def __init__(self, centerOfObject):
        self.__northernNeighborBlocks = []
        self.__westernNeighborBlocks = []
        self.__easternNeighborBlocks = []
        self.__southernNeighborBlocks = []
        self.updateCenterOfObject(centerOfObject)

    @property
    def hasNeighbors(self):
        if self.__northernNeighborBlocks or \
                self.__westernNeighborBlocks or \
                self.__easternNeighborBlocks or \
                self.__southernNeighborBlocks:
            return True
        else:
            return False

    def updateCenterOfObject(self, center):
        self.__centerOfObject = center

    def isNeighbor(self, block):
        if block in self.__northernNeighborBlocks or \
           block in self.__westernNeighborBlocks or \
           block in self.__easternNeighborBlocks or \
           block in self.__southernNeighborBlocks:
            return True
        else:
            return False

    def clearNeighborBlocks(self):
        self.__northernNeighborBlocks = []
        self.__westernNeighborBlocks = []
        self.__easternNeighborBlocks = []
        self.__southernNeighborBlocks = []

    def addNeighborBlocks(self, neighborBlocks):
        for neighborBlock in neighborBlocks:
            direction = findDirectionOfShapeFromPoint(basePoint=self.__centerOfObject,
                                                      targetShape=neighborBlock.geometry)
            self.addNeighborBlock(block=neighborBlock, direction=direction)

    def addNeighborBlock(self, block, direction):
        if direction == CardinalDirection.north:
            self.__northernNeighborBlocks.append(block)
        elif direction == CardinalDirection.west:
            self.__westernNeighborBlocks.append(block)
        elif direction == CardinalDirection.east:
            self.__easternNeighborBlocks.append(block)
        elif direction == CardinalDirection.south:
            self.__southernNeighborBlocks.append(block)
