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