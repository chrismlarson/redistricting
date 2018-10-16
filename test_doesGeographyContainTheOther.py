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
        aContainsB = doesGeographyContainTheOther(container=a, target=b)
        self.assertTrue(aContainsB)
        bContainsA = doesGeographyContainTheOther(container=b, target=a)
        self.assertFalse(bContainsA)

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
        aContainsB = doesGeographyContainTheOther(container=a, target=b)
        self.assertTrue(aContainsB)
        bContainsA = doesGeographyContainTheOther(container=b, target=a)
        self.assertFalse(bContainsA)

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
        aContainsB = doesGeographyContainTheOther(container=a, target=b)
        self.assertFalse(aContainsB)
        bContainsA = doesGeographyContainTheOther(container=b, target=a)
        self.assertFalse(bContainsA)

    def test_containsTheOther_BnotInAwithHole(self):
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
        aContainsB = doesGeographyContainTheOther(container=a, target=b)
        self.assertFalse(aContainsB)
        bContainsA = doesGeographyContainTheOther(container=b, target=a)
        self.assertFalse(bContainsA)

    def test_containsTheOther_BinAMultiPolygon(self):
        a = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={
                            "type": "MultiPolygon",
                            "coordinates": [
                                [[
                                    [-82.60879799999999, 43.743775],
                                    [-82.60899999999999, 43.743736],
                                    [-82.609098, 43.74378],
                                    [-82.60789800000001, 43.744233],
                                    [-82.607466, 43.744281],
                                    [-82.607097, 43.744456],
                                    [-82.606692, 43.744626],
                                    [-82.606404, 43.74435],
                                    [-82.606708, 43.744312],
                                    [-82.607049, 43.744302],
                                    [-82.607451, 43.744177],
                                    [-82.607694, 43.74415],
                                    [-82.608666, 43.743801],
                                    [-82.60879799999999, 43.743775]
                                ]],
                                [[
                                    [-82.606212, 43.734192],
                                    [-82.606246, 43.734014],
                                    [-82.606542, 43.733894],
                                    [-82.60693000000001, 43.733642],
                                    [-82.607241, 43.733473],
                                    [-82.60751399999999, 43.733501],
                                    [-82.606617, 43.734042],
                                    [-82.606464, 43.734251],
                                    [-82.606207, 43.734217],
                                    [-82.606212, 43.734192]
                                ]],
                                [[
                                    [-82.608132, 43.746174],
                                    [-82.608152, 43.746201],
                                    [-82.60801499999999, 43.746305],
                                    [-82.60791500000001, 43.746425],
                                    [-82.607719, 43.746397],
                                    [-82.607742, 43.746309],
                                    [-82.60781, 43.746315],
                                    [-82.607871, 43.746227],
                                    [-82.608108, 43.746142],
                                    [-82.608132, 43.746174]
                                ]]
                            ]
                        })
        b = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-82.59254199999999, 43.777148],
                                    [-82.599344, 43.777084],
                                    [-82.599521, 43.777149],
                                    [-82.609269, 43.789296],
                                    [-82.608028, 43.79799],
                                    [-82.621675, 43.826759],
                                    [-82.62451, 43.836733],
                                    [-82.62539700000001, 43.847984],
                                    [-82.639571, 43.862742],
                                    [-82.63938400000001, 43.862746],
                                    [-82.593673, 43.863701],
                                    [-82.59366799999999, 43.863332],
                                    [-82.593637, 43.860939],
                                    [-82.59254199999999, 43.777148]
                                ]
                            ]
                        })
        aContainsB = doesGeographyContainTheOther(container=a, target=b)
        self.assertFalse(aContainsB)
        bContainsA = doesGeographyContainTheOther(container=b, target=a)
        self.assertFalse(bContainsA)


    def test_containsTheOther_BMultiploygoninAWithHoles(self):
        exterior = [[-10, 10], [10, 10], [10, -10], [-10, -10]]
        shape1 = [[-1, 1], [1, 1], [1, -1], [-1, -1]]
        shape2 = [[-5, 5], [-4, 5], [-4, 4], [-5, 4]]

        a = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={'type': 'Polygon',
                                         'coordinates': [exterior, shape1, shape2]})
        b = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={
                            "type": "MultiPolygon",
                            "coordinates": [
                                [shape1],
                                [shape2]
                            ]
                        })
        aContainsB = doesGeographyContainTheOther(container=a, target=b)
        self.assertTrue(aContainsB)
        bContainsA = doesGeographyContainTheOther(container=b, target=a)
        self.assertFalse(bContainsA)