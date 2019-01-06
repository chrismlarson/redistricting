from geographyHelper import isPolygonAnHourglass
from shapely.geometry import Polygon, Point
from shapely.affinity import rotate
from unittest import TestCase


class TestIsPolygonAnHourglass(TestCase):

    def test_isPolygonAnHourglass_WithHourglass(self):
        hourglassShape = Polygon([(0, 0.2), (0, 1.8), (1, 1.1), (2, 1.8), (2, 0.2), (1, 0.9), (0, 0.2)])
        isHourglass = isPolygonAnHourglass(hourglassShape)
        self.assertTrue(isHourglass)

    def test_isPolygonAnHourglass_WithSquare(self):
        hourglassShape = Polygon([(-1, 1), (1, 1), (1, -1), (-1,-1)])
        isHourglass = isPolygonAnHourglass(hourglassShape)
        self.assertFalse(isHourglass)

    def test_isPolygonAnHourglass_WithNarrowRectangle(self):
        hourglassShape = Polygon([(-10, 1), (10, 1), (10, -1), (-10,-1)])
        isHourglass = isPolygonAnHourglass(hourglassShape)
        self.assertFalse(isHourglass)