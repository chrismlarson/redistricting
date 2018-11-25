import os
from unittest import TestCase
from exportData.exportData import loadDataFromFile
from geographyHelper import Alignment


class TestGetPopulationEnergyPolygonSplit(TestCase):

    def test_getPopulationEnergyPolygonSplit_CentroidNotWithinPolygon(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-CentroidNotWithinPolygon.redistdata')
        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.northSouth)
        northSouthSplit = testRedistrictingGroup.getPopulationEnergySplit(Alignment.northSouth)

        self.assertTrue(len(northSouthSplit[0]) > 0)
        self.assertTrue(len(northSouthSplit[1]) > 0)


    def test_getPopulationEnergyPolygonSplit_AandBShouldBeFound01(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-ContainerBoundaryIsMultiLineString.redistdata')
        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.northSouth)
        northSouthSplit = testRedistrictingGroup.getPopulationEnergySplit(Alignment.northSouth)

        self.assertTrue(len(northSouthSplit[0]) > 0)
        self.assertTrue(len(northSouthSplit[1]) > 0)
