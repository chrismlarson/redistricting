import os
from unittest import TestCase
from geographyHelper import isPolygonAGoodDistrictShape
from exportData.exportData import loadDataFromFile


class TestIsPolygonAGoodDistrictShape(TestCase):

    def test_isPolygonAGoodDistrictShape_HourglassThumbShape(self):
        candidatesShapeFilePath = os.path.join(os.path.dirname(__file__),
                                           'testData/HourglassThumbDistrictSplit-ReferenceDistrictCandidateShapes.redistdata')
        candidateShapes = loadDataFromFile(filePath=candidatesShapeFilePath)
        upperCandidate = candidateShapes[0]
        lowerCandidate = candidateShapes[1]

        parentShapeFilePath = os.path.join(os.path.dirname(__file__),
                                           'testData/HourglassThumbDistrictSplit-ReferenceParentShape.redistdata')
        parentShape = loadDataFromFile(filePath=parentShapeFilePath)

        self.assertTrue(isPolygonAGoodDistrictShape(districtPolygon=upperCandidate, parentPolygon=parentShape))
        self.assertFalse(isPolygonAGoodDistrictShape(districtPolygon=lowerCandidate, parentPolygon=parentShape))

    def test_isPolygonAGoodDistrictShape_TopOfMichiganLowerPeninsula(self):
        candidatesShapeFilePath = os.path.join(os.path.dirname(__file__),
                                           'testData/UPDistrictSplit-ReferenceDistrictCandidatePolygons.redistdata')
        candidateShapes = loadDataFromFile(filePath=candidatesShapeFilePath)
        upperCandidate = candidateShapes[0]
        lowerCandidate = candidateShapes[1]

        parentShapeFilePath = os.path.join(os.path.dirname(__file__),
                                           'testData/UPDistrictSplit-ReferenceParentShape.redistdata')
        parentShape = loadDataFromFile(filePath=parentShapeFilePath)

        self.assertTrue(isPolygonAGoodDistrictShape(districtPolygon=upperCandidate, parentPolygon=parentShape))
        self.assertTrue(isPolygonAGoodDistrictShape(districtPolygon=lowerCandidate, parentPolygon=parentShape))
