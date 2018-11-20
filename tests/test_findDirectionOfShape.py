from unittest import TestCase
from geographyHelper import findDirectionOfShape, CardinalDirection
from shapely.geometry import Polygon


class TestFindDirectionOfShape(TestCase):

    # Cardinal direction tests

    def test_findDirectionOfShape_north(self):
        centerShape = Polygon([(-1, 1), (1, 1), (1, -1), (-1, -1)])
        northShape = Polygon([(-1, 10), (1, 10), (1, 8), (-1, 8)])
        direction = findDirectionOfShape(centerShape, northShape)
        self.assertEqual(direction, CardinalDirection.north)


    def test_findDirectionOfShape_west(self):
        centerShape = Polygon([(-1, 1), (1, 1), (1, -1), (-1, -1)])
        westShape = Polygon([(-10, 1), (8, 1), (8, -1), (-10, -1)])
        direction = findDirectionOfShape(centerShape, westShape)
        self.assertEqual(direction, CardinalDirection.west)


    def test_findDirectionOfShape_east(self):
        centerShape = Polygon([(-1, 1), (1, 1), (1, -1), (-1, -1)])
        eastShape = Polygon([(8, 1), (10, 1), (10, -1), (8, -1)])
        direction = findDirectionOfShape(centerShape, eastShape)
        self.assertEqual(direction, CardinalDirection.east)


    def test_findDirectionOfShape_south(self):
        centerShape = Polygon([(-1, 1), (1, 1), (1, -1), (-1, -1)])
        southShape = Polygon([(-1, -8), (1, -8), (1, -10), (-1, -10)])
        direction = findDirectionOfShape(centerShape, southShape)
        self.assertEqual(direction, CardinalDirection.south)


    # Overlapping tests

    def test_findDirectionOfShape_closeNorthOverlap(self):
        centerShape = Polygon([(-1, 1), (1, 1), (1, -1), (-1, -1)])
        northOverlapShape = Polygon([(-1, 2), (1, 2), (1, 0), (-1, 0)])
        direction = findDirectionOfShape(centerShape, northOverlapShape)
        self.assertEqual(direction, CardinalDirection.north)


    def test_findDirectionOfShape_sameShape(self):
        centerShape = Polygon([(-1, 1), (1, 1), (1, -1), (-1, -1)])
        dupeShape = Polygon([(-1, 1), (1, 1), (1, -1), (-1, -1)])
        direction = findDirectionOfShape(centerShape, dupeShape)
        self.assertEqual(direction, CardinalDirection.north)



    # Oblong Parent Tests
    def test_findDirectionOfShape_northernNarrow(self):
        baseShape = Polygon([(-1, 5), (1, 5), (1, -5), (-1, -5)])
        northShape = Polygon([(-1, 10), (1, 10), (1, 8), (-1, 8)])
        direction = findDirectionOfShape(baseShape, northShape)
        self.assertEqual(direction, CardinalDirection.north)

        northEasternShape = Polygon([(2, 10), (3, 10), (3, 8), (2, 8)])
        direction = findDirectionOfShape(baseShape, northEasternShape)
        self.assertEqual(direction, CardinalDirection.east)

