from unittest import TestCase

from geographyHelper import topAngleFromCenterOfRectangle


class TestTopAngleFromCenterOfRectangle(TestCase):

    def test_topAngleFromCenterOfRectangle_square(self):
        diagonal = topAngleFromCenterOfRectangle(width=10, height=10)
        self.assertEqual(diagonal, 45)

    def test_topAngleFromCenterOfRectangle_twiceAsWide(self):
        diagonal = topAngleFromCenterOfRectangle(width=20, height=10)
        self.assertTrue(diagonal > 45)

    def test_topAngleFromCenterOfRectangle_twiceAsTall(self):
        diagonal = topAngleFromCenterOfRectangle(width=10, height=20)
        self.assertTrue(diagonal < 45)
