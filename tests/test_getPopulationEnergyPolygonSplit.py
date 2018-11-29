import os
from unittest import TestCase
from exportData.exportData import loadDataFromFile
from formatData.redistrictingGroup import SplitType
from geographyHelper import Alignment


class TestGetPopulationEnergyPolygonSplit(TestCase):

    def test_getPopulationEnergyPolygonSplit_CentroidNotWithinPolygon(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-CentroidNotWithinPolygon.redistdata')
        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.northSouth)
        northSouthSplitResult = testRedistrictingGroup.getPopulationEnergySplit(Alignment.northSouth)
        northSouthSplitResultType = northSouthSplitResult[0]
        northSouthSplit = northSouthSplitResult[1]
        self.assertEqual(northSouthSplitResultType, SplitType.NormalSplit)
        self.assertTrue(len(northSouthSplit[0]) > 0)
        self.assertTrue(len(northSouthSplit[1]) > 0)


    def test_getPopulationEnergyPolygonSplit_BoundaryIsMultiLineString(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-ContainerBoundaryIsMultiLineString.redistdata')
        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.northSouth)
        northSouthSplitResult = testRedistrictingGroup.getPopulationEnergySplit(Alignment.northSouth)
        northSouthSplitResultType = northSouthSplitResult[0]
        northSouthSplit = northSouthSplitResult[1]
        self.assertEqual(northSouthSplitResultType, SplitType.NormalSplit)
        self.assertTrue(len(northSouthSplit[0]) > 0)
        self.assertTrue(len(northSouthSplit[1]) > 0)

    def test_getPopulationEnergyPolygonSplit_SeamInCornerOfGroup(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-SeamInCornerOfGroup.redistdata')
        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.westEast)
        westEastSplitResult = testRedistrictingGroup.getPopulationEnergySplit(Alignment.westEast)
        westEastSplitResultType = westEastSplitResult[0]
        westEastSplit = westEastSplitResult[1]
        self.assertEqual(westEastSplitResultType, SplitType.NormalSplit)
        self.assertTrue(len(westEastSplit[0]) > 0)
        self.assertTrue(len(westEastSplit[1]) > 0)

    def test_getPopulationEnergyPolygonSplit_MissingWesternAndEasternChildBlocks(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-NoWesternOrEasternChildren.redistdata')
        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.northSouth)
        northSouthSplitResult = testRedistrictingGroup.getPopulationEnergySplit(Alignment.northSouth)
        northSouthSplitResultType = northSouthSplitResult[0]
        northSouthSplit = northSouthSplitResult[1]
        self.assertEqual(northSouthSplitResultType, SplitType.NoSplit)
        self.assertEqual(northSouthSplit, None)

        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.westEast)
        westEastSplitResult = testRedistrictingGroup.getPopulationEnergySplit(Alignment.westEast)
        westEastSplitResultType = westEastSplitResult[0]
        westEastSplit = westEastSplitResult[1]
        self.assertEqual(westEastSplitResultType, SplitType.NormalSplit)
        self.assertTrue(len(westEastSplit[0]) > 0)
        self.assertTrue(len(westEastSplit[1]) > 0)

    def test_getPopulationEnergyPolygonSplit_GeometryCollectionAfterSplit(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-TooSmallToSplit.redistdata')
        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        testRedistrictingGroup.fillPopulationEnergyGraph(Alignment.northSouth)
        northSouthSplitResult = testRedistrictingGroup.getPopulationEnergySplit(Alignment.northSouth)
        northSouthSplitResultType = northSouthSplitResult[0]
        self.assertEqual(northSouthSplitResultType, SplitType.ForceSplitAllBlocks)




