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


    def test_getPopulationEnergyPolygonSplit_BoundaryIsMultiLineString(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-ContainerBoundaryIsMultiLineString.redistdata')
        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.northSouth)
        northSouthSplit = testRedistrictingGroup.getPopulationEnergySplit(Alignment.northSouth)

        self.assertTrue(len(northSouthSplit[0]) > 0)
        self.assertTrue(len(northSouthSplit[1]) > 0)

    def test_getPopulationEnergyPolygonSplit_SeamInCornerOfGroup(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-SeamInCornerOfGroup.redistdata')
        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.westEast)
        westEastSplit = testRedistrictingGroup.getPopulationEnergySplit(Alignment.westEast)

        self.assertTrue(len(westEastSplit[0]) > 0)
        self.assertTrue(len(westEastSplit[1]) > 0)

    def test_getPopulationEnergyPolygonSplit_MissingWesternAndEasternChildBlocks(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-NoWesternOrEasternChildren.redistdata')
        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.northSouth)
        northSouthSplit = testRedistrictingGroup.getPopulationEnergySplit(Alignment.northSouth)
        self.assertEqual(northSouthSplit, None)

        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.westEast)
        westEastSplit = testRedistrictingGroup.getPopulationEnergySplit(Alignment.westEast)

        self.assertTrue(len(westEastSplit[0]) > 0)
        self.assertTrue(len(westEastSplit[1]) > 0)


