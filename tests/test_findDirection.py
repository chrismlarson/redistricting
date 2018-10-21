from unittest import TestCase
from geographyHelper import findDirection, CardinalDirection
from shapely.geometry import Point


class TestFindDirection(TestCase):

    # Cardinal direction tests

    def test_findDirection_north(self):
        center = Point(0.0, 0.0)
        north = Point(0.0, 1.0)
        direction = findDirection(center, north)
        self.assertEqual(direction, CardinalDirection.north)


    def test_findDirection_west(self):
        center = Point(0.0, 0.0)
        west = Point(-1.0, 0.0)
        direction = findDirection(center, west)
        self.assertEqual(direction, CardinalDirection.west)


    def test_findDirection_east(self):
        center = Point(0.0, 0.0)
        east = Point(1.0, 0.0)
        direction = findDirection(center, east)
        self.assertEqual(direction, CardinalDirection.east)


    def test_findDirection_south(self):
        center = Point(0.0, 0.0)
        south = Point(0.0, -1.0)
        direction = findDirection(center, south)
        self.assertEqual(direction, CardinalDirection.south)



    # Primary InterCardinal direction tests

    def test_findDirection_northwest(self):
        center = Point(0.0, 0.0)
        northwest = Point(-1.0, 1.0)
        direction = findDirection(center, northwest)
        self.assertEqual(direction, CardinalDirection.west)


    def test_findDirection_northeast(self):
        center = Point(0.0, 0.0)
        northeast = Point(1.0, 1.0)
        direction = findDirection(center, northeast)
        self.assertEqual(direction, CardinalDirection.north)


    def test_findDirection_southeast(self):
        center = Point(0.0, 0.0)
        southeast = Point(1.0, -1.0)
        direction = findDirection(center, southeast)
        self.assertEqual(direction, CardinalDirection.east)


    def test_findDirection_southwest(self):
        center = Point(0.0, 0.0)
        southwest = Point(-1.0, -1.0)
        direction = findDirection(center, southwest)
        self.assertEqual(direction, CardinalDirection.south)



    # Various close to Cardinal direction tests

    def test_findDirection_northnorthwest(self):
        center = Point(0.0, 0.0)
        northnorthwest = Point(-1.0, 10.0)
        direction = findDirection(center, northnorthwest)
        self.assertEqual(direction, CardinalDirection.north)

    def test_findDirection_eastnortheast(self):
        center = Point(0.0, 0.0)
        eastnortheast = Point(10.0, 1.0)
        direction = findDirection(center, eastnortheast)
        self.assertEqual(direction, CardinalDirection.east)

    def test_findDirection_southsoutheast(self):
        center = Point(0.0, 0.0)
        southsoutheast = Point(1.0, -10.0)
        direction = findDirection(center, southsoutheast)
        self.assertEqual(direction, CardinalDirection.south)

    def test_findDirection_westsouthwest(self):
        center = Point(0.0, 0.0)
        westsouthwest = Point(-10.0, -1.0)
        direction = findDirection(center, westsouthwest)
        self.assertEqual(direction, CardinalDirection.west)



    # Various close to Cardinal direction tests

    def test_findDirection_moved_center(self):
        center = Point(0.0, 0.0)
        westsouthwest = Point(-10.0, -1.0)
        direction = findDirection(westsouthwest, center)
        self.assertEqual(direction, CardinalDirection.east)

    def test_findDirection_samePoint(self):
        center = Point(0.0, 0.0)
        dupe = Point(0.0, 0.0)
        direction = findDirection(center, dupe)
        self.assertEqual(direction, CardinalDirection.north)