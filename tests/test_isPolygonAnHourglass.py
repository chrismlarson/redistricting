from exportData.exportData import loadDataFromFile
from geographyHelper import isPolygonAnHourglass
from shapely.geometry import Polygon
import os
from unittest import TestCase


class TestIsPolygonAnHourglass(TestCase):

    def test_isPolygonAnHourglass_WithHourglass(self):
        hourglassShape = Polygon([(0, 0.2), (0, 1.8), (1, 1.025), (2, 1.8), (2, 0.2), (1, 0.975), (0, 0.2)])
        isHourglass = isPolygonAnHourglass(hourglassShape)
        self.assertTrue(isHourglass)

    def test_isPolygonAnHourglass_WithSquare(self):
        hourglassShape = Polygon([(-1, 1), (1, 1), (1, -1), (-1, -1)])
        isHourglass = isPolygonAnHourglass(hourglassShape)
        self.assertFalse(isHourglass)

    def test_isPolygonAnHourglass_WithNarrowRectangle(self):
        hourglassShape = Polygon([(-10, 1), (10, 1), (10, -1), (-10, -1)])
        isHourglass = isPolygonAnHourglass(hourglassShape)
        self.assertFalse(isHourglass)

    def test_isPolygonAnHourglass_HourglassThumbShape(self):
        candidateDistrictShapeFilePath = os.path.join(os.path.dirname(__file__),
                                           'testData/HourglassThumbDistrictSplit-ReferenceDistrictCandidateShapes.redistdata')
        candidateDistrictShapes = loadDataFromFile(filePath=candidateDistrictShapeFilePath)
        self.assertFalse(isPolygonAnHourglass(candidateDistrictShapes[0]))
        self.assertTrue(isPolygonAnHourglass(candidateDistrictShapes[1]))

    def test_isPolygonAnHourglass_TopOfMichiganLowerPeninsula(self):
        candidatesShapeFilePath = os.path.join(os.path.dirname(__file__),
                                           'testData/UPDistrictSplit-ReferenceDistrictCandidatePolygons.redistdata')
        candidateShapes = loadDataFromFile(filePath=candidatesShapeFilePath)
        candidateWithUP = candidateShapes[0]
        polygonsInCandidateWithUP = list(candidateWithUP)
        lowerPortionOfCandidate = polygonsInCandidateWithUP[3]
        self.assertFalse(isPolygonAnHourglass(lowerPortionOfCandidate))
