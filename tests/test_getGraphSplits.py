import os
from unittest import TestCase
from exportData.exportData import loadDataFromFile


class TestGetGraphSplits(TestCase):

    def test_getGraphSplits_HourglassShape(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/RedistrictingGroup-ErrorCase-HourglassShape.redistdata')

        testRedistrictingGroup = loadDataFromFile(filePath=testDataFilePath)
        graphSplits = testRedistrictingGroup.getGraphSplits()

        self.assertEqual(len(graphSplits), 2)

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

