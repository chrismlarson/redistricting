import os
from unittest import TestCase
from exportData.exportData import loadDataFromFile
from shapely.geometry import Polygon


class TestGetGraphSplits(TestCase):

    def test_getGraphSplits_HourglassShape(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-HourglassShape.redistdata')

        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        graphSplits = testRedistrictingGroup.getGraphSplits()

        self.assertEqual(len(graphSplits), 4)

    def test_getGraphSplits_TooSmallToBreak(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-TooSmallToSplit.redistdata')

        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        graphSplits = testRedistrictingGroup.getGraphSplits()

        self.assertEqual(len(graphSplits), len(testRedistrictingGroup.children))

    def test_getGraphSplits_WeirdSplitThatCanProduceOrphans(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-WeirdSplitWithOrphans.redistdata')

        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        graphSplits = testRedistrictingGroup.getGraphSplits()

        self.assertEqual(len(graphSplits), 4)

    def test_getGraphSplits_NormalSplitCausesIsolatedBlockInfo(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-NormalSplitCausesIsolatedBlockInfo.redistdata')

        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        graphSplits = testRedistrictingGroup.getGraphSplits()

        self.assertEqual(len(graphSplits), 4)
        for graphSplit in graphSplits:
            self.assertEqual(type(graphSplit.geometry), Polygon)

    def test_getGraphSplits_CouldNotFindSplit(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-CouldNotFindSplit.redistdata')

        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        graphSplits = testRedistrictingGroup.getGraphSplits()

        self.assertEqual(len(graphSplits), len(testRedistrictingGroup.children))

    def test_getGraphSplits_BlockCanNotFindPreviousNeighbor(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-BlockCanNotFindPreviousNeighbor.redistdata')

        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        graphSplits = testRedistrictingGroup.getGraphSplits()

        self.assertEqual(len(graphSplits), 3)

    def test_getGraphSplits_BlockCanNotFindPreviousNeighborBecauseCutOff(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-BlockCanNotFindPreviousNeighborBecauseCutOff.redistdata')

        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        graphSplits = testRedistrictingGroup.getGraphSplits()

        self.assertEqual(len(graphSplits), 4)

    def test_getGraphSplits_CouldNotFindRepresentativeBlock(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-CouldNotFindRepresentativeBlock.redistdata')

        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        graphSplits = testRedistrictingGroup.getGraphSplits()

        self.assertEqual(len(graphSplits), 11)
