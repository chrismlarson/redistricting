from unittest import TestCase
from censusData.censusBlock import CensusBlock
from formatData.atomicBlock import AtomicBlock
from formatData.redistrictingGroup import RedistrictingGroup
from redistrict.district import createDistrictFromRedistrictingGroups, WeightingMethod, BreakingMethod


class TestDistrict(TestCase):
    def test_splitDistrict_singleRedistrictingGroup(self):
        blockOne = AtomicBlock(childrenBlocks=[CensusBlock(countyFIPS='01',
                                                           tractFIPS='01',
                                                           blockFIPS='01',
                                                           population=10,
                                                           isWater=False,
                                                           geoJSONGeometry={'type': 'Polygon', 'coordinates':
                                                               [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]})])
        blockTwo = AtomicBlock(childrenBlocks=[CensusBlock(countyFIPS='01',
                                                           tractFIPS='01',
                                                           blockFIPS='02',
                                                           population=10,
                                                           isWater=False,
                                                           geoJSONGeometry={'type': 'Polygon', 'coordinates':
                                                               [[[0, 0], [0, -1], [1, -1], [1, 0], [0, 0]]]})])
        singleRedistrictingGroup = RedistrictingGroup(childrenBlocks=[blockOne, blockTwo])
        singleRedistrictingGroup.assignNeighboringBlocksToBlocks()
        testDistrictCandidate = createDistrictFromRedistrictingGroups([singleRedistrictingGroup])
        splits = testDistrictCandidate.splitDistrict(numberOfDistricts=2,
                                                     populationDeviation=1,
                                                     weightingMethod=WeightingMethod.distance,
                                                     breakingMethod=BreakingMethod.splitGroupsOnEdge,
                                                     shouldMergeIntoFormerRedistrictingGroups=True,
                                                     fastCalculations=False,
                                                     showDetailedProgress=False)
        self.assertEqual(len(splits), 2)
