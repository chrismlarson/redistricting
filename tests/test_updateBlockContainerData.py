from unittest import TestCase
from shapely.geometry import Polygon, Point
from censusData.censusBlock import CensusBlock
from formatData.censusBlockContainer import CensusBlockContainer


class TestCensusBlockContainer(TestCase):

    def test_updateBlockContainerData_touchingSquares(self):
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
                                         'coordinates': [[[-1, 1], [-1, 2], [1, 2], [1, 1]]]})

        blocks = [a,b]
        blockContainer = CensusBlockContainer()
        blockContainer.blocks = blocks

        self.assertEqual(blockContainer.population, 2)

        combinedPolygon = Polygon([(-1, 0), (-1, 2), (1, 2), (1, 0)])
        self.assertEqual(blockContainer.geometry, combinedPolygon)


    def test_updateBlockContainerData_squareWithinAnother(self):
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
        blocks = [a, b]
        blockContainer = CensusBlockContainer()
        blockContainer.blocks = blocks

        self.assertEqual(blockContainer.population, 2)
        self.assertEqual(blockContainer.geometry, Polygon(exterior))


    def test_updateBlockContainerData_singleCircle(self):
        a = CensusBlock(countyFIPS='01',
                        tractFIPS='01',
                        blockFIPS='01',
                        population=int('1'),
                        isWater=False,
                        geoJSONGeometry={'type': 'Polygon',
                                         'coordinates': [[[0,0], [-1, 1], [1, 1], [1, 0]]]})

        circle = Point(0,0).buffer(1) #replace the geometry
        a.geometry = circle

        blocks = [a]
        blockContainer = CensusBlockContainer()
        blockContainer.blocks = blocks

        self.assertEqual(blockContainer.population, 1)
        self.assertEqual(blockContainer.geometry, circle)
