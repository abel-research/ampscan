"""
Testing suite for the align module
"""

import unittest
from util import get_path
from ampscan import align


class TestAlign(unittest.TestCase):
    DELTA = 0.01

    def setUp(self):
        """Runs before each unit test.
        Sets up AmpObject object using "stl_file_4.stl" "stl_file_5.stl".
        """
        from ampscan.core import AmpObject
        # Load 2 spheres with radius 1, and 1.2
        stl_path = get_path("stl_file_5.stl") # R=1
        self.amp1 = AmpObject(stl_path)
        stl_path = get_path("stl_file_4.stl") # R=1.2
        self.amp2 = AmpObject(stl_path)
        stl_path = get_path("stl_file.stl")
        self.amp3 = AmpObject(stl_path)
        self.amp4 = AmpObject(stl_path)

    def test_align(self):
        """Test that objects that are already centered on origin are aligned correctly"""
        al = align(self.amp1, self.amp2).m

        # Both objects are already centered, so should be close to origin (allowing for some inaccuracy)
        self.assertAlmostEqual(al.vert.mean(axis=0)[0], 0, delta=TestAlign.DELTA)
        self.assertAlmostEqual(al.vert.mean(axis=0)[1], 0, delta=TestAlign.DELTA)
        self.assertAlmostEqual(al.vert.mean(axis=0)[2], 0, delta=TestAlign.DELTA)


    def test_align_points(self):
        """Test that the shape can be aligned to -5mm in z axis"""
        mv = [
            [0, 0, 5],
            [5, 0, 5],
            [0, 5, 5]
        ]
        sv = [
            [0, 0, 0],
            [5, 0, 0],
            [0, 5, 0]
        ]
        al = align(self.amp1, self.amp2, mv=mv, sv=sv, method='contPoints').m
        zMax = self.amp1.vert[:, 2].max() - 5
        # Both objects are already centered, so should be close to origin (allowing for some inaccuracy)
        self.assertAlmostEqual(al.vert[:, 2].max(), zMax, delta=TestAlign.DELTA)

    def test_align_idx(self):
        """Test that the shape can be using idxPoints"""
        self.amp4.rotateAng([5, 5, 5], ang='deg')
        al = align(self.amp3, self.amp4, mv=[0, 1, 2, 3], sv=[0, 1, 2, 3], method='idxPoints')
        all(self.assertAlmostEqual(al.m.vert[i, 0], al.s.vert[i, 0], delta=0.1) for i in range(al.s.vert.shape[0]))
