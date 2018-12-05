from exportData.exportData import saveDataToFileWithDescription
from geographyHelper import polygonFromMultipleGeometries
from censusData import censusBlock


class CensusContainer:
    def __init__(self):
        self.children = []
        self.geometry = None
        self.population = None

    def updateBlockContainerData(self):
        self.geometry = polygonFromMultipleGeometries(self.children)
        self.population = censusBlock.populationFromBlocks(self.children)

    @property
    def children(self):
        return self.__children

    @children.setter
    def children(self, children):
        if len(children) != len(set(children)):
            saveDataToFileWithDescription(data=self,
                                          censusYear='',
                                          stateName='',
                                          descriptionOfInfo='ErrorCase-DuplicateChildren')
            raise RuntimeError("Children contains duplicates: {0}".format(self))

        self.__children = children
        self.updateBlockContainerData()