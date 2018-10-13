from unittest import TestCase
from censusData.censusBlock import CensusBlock
from geographyHelper import intersectingGeometries


class TestIntersectingGeometries(TestCase):

    def test_intersectingGeometries_BinA(self):
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
        areIntersecting = intersectingGeometries(a, b)
        self.assertTrue(areIntersecting)

    def test_intersectingGeometries_BinAwithHole(self):
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
        areIntersecting = intersectingGeometries(a, b)
        self.assertTrue(areIntersecting)

    def test_intersectingGeometries_BnotInA(self):
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
        areIntersecting = intersectingGeometries(a, b)
        self.assertFalse(areIntersecting)

    def test_intersectingGeometries_BnotInAwithHole(self):
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
                                         'coordinates': [[[100, 100], [101, 100], [101, 99], [100, 99]]]})
        areIntersecting = intersectingGeometries(a, b)
        self.assertFalse(areIntersecting)