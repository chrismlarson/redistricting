from unittest import TestCase
from censusData.censusBlock import CensusBlock
from formatData.redistrictingGroup import RedistrictingGroup, convertAllCensusBlocksToAtomicBlocks, \
    assignNeighboringBlocksToBlocksForAllRedistrictingGroups, \
    attachOrphanBlocksToClosestNeighborForAllRedistrictingGroups


class TestAttachOrphanBlocksToClosestNeighbor(TestCase):
    def test_attachOrphanBlocksToClosestNeighbor_Orphans(self):
        a = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={'type': 'Polygon',
                                         'coordinates': [[[-1, 0], [-1, 1], [1, 1], [1, 0]]]})
        b = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={'type': 'Polygon',
                                         'coordinates': [[[4, 4], [4, 5], [5, 5], [5, 4]]]})

        testRedistGroup = RedistrictingGroup(childrenBlocks=[a,b])
        convertAllCensusBlocksToAtomicBlocks()
        assignNeighboringBlocksToBlocksForAllRedistrictingGroups()

        attachOrphanBlocksToClosestNeighborForAllRedistrictingGroups()

        self.assertTrue(testRedistGroup.children[0].isNeighbor(testRedistGroup.children[1]))
        self.assertTrue(testRedistGroup.children[1].isNeighbor(testRedistGroup.children[0]))
