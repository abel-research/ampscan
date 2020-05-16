"""
Testing suite for trim module
"""
import unittest
from util import get_path
import numpy as np


class TestTrim(unittest.TestCase):

    def setUp(self):
        """Runs before each unit test
        Sets up the AmpObject object using "stl_file.stl"
        """
        from ampscan.core import AmpObject
        stl_path = get_path("stl_file.stl")
        self.amp = AmpObject(stl_path)

    def test_trim(self):
        """Tests the trim method of AmpObject for TypeErrors"""

        # Testing that the method runs
        self.amp.planarTrim(0.6, plane=2)

        # Testing invalid data types raise TypeErrors
        with self.assertRaises(TypeError):
            self.amp.planarTrim(0.6, plane=[])
        with self.assertRaises(TypeError):
            self.amp.planarTrim(0.6, plane=0.9)
        with self.assertRaises(TypeError):
            self.amp.planarTrim([], plane=[])

    def test_trim_2(self):
        """Tests the trim method of AmpObject by checking no vertices are above trim line"""
        # Test no points are above 10
        h = 10
        self.amp.planarTrim(h, plane=2)
        self.assertLessEqual(self.amp.vert[:, 2].max(), h)

        # Test no points are above 0
        h = 0
        self.amp.planarTrim(h, plane=2)
        self.assertLessEqual(self.amp.vert[:, 2].max(), h)

    def test_trim_3(self):
        """Tests the trim method of AmpObject by checking no vertices are above trim line"""
        # Test no points are above 10
        p0 = np.array([50, 50, 0])
        p1 = np.array([50, -50, -40])
        p2 = np.array([-50, 50, 10])
        v0 = p1 - p0
        v1 = p2 - p0
        c = np.cross(v0, v1)
        c = c/np.linalg.norm(c)
        k = -np.multiply(c, p0).sum()
        # planar values for each vert on face 
        height = -(self.vert[:, 0]*c[0] + self.vert[:, 1]*c[0] + k)/c[2]
        self.amp.threePointTrim(p0, p1, p2)
        self.assertLessEqual(self.amp.vert[:, 2], height)
