from geographyHelper import geometryFromMultipleGeometries
from censusData import censusBlock


class CensusBlockContainer:
    def __init__(self):
        self.blocks = []
        self.geometry = None
        self.population = None

    def updateBlockContainerData(self):
        self.geometry = geometryFromMultipleGeometries(self.blocks)
        self.population = censusBlock.populationFromBlocks(self.blocks)

    @property
    def blocks(self):
        return self.__blocks

    @blocks.setter
    def blocks(self, blocks):
        self.__blocks = blocks
        self.updateBlockContainerData()