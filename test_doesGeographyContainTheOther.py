from unittest import TestCase
from censusData.censusBlock import CensusBlock
from geographyHelper import doesGeographyContainTheOther


class TestDoesGeographyContainTheOther(TestCase):

    def test_containsTheOther_BinA(self):
        a = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={'type': 'Polygon',
                                         'coordinates': [[[-10, 10], [10, 10], [10, -10], [-10, -10]]]})
        b = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={'type': 'Polygon',
                                         'coordinates': [[[-1, 1], [1, 1], [1, -1], [-1, -1]]]})
        isContained = doesGeographyContainTheOther(container=a, target=b)
        self.assertTrue(isContained)

    def test_containsTheOther_BinAwithHole(self):
        exterior = [[-10, 10], [10, 10], [10, -10], [-10, -10]]
        hole = [[-1, 1], [1, 1], [1, -1], [-1, -1]]

        a = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={'type': 'Polygon',
                                         'coordinates': [exterior, hole]})
        b = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={'type': 'Polygon',
                                         'coordinates': [hole]})
        isContained = doesGeographyContainTheOther(container=a, target=b)
        self.assertTrue(isContained)

    def test_containsTheOther_BnotInA(self):
        a = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={'type': 'Polygon',
                                         'coordinates': [[[5, 5], [6, 5], [6, 4], [5, 4]]]})
        b = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={'type': 'Polygon',
                                         'coordinates': [[[-1, 1], [1, 1], [1, -1], [-1, -1]]]})
        isContained = doesGeographyContainTheOther(container=a, target=b)
        self.assertFalse(isContained)
