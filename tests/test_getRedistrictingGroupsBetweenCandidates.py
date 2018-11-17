import os
from exportData.exportData import loadDataFromFile
from redistrict.district import getRedistrictingGroupsBetweenCandidates
from unittest import TestCase


class TestGetRedistrictingGroupsBetweenCandidates(TestCase):
    @classmethod
    def setUpClass(cls):
        testDataFilePath = os.path\
            .join(os.path.dirname(__file__),
                  'testData/2010-Michigan-CandidateRedistrictingGroupInfoNoAtomicBlocks.redistdata')
        cls._stateData = loadDataFromFile(filePath=testDataFilePath)



    def test_getRedistrictingGroupsBetweenCandidates(self):
        candidateDistrictA = self._stateData[0]
        candidateDistrictB = self._stateData[1]

        betweenCandidates = getRedistrictingGroupsBetweenCandidates(aCandidate=candidateDistrictA,
                                                                    bCandidate=candidateDistrictB)

        self.assertEqual(len(betweenCandidates), 20)