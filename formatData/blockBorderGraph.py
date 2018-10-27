from geographyHelper import isBoundaryGeometry, findDirectionOfShapeFromPoint, CardinalDirection
from formatData.censusBlockContainer import CensusBlockContainer


class BlockBorderGraph(CensusBlockContainer):
    def __init__(self):
        CensusBlockContainer.__init__(self)
        self.__northernChildBlocks = []
        self.__westernChildBlocks = []
        self.__easternChildBlocks = []
        self.__southernChildBlocks = []

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
        centerOfContainer = self.geometry.centroid
        for block in self.blocks:
            if isBoundaryGeometry(parent=self, child=block):
                direction = findDirectionOfShapeFromPoint(basePoint=centerOfContainer, targetShape=block.geometry)
                self.__addBorderBlocks(block=block, direction=direction)

    def __addBorderBlocks(self, block, direction):
        if direction == CardinalDirection.north:
            self.__northernChildBlocks.append(block)
        elif direction == CardinalDirection.west:
            self.__westernChildBlocks.append(block)
        elif direction == CardinalDirection.east:
            self.__easternChildBlocks.append(block)
        elif direction == CardinalDirection.south:
            self.__southernChildBlocks.append(block)