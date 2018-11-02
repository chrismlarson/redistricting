from geographyHelper import geometryFromMultipleGeometries
from censusData import censusBlock


class CensusContainer:
    def __init__(self):
        self.children = []
        self.geometry = None
        self.population = None

    def updateBlockContainerData(self):
        self.geometry = geometryFromMultipleGeometries(self.children)
        self.population = censusBlock.populationFromBlocks(self.children)

    @property
    def children(self):
        return self.__children

    @children.setter
    def children(self, children):
        self.__children = children
        self.updateBlockContainerData()