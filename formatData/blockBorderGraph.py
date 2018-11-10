from geographyHelper import isBoundaryGeometry, findDirectionOfBorderGeometries, CardinalDirection
from formatData.censusContainer import CensusContainer


class BlockBorderGraph(CensusContainer):
    def __init__(self):
        CensusContainer.__init__(self)
        self.__northernChildBlocks = []
        self.__westernChildBlocks = []
        self.__easternChildBlocks = []
        self.__southernChildBlocks = []

    @property
    def northernChildBlocks(self):
        return self.__northernChildBlocks

    @property
    def westernChildBlocks(self):
        return self.__westernChildBlocks

    @property
    def easternChildBlocks(self):
        return self.__easternChildBlocks

    @property
    def southernChildBlocks(self):
        return self.__southernChildBlocks

    @property
    def borderChildren(self):
        return self.northernChildBlocks + self.westernChildBlocks + self.easternChildBlocks + self.southernChildBlocks

    def updateBlockContainerData(self):
        super(BlockBorderGraph, self).updateBlockContainerData()
        self.__findBorderBlocks()

    def isBorderBlock(self, block):
        return block in self.__northernChildBlocks or \
               block in self.__westernChildBlocks or \
               block in self.__easternChildBlocks or \
               block in self.__southernChildBlocks

    def __findBorderBlocks(self):
        self.__northernChildBlocks = []
        self.__westernChildBlocks = []
        self.__easternChildBlocks = []
        self.__southernChildBlocks = []
        borderBlocks = []
        for block in self.children:
            if isBoundaryGeometry(parent=self, child=block):
                borderBlocks.append(block)
        if len(borderBlocks) > 0:
            blockDirections = findDirectionOfBorderGeometries(parentShape=self, targetShapes=borderBlocks)
            for blockDirection in blockDirections:
                self.__addBorderBlocks(block=blockDirection[0], direction=blockDirection[1])

    def __addBorderBlocks(self, block, direction):
        if direction == CardinalDirection.north:
            self.__northernChildBlocks.append(block)
        elif direction == CardinalDirection.west:
            self.__westernChildBlocks.append(block)
        elif direction == CardinalDirection.east:
            self.__easternChildBlocks.append(block)
        elif direction == CardinalDirection.south:
            self.__southernChildBlocks.append(block)
