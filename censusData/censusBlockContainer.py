import geographyHelper
from censusData import censusBlock


class CensusBlockContainer:
    def __init__(self):
        self.blocks = []
        self.borderBlocks = []

    def updateBlockContainerData(self):
        self.geometry = geographyHelper.geometryFromBlocks(self.blocks)
        self.population = censusBlock.populationFromBlocks(self.blocks)
        self.__findBorderBlocks()

    @property
    def blocks(self):
        return self.__blocks

    @blocks.setter
    def blocks(self, blocks):
        self.__blocks = blocks
        self.updateBlockContainerData()


    def __findBorderBlocks(self):
        self.borderBlocks = []
        for block in self.blocks:
            if geographyHelper.isBoundaryGeometry(parent=self, child=block):
                self.borderBlocks.append(block)