from unittest import TestCase
from censusData.censusBlock import CensusBlock
from formatData.redistrictingGroup import RedistrictingGroup, convertAllCensusBlocksToAtomicBlocks, \
    assignNeghboringBlocksToBlocksInAllRedistrictingGroups, \
    attachOrphanBlocksToClosestNeighborFromAllRedistrictingGroups


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
        assignNeghboringBlocksToBlocksInAllRedistrictingGroups()

        attachOrphanBlocksToClosestNeighborFromAllRedistrictingGroups()

        self.assertTrue(testRedistGroup.blocks[0].isNeighbor(testRedistGroup.blocks[1]))
        self.assertTrue(testRedistGroup.blocks[1].isNeighbor(testRedistGroup.blocks[0]))
