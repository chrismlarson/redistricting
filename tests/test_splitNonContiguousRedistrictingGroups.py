import os
from unittest import TestCase
from exportData.exportData import loadDataFromFile
from formatData.redistrictingGroup import RedistrictingGroup, splitNonContiguousRedistrictingGroups


class TestSplitNonContiguousRedistrictingGroups(TestCase):

    def test_splitNonContiguousRedistrictingGroups_NeedsASplitWithLargeNumberOfBlocks(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/2010-Michigan-CharlevoixRedistrictingGroupInfoNeedsSplit.redistdata')
        testData = loadDataFromFile(filePath=testDataFilePath)
        RedistrictingGroup.redistrictingGroupList = testData
        splitNonContiguousRedistrictingGroups()
        self.assertEqual(len(RedistrictingGroup.redistrictingGroupList), 2)
