import os
from unittest import TestCase
from exportData.exportData import loadDataFromFile
from formatData.redistrictingGroup import RedistrictingGroup, \
    assignNeighboringRedistrictingGroupsForAllRedistrictingGroups
from geographyHelper import findContiguousGroupsOfGraphObjects


class TestAttachOrphanRedistrictingGroupsToClosestNeighbor(TestCase):

    def test_attachOrphanRedistrictingGroupsToClosestNeighbor_ThreeRegions(self):
        testDataFilePath = os.path.join(os.path.dirname(__file__),
                                        'testData/2010-Michigan-KeweenawAndTheThumbRedistrictingGroupInfoHasOrphans.redistdata')
        testData = loadDataFromFile(filePath=testDataFilePath)
        RedistrictingGroup.redistrictingGroupList = testData
        contiguousRegions = findContiguousGroupsOfGraphObjects(RedistrictingGroup.redistrictingGroupList)
        self.assertEqual(len(contiguousRegions), 3)

        assignNeighboringRedistrictingGroupsForAllRedistrictingGroups()
        contiguousRegions = findContiguousGroupsOfGraphObjects(RedistrictingGroup.redistrictingGroupList)
        self.assertEqual(len(contiguousRegions), 1)
