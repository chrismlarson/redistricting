from os import path
from unittest import TestCase

from exportData.exportData import loadDataFromFile


class TestDistrict(TestCase):
    def test_splitDistrict_singleRedistrictingGroup(self):
        filePath = path.expanduser('~/Documents/--ErrorCase-NoGroupsCapableOfBreakingInfo.redistdata')
        data = loadDataFromFile(filePath)
        districtCandidate = data[0]
        splits = districtCandidate.splitDistrict(numberOfDistricts=2,
                                                 populationDeviation=1,
                                                 splitBestCandidateGroup=False,
                                                 shouldMergeIntoFormerRedistrictingGroups=True,
                                                 fastCalculations=False,
                                                 showDetailedProgress=False,
                                                 useDistanceScoring=True)
        self.assertEqual(len(splits), 2)
