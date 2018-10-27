from geographyHelper import findDirectionOfShapeFromPoint, CardinalDirection


class BlockGraphObject:
    def __init__(self, centerOfObject):
        self.__northernNeighborBlocks = []
        self.__westernNeighborBlocks = []
        self.__easternNeighborBlocks = []
        self.__southernNeighborBlocks = []
        self.updateCenterOfObject(centerOfObject)

    def updateCenterOfObject(self, center):
        self.__centerOfObject = center

    def addNeighborBlocks(self, neighborBlocks):
        self.__northernNeighborBlocks = []
        self.__westernNeighborBlocks = []
        self.__easternNeighborBlocks = []
        self.__southernNeighborBlocks = []
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
